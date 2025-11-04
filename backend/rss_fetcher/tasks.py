"""
Celery tasks for RSS feed fetching.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
from cms.models import Article
from .models import RSSFeed
import feedparser
import logging
from slugify import slugify
import json
import time
import requests

logger = logging.getLogger(__name__)

# Google Trends (optional - will fail gracefully if not available)
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logger.warning("pytrends not available. Google Trends integration disabled.")


@shared_task
def fetch_rss_feeds(force=False):
    """
    Fetch articles from all active RSS feeds and create draft articles.
    This task is scheduled to run periodically via Celery Beat.
    Only fetches feeds that haven't been fetched recently based on their fetch_interval.
    
    Args:
        force: If True, fetch all feeds regardless of last_fetched_at timestamp
    """
    logger.info("Starting automatic RSS feed fetch")
    
    # Get RSS feeds from database
    feeds = RSSFeed.objects.filter(is_active=True)
    
    if not feeds.exists():
        # Fallback to settings if no feeds in database
        feed_urls = getattr(settings, 'RSS_FEEDS', [])
        if not feed_urls:
            logger.warning("No RSS feeds configured")
            return {'success': False, 'message': 'No RSS feeds configured'}
    
    articles_created = 0
    feeds_processed = 0
    feeds_skipped = 0
    errors = []
    now = timezone.now()
    
    # Process feeds from database
    for feed in feeds:
        try:
            # Check if feed needs to be fetched based on its interval
            should_fetch = True
            if not force and feed.last_fetched_at:
                minutes_since_last_fetch = (now - feed.last_fetched_at).total_seconds() / 60
                if minutes_since_last_fetch < feed.fetch_interval:
                    should_fetch = False
                    feeds_skipped += 1
                    logger.debug(f"Feed '{feed.name}' skipped (last fetched {int(minutes_since_last_fetch)} min ago, interval: {feed.fetch_interval} min)")
            
            if should_fetch:
                logger.info(f"Fetching feed: {feed.name} ({feed.url})")
                result = fetch_single_rss_feed(feed.url)
                articles_created += result.get('articles_created', 0)
                
                # Update last fetched timestamp
                feed.last_fetched_at = now
                feed.save()
                feeds_processed += 1
                logger.info(f"Feed '{feed.name}': Created {result.get('articles_created', 0)} new articles")
            
        except Exception as e:
            error_msg = f"Error fetching feed '{feed.name}' ({feed.url}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
    
    # If no feeds in database, use settings fallback
    if not feeds.exists():
        feed_urls = getattr(settings, 'RSS_FEEDS', [])
        logger.info(f"Using RSS_FEEDS from settings ({len(feed_urls)} feeds)")
        for feed_url in feed_urls:
            try:
                logger.info(f"Fetching feed from settings: {feed_url}")
                result = fetch_single_rss_feed(feed_url)
                articles_created += result.get('articles_created', 0)
                feeds_processed += 1
            except Exception as e:
                error_msg = f"Error fetching feed {feed_url}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
    
    logger.info(f"RSS feed fetch completed. Processed {feeds_processed} feeds, skipped {feeds_skipped}, created {articles_created} new articles.")
    
    return {
        'success': True,
        'articles_created': articles_created,
        'feeds_processed': feeds_processed,
        'feeds_skipped': feeds_skipped,
        'errors': errors
    }


def fetch_single_rss_feed(feed_url, category='reliable_sources', trend_data=None):
    """
    Fetch and process a single RSS feed.
    """
    logger.info(f"Fetching RSS feed: {feed_url}")
    
    # Parse RSS feed
    feed = feedparser.parse(feed_url)
    
    if feed.bozo:
        logger.warning(f"Feed parsing issues for {feed_url}: {feed.bozo_exception}")
    
    articles_created = 0
    
    for entry in feed.entries[:10]:  # Limit to 10 most recent entries
        try:
            # Check if article already exists (by source_url)
            if entry.get('link'):
                existing = Article.objects.filter(source_url=entry.link).first()
                if existing:
                    logger.debug(f"Article already exists: {entry.link}")
                    continue
            
            # Create article
            title = entry.get('title', 'Untitled')
            summary = entry.get('summary', '') or entry.get('description', '')
            
            # Try to extract image from RSS entry
            image_url = None
            # Check for media:content or enclosure (common RSS image formats)
            if 'media_content' in entry and entry.media_content:
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        image_url = media.get('url') or media.get('fileUrl')
                        break
            # Check for enclosure
            if not image_url and 'enclosures' in entry:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('href')
                        break
            # Check for links with image extensions
            if not image_url:
                links = entry.get('links', [])
                for link in links:
                    href = link.get('href', '')
                    if any(href.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        image_url = href
                        break
            
            # Generate unique slug
            slug = slugify(title)
            base_slug = slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            article = Article.objects.create(
                title=title,
                slug=slug,
                summary=summary[:500],  # Limit summary length
                status='fetched',
                source_url=entry.get('link', ''),
                source_feed=feed_url,
                category=category,
                trend_data=trend_data,
            )
            
            # Try to fetch image if URL found in RSS
            if image_url:
                try:
                    from workers.tasks import fetch_and_save_featured_image
                    fetch_and_save_featured_image(article, image_url)
                except Exception as e:
                    logger.debug(f"Could not fetch image from RSS: {str(e)}")
                    # Will be fetched from source URL during generation
            
            articles_created += 1
            logger.debug(f"Created article: {article.title}")
            
        except Exception as e:
            logger.error(f"Error creating article from entry: {str(e)}")
            continue
    
    return {'articles_created': articles_created}


@shared_task
def fetch_single_feed_task(feed_id):
    """
    Fetch a single RSS feed by ID.
    """
    try:
        feed = RSSFeed.objects.get(id=feed_id)
        result = fetch_single_rss_feed(feed.url)
        
        feed.last_fetched_at = timezone.now()
        feed.save()
        
        return result
    except RSSFeed.DoesNotExist:
        logger.error(f"RSS Feed {feed_id} not found")
        return {'success': False, 'error': 'Feed not found'}


@shared_task
def fetch_google_trends_sports():
    """
    Fetch last 1 hour sports articles from NewsAPI for India.
    Falls back to RSS feeds if NewsAPI not configured.
    Articles are automatically enriched with Google Trends data.
    """
    logger.info("Starting Sports Trends fetch")
    
    # Try NewsAPI first for India sports
    if settings.NEWS_API_KEY:
        result = _fetch_newsapi_india_sports()
        if result['success'] and result['articles_created'] > 0:
            return result
        logger.info("NewsAPI returned no articles, falling back to RSS")
    
    # Fallback to RSS feeds
    return _fetch_sports_rss()


def _fetch_newsapi_india_sports():
    """
    Fetch trending sports articles from NewsAPI for India (last 1 hour).
    """
    logger.info("Fetching sports articles from NewsAPI for India")
    
    # Calculate timestamp for 1 hour ago
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    from_time = one_hour_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Build API URL for India sports articles
    # Using 'everything' endpoint with country and sports keywords
    api_url = 'https://newsapi.org/v2/everything'
    
    # Indian sports keywords for better filtering
    sports_keywords = '(cricket OR football OR ipl OR bcci OR kohli OR dhoni OR messi OR ronaldo OR premier league)'
    
    params = {
        'q': sports_keywords,
        'language': 'en',
        'sortBy': 'popularity',  # Most popular/trending articles first
        'from': from_time,
        'pageSize': 50,  # Get up to 50 articles
        'apiKey': settings.NEWS_API_KEY,
    }
    
    articles_created = 0
    errors = []
    
    try:
        logger.info(f"Fetching NewsAPI with params: q={sports_keywords}, from={from_time}")
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code != 200:
            error_msg = f"NewsAPI request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            errors.append(error_msg)
            return {
                'success': False,
                'articles_created': 0,
                'errors': errors
            }
        
        data = response.json()
        
        if data.get('status') != 'ok':
            error_msg = f"NewsAPI returned error: {data.get('message', 'Unknown error')}"
            logger.error(error_msg)
            errors.append(error_msg)
            return {
                'success': False,
                'articles_created': 0,
                'errors': errors
            }
        
        articles = data.get('articles', [])
        logger.info(f"Received {len(articles)} articles from NewsAPI")
        
        # Filter articles and create database entries
        for article_data in articles:
            try:
                url = article_data.get('url')
                if not url:
                    continue
                
                # Check if article already exists
                existing = Article.objects.filter(source_url=url).first()
                if existing:
                    logger.debug(f"Article already exists: {url}")
                    continue
                
                # Parse published date
                published_time = None
                published_str = article_data.get('publishedAt', '')
                if published_str:
                    try:
                        # NewsAPI uses ISO 8601 format: 2024-01-01T12:00:00Z
                        published_time = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    except:
                        logger.debug(f"Could not parse date: {published_str}")
                
                # Determine sport from title/content
                title = article_data.get('title', 'Untitled')
                title_lower = title.lower()
                
                if any(word in title_lower for word in ['cricket', 'ipl', 'bcci', 'kohli', 'dhoni', 'ashes', 'test match']):
                    sport = 'Cricket'
                elif any(word in title_lower for word in ['football', 'soccer', 'premier league', 'messi', 'ronaldo', 'world cup', 'epl']):
                    sport = 'Football'
                else:
                    sport = 'Sports'  # Generic sports
                
                # Build trend data
                trend_data = {
                    'title': title,
                    'link': url,
                    'published': published_str,
                    'published_parsed': published_time.isoformat() if published_time else None,
                    'sport': sport,
                    'feed_name': article_data.get('source', {}).get('name', 'NewsAPI'),
                    'source': article_data.get('source', {}).get('name', 'NewsAPI'),
                    'author': article_data.get('author', ''),
                    'description': article_data.get('description', ''),
                    'content': article_data.get('content', ''),
                    'image_url': article_data.get('urlToImage', ''),
                    'newsapi': True,
                }
                
                summary = article_data.get('description', '') or article_data.get('content', '')[:500]
                
                # Generate unique slug
                slug = slugify(title)
                base_slug = slug
                counter = 1
                while Article.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                article = Article.objects.create(
                    title=title,
                    slug=slug,
                    summary=summary[:500],
                    status='fetched',
                    source_url=url,
                    source_feed='NewsAPI',
                    category='trends',
                    trend_data=trend_data,
                )
                
                articles_created += 1
                logger.debug(f"Created NewsAPI article: {title} ({sport})")
                
            except Exception as e:
                logger.error(f"Error processing NewsAPI article: {str(e)}")
                continue
        
        logger.info(f"NewsAPI fetch completed. Created {articles_created} new articles.")
        
        return {
            'success': True,
            'articles_created': articles_created,
            'errors': errors
        }
        
    except Exception as e:
        error_msg = f"Error in NewsAPI fetch: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            'success': False,
            'articles_created': 0,
            'errors': [error_msg]
        }


def _fetch_sports_rss():
    """
    Fetch sports articles from RSS feeds for Football and Cricket.
    """
    logger.info("Fetching sports RSS feeds")
    
    feeds_to_fetch = [
        {
            'name': 'ESPN Cricket',
            'url': 'https://www.espncricinfo.com/rss/content/story/feeds/0.xml',
            'sport': 'Cricket'
        },
        {
            'name': 'BBC Football',
            'url': 'http://feeds.bbci.co.uk/sport/football/rss.xml',
            'sport': 'Football'
        },
        {
            'name': 'BBC Cricket',
            'url': 'http://feeds.bbci.co.uk/sport/cricket/rss.xml',
            'sport': 'Cricket'
        },
        {
            'name': 'ESPN Football',
            'url': 'http://www.espn.com/espn/rss/soccer/news',
            'sport': 'Football'
        },
    ]
    
    articles_created = 0
    total_errors = []
    
    for feed_info in feeds_to_fetch:
        trends_url = feed_info['url']
        sport_name = feed_info['sport']
        
        try:
            logger.info(f"Fetching {feed_info['name']} feed: {trends_url}")
            feed = feedparser.parse(trends_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues for {feed_info['name']}: {feed.bozo_exception}")
            
            one_hour_ago = timezone.now() - timedelta(hours=1)
            
            for entry in feed.entries[:20]:
                try:
                    if entry.get('link'):
                        existing = Article.objects.filter(source_url=entry.link).first()
                        if existing:
                            logger.debug(f"Trend already exists: {entry.link}")
                            continue
                    
                    published_time = None
                    if entry.get('published_parsed'):
                        try:
                            published_time = datetime(*entry.published_parsed[:6])
                            published_time = timezone.make_aware(published_time)
                        except:
                            pass
                    
                    if published_time and published_time < one_hour_ago:
                        logger.debug(f"Skipping old article: {entry.title}")
                        continue
                    
                    title = entry.get('title', 'Untitled')
                    summary = entry.get('summary', '') or entry.get('description', '')
                    
                    trend_data = {
                        'title': title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'published_parsed': published_time.isoformat() if published_time else None,
                        'sport': sport_name,
                        'feed_name': feed_info['name'],
                        'source': entry.get('source', {}).get('title', feed_info['name']) if entry.get('source') else feed_info['name'],
                        'tags': entry.get('tags', []),
                        'author': entry.get('author', ''),
                    }
                    
                    slug = slugify(title)
                    base_slug = slug
                    counter = 1
                    while Article.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    article = Article.objects.create(
                        title=title,
                        slug=slug,
                        summary=summary[:500],
                        status='fetched',
                        source_url=entry.get('link', ''),
                        source_feed=trends_url,
                        category='trends',
                        trend_data=trend_data,
                    )
                    
                    articles_created += 1
                    logger.debug(f"Created article: {article.title} ({sport_name})")
                    
                except Exception as e:
                    logger.error(f"Error creating article: {str(e)}")
                    continue
            
        except Exception as e:
            error_msg = f"Error fetching {feed_info['name']}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            total_errors.append(error_msg)
    
    logger.info(f"RSS-only fetch completed. Created {articles_created} new articles.")
    
    return {
        'success': True if not total_errors else False,
        'articles_created': articles_created,
        'errors': total_errors
    }


@shared_task
def enhance_articles_with_google_trends():
    """
    Enhance existing trend articles with Google Trends data.
    Fetches actual Google Trends data for sports keywords and updates trend_data.
    """
    if not PYTRENDS_AVAILABLE:
        logger.warning("pytrends not available. Skipping Google Trends enhancement.")
        return {
            'success': False,
            'message': 'pytrends library not installed'
        }
    
    logger.info("Starting Google Trends enhancement")
    
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Get recent trend articles (last hour)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_articles = Article.objects.filter(
            category='trends',
            created_at__gte=one_hour_ago
        )[:20]  # Process up to 20 recent articles
        
        if not recent_articles.exists():
            logger.info("No recent trend articles to enhance")
            return {
                'success': True,
                'articles_enhanced': 0
            }
        
        articles_enhanced = 0
        
        for article in recent_articles:
            try:
                # Extract keywords from title
                title_words = article.title.split()
                # Get first 3 significant words as potential search terms
                keywords = [w for w in title_words if len(w) > 4][:3]
                
                if not keywords:
                    continue
                
                # Add delay to avoid rate limiting (2 seconds between requests)
                time.sleep(2)
                
                # Get Google Trends interest for these keywords
                pytrends.build_payload(keywords, cat=0, timeframe='now 1-H', geo='US')
                trends_data = pytrends.interest_over_time()
                
                if not trends_data.empty:
                    # Calculate average interest
                    avg_interest = trends_data[keywords].sum(axis=1).mean()
                    
                    # Get related queries
                    related_queries = pytrends.related_queries()
                    
                    # Update trend_data with Google Trends info
                    trend_data = article.trend_data or {}
                    trend_data.update({
                        'google_trends': {
                            'avg_interest': float(avg_interest),
                            'timeframe': 'last 1 hour',
                            'keywords_searched': keywords,
                            'related_queries': {
                                kw: {
                                    'top': list(related_queries.get(kw, {}).get('top', {}).head(5)['query'].values) if kw in related_queries and related_queries[kw].get('top') is not None else [],
                                    'rising': list(related_queries.get(kw, {}).get('rising', {}).head(5)['query'].values) if kw in related_queries and related_queries[kw].get('rising') is not None else []
                                } for kw in keywords
                            }
                        }
                    })
                    
                    article.trend_data = trend_data
                    article.save()
                    articles_enhanced += 1
                    logger.debug(f"Enhanced article with Google Trends: {article.title}")
                
            except Exception as e:
                logger.error(f"Error enhancing article {article.id}: {str(e)}")
                continue
        
        logger.info(f"Google Trends enhancement completed. Enhanced {articles_enhanced} articles.")
        
        return {
            'success': True,
            'articles_enhanced': articles_enhanced
        }
        
    except Exception as e:
        error_msg = f"Error in Google Trends enhancement: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            'success': False,
            'error': error_msg
        }

