"""
Celery tasks for RSS feed fetching.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from cms.models import Article
from .models import RSSFeed
import feedparser
import logging
from slugify import slugify

logger = logging.getLogger(__name__)


@shared_task
def fetch_rss_feeds():
    """
    Fetch articles from all active RSS feeds and create draft articles.
    This task is scheduled to run periodically via Celery Beat.
    Only fetches feeds that haven't been fetched recently based on their fetch_interval.
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
            if feed.last_fetched_at:
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


def fetch_single_rss_feed(feed_url):
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

