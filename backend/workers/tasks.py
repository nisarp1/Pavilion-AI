"""
Celery tasks for article generation and processing.
"""
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a dummy decorator if celery is not available
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from django.utils import timezone
from django.conf import settings
from cms.models import Article, Category
from slugify import slugify
import logging
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import re
import os
import html

logger = logging.getLogger(__name__)

# Google Cloud Text-to-Speech
try:
    from google.cloud import texttospeech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("google-cloud-texttospeech not available. Audio generation will be disabled.")

# Configure Gemini AI
GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', '')
GEMINI_MODEL = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info(f"Gemini AI configured with model: {GEMINI_MODEL}")
    except Exception as e:
        logger.error(f"Failed to configure Gemini AI: {str(e)}")
else:
    logger.warning("GEMINI_API_KEY not configured")


def fetch_featured_image_from_url(article_url):
    """
    Fetch featured image from article URL.
    Tries multiple methods to find the image.
    """
    if not article_url:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple methods to find featured image
        image_url = None
        
        # 1. Try Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image.get('content')
        
        # 2. Try Twitter card image
        if not image_url:
            twitter_image = soup.find('meta', {'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                image_url = twitter_image.get('content')
        
        # 3. Try article:image meta tag
        if not image_url:
            article_image = soup.find('meta', {'name': 'article:image'})
            if article_image and article_image.get('content'):
                image_url = article_image.get('content')
        
        # 4. Try first large image in article content
        if not image_url:
            # Look for img tags in article content
            article_content = soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower() or 'post' in x.lower()))
            if article_content:
                images = article_content.find_all('img')
                for img in images:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src:
                        # Check if it's a reasonable size (not an icon)
                        width = img.get('width')
                        height = img.get('height')
                        if width and height:
                            try:
                                if int(width) > 300 and int(height) > 200:
                                    image_url = src
                                    break
                            except:
                                pass
                        else:
                            # If no size specified, use first image
                            if not image_url:
                                image_url = src
        
        # 5. Try first large image on page
        if not image_url:
            all_images = soup.find_all('img')
            for img in all_images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not any(skip in src.lower() for skip in ['logo', 'icon', 'avatar', 'button']):
                    width = img.get('width')
                    height = img.get('height')
                    if width and height:
                        try:
                            if int(width) > 400 and int(height) > 300:
                                image_url = src
                                break
                        except:
                            pass
        
        # Make absolute URL if relative
        if image_url:
            image_url = urljoin(article_url, image_url)
            return image_url
        
        return None
        
    except Exception as e:
        logger.debug(f"Error fetching image from URL {article_url}: {str(e)}")
        return None


def auto_assign_categories(article):
    """
    Automatically assign categories to an article based on its content.
    Uses keyword matching against category names and descriptions.
    Also considers subcategories for more precise matching.
    """
    try:
        # Get all active categories (including subcategories)
        all_categories = Category.objects.filter(is_active=True).select_related('parent').prefetch_related('children')
        
        if not all_categories.exists():
            logger.debug("No categories available for auto-assignment")
            return
        
        # Prepare article text for matching (title + summary + body)
        article_text = ''
        if article.title:
            article_text += article.title.lower() + ' '
        if article.summary:
            article_text += article.summary.lower() + ' '
        if article.summary_english:
            article_text += article.summary_english.lower() + ' '
        if article.body:
            # Remove HTML tags for better matching
            body_text = re.sub(r'<[^>]+>', ' ', article.body)
            article_text += body_text.lower() + ' '
        
        # Also check source URL for hints
        if article.source_url:
            url_lower = article.source_url.lower()
            article_text += url_lower + ' '
        
        matched_categories = []
        
        # Define keyword mappings for common sports terms
        keyword_mappings = {
            'cricket': ['cricket', 'cricketer', 'ipl', 'odi', 'test', 't20', 'wicket', 'run', 'batting', 'bowling', 'team india', 'bcci'],
            'football': ['football', 'soccer', 'fifa', 'premier league', 'epl', 'la liga', 'serie a', 'champions league', 'world cup', 'goal', 'match', 'player'],
            'ipl': ['ipl', 'indian premier league', 'csk', 'mi', 'rcb', 'kkr', 'dc', 'rr', 'srh', 'lsg', 'gt', 'pbks'],
            'epl': ['epl', 'premier league', 'manchester', 'liverpool', 'chelsea', 'arsenal', 'tottenham'],
            'laliga': ['la liga', 'barcelona', 'real madrid', 'atletico', 'sevilla', 'valencia'],
            'seriea': ['serie a', 'juventus', 'milan', 'inter', 'napoli', 'roma'],
            'isl': ['isl', 'indian super league', 'mumbai city', 'atk', 'kerala blasters', 'bengaluru'],
        }
        
        # Match against category names and descriptions
        for category in all_categories:
            score = 0
            category_name_lower = category.name.lower()
            
            # Direct category name match (high weight)
            if category_name_lower in article_text:
                # Count occurrences and weight heavily
                count = article_text.count(category_name_lower)
                score += count * 50  # High weight for exact category name
            
            # Check keyword mappings
            for key, keywords in keyword_mappings.items():
                if key in category_name_lower:
                    for keyword in keywords:
                        if keyword in article_text:
                            count = article_text.count(keyword)
                            score += count * 20  # Medium-high weight for mapped keywords
            
            # Check description words
            if category.description:
                desc_words = re.findall(r'\b\w+\b', category.description.lower())
                for word in desc_words:
                    if len(word) > 3 and word in article_text:
                        count = article_text.count(word)
                        score += count * 5  # Lower weight for description words
            
            # Check subcategory names (higher weight if subcategory matches)
            if category.children.exists():
                for child in category.children.filter(is_active=True):
                    child_name_lower = child.name.lower()
                    if child_name_lower in article_text:
                        count = article_text.count(child_name_lower)
                        score += count * 30  # Medium-high weight for subcategory names
                        # Also add score to parent
                        parent_score = count * 15
                        score += parent_score
            
            # Check individual words from category name
            category_words = re.findall(r'\b\w+\b', category_name_lower)
            for word in category_words:
                if len(word) > 3 and word in article_text:
                    count = article_text.count(word)
                    score += count * 3  # Lower weight for individual words
            
            # If score is significant, add to matched categories
            if score > 15:  # Threshold for matching
                matched_categories.append((category, score))
        
        # Sort by score and take top matches
        matched_categories.sort(key=lambda x: x[1], reverse=True)
        
        # Assign categories (limit to top 3 to avoid over-categorization)
        categories_to_assign = [cat for cat, score in matched_categories[:3]]
        
        if categories_to_assign:
            # Clear existing categories and assign new ones
            article.categories.clear()
            article.categories.add(*categories_to_assign)
            logger.info(f"Auto-assigned {len(categories_to_assign)} categories to article {article.id} ({article.title[:50]}): {[c.name for c in categories_to_assign]}")
        else:
            logger.debug(f"No categories matched for article {article.id} ({article.title[:50]})")
            
    except Exception as e:
        logger.error(f"Error auto-assigning categories to article {article.id}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())


def fetch_and_save_featured_image(article, image_url=None):
    """
    Download and save featured image for an article.
    """
    if article.featured_image:
        # Image already exists
        return
    
    # Try to get image URL if not provided
    if not image_url:
        image_url = fetch_featured_image_from_url(article.source_url)
    
    if not image_url:
        logger.debug(f"No image found for article {article.id}")
        return
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()
        
        # Get file extension
        parsed_url = urlparse(image_url)
        file_ext = parsed_url.path.split('.')[-1].lower()
        if file_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            file_ext = 'jpg'
        
        # Download image
        img_data = BytesIO(response.content)
        
        # Verify it's actually an image
        try:
            img = Image.open(img_data)
            img.verify()
            
            # Reset BytesIO
            img_data.seek(0)
            img_data.name = f"article_{article.id}_featured.{file_ext}"
            
            # Convert to WebP
            try:
                from cms.utils import process_image_to_webp
                new_name, new_content = process_image_to_webp(img_data)
                
                if new_name and new_content:
                    logger.info(f"Converted fetched image to WebP: {new_name}")
                    article.featured_image.save(new_name, new_content, save=True)
                else:
                    # Fallback to original
                    logger.warning("WebP conversion failed, saving original")
                    img_data.seek(0)
                    article.featured_image.save(
                        img_data.name,
                        ContentFile(img_data.read()),
                        save=True
                    )
            except Exception as e:
                logger.error(f"Error converting to WebP: {e}")
                # Fallback to original
                img_data.seek(0)
                article.featured_image.save(
                    img_data.name,
                    ContentFile(img_data.read()),
                    save=True
                )
            
            logger.info(f"Featured image saved for article {article.id}")
            
        except Exception as e:
            logger.error(f"Invalid image file for article {article.id}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading featured image for article {article.id}: {str(e)}")


def generate_article_with_gemini(article, mode='core'):
    """
    Generate article content in Malayalam using Google Gemini AI.
    Creates professional, editorial Malayalam content.
    
    Args:
        article: The article object
        mode: 'core' (default) - generates Title, Summary, Body
              'extras' - generates Reel script, Social media text, SEO metadata
              'full' - generates everything (legacy)
              
    Returns:
        dict: A dictionary with generated content fields
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured")
        return None
    
    try:
        # Get original English content for context
        original_title = article.title  # Keep original for slug generation
        original_summary = article.summary if article.summary and article.summary.strip() else "No summary provided"
        
        # Main prompt for generating complete Malayalam article
        if 'google.com/search' in article.source_url or 'search?' in article.source_url or article.source_feed == 'Trends Stub':
             # RESEARCH MODE for Stubs
             topic = article.title.replace(': Latest Updates', '').replace(': Latest News', '')
             prompt = f"""You are a professional news editor. I need you to research and write a BREAKING NEWS article in Malayalam about the topic: "{topic}".
             
             Since I cannot provide the full source text, you must:
             1. RECALL the most recent real-world events regarding "{topic}" (especially sports/cricket news from the last 24-48 hours).
             2. If "Ambati Rayudu" or "Cricket Academy" is related, focus on that.
             3. GENERATE a factual, news-style article in Malayalam based on your knowledge of recent events.
             4. DO NOT hallucinate a generic essay. Write about specific recent events (scores, inaugurations, matches, statements).
             
             TOPIC: {topic}
             CONTEXT: Recent Sports/News Trends
             
             REQUIRED OUTPUT FORMAT (provide as JSON):
             {{
                 "title_malayalam": "A specific, catchy headline about the recent event in Malayalam",
                 "summary_malayalam": "2-3 sentences summarizing the specific news event",
                 "summary_english": "2-3 sentences summarizing the event in English",
                 "body_malayalam": "Full detailed news report in Malayalam (4-5 paragraphs, HTML <p> tags). Include specific names, places, and context.",
                 "instagram_reel_script": "Engaging 30s script for Instagram Reel about this specific news",
                 "social_media_poster_text": "Catchy 3-4 word title for poster",
                 "social_media_caption": "Caption with hashtags",
                 "meta_title": "SEO Title",
                 "meta_description": "SEO Description",
                 "og_title": "Social Title",
                 "og_description": "Social Description"
             }}
             """
        else:
            # STANDARD MODE for normal articles
            prompt = f"""You are a professional Malayalam content writer and editor for a news/editorial website. Based on the following English article information, create a complete, localized Malayalam article.
    
    ORIGINAL ENGLISH TITLE: {original_title}
    
    ORIGINAL ENGLISH SUMMARY: {original_summary}
    
    SOURCE URL: {article.source_url if article.source_url else 'Not available'}
    
    IMPORTANT INSTRUCTIONS:
    1. DO NOT provide a plain translation. Instead, rewrite the article in authentic Malayalam editorial style
    2. Use professional, editorial, and authentic Malayalam language and tone
    3. Localize the content - adapt it for Malayalam-speaking readers while maintaining editorial authenticity
    4. Use appropriate Malayalam vocabulary, expressions, and cultural context
    5. Maintain journalistic standards and editorial voice
    
    REQUIRED OUTPUT FORMAT (provide as JSON):
    {{
        "title_malayalam": "Malayalam title (professional, editorial style)",
        "summary_malayalam": "Malayalam summary (2-3 sentences, professional editorial tone)",
        "summary_english": "English summary (2-3 sentences)",
        "body_malayalam": "Full article body in Malayalam (4-5 paragraphs in HTML format with <p> tags)",
        "instagram_reel_script": "Thoughtful and engaging Instagram Reel script (voiceover type) in Malayalam. Conversational, engaging, and summarizes the key points. Approx 30-60 seconds when read aloud.",
        "social_media_poster_text": "Short, punchy Malayalam text for a poster image (2-5 words, very catchy)",
        "social_media_caption": "Engaging Malayalam caption for social media (Facebook/Instagram) with relevant hashtags",
        "meta_title": "SEO meta title in Malayalam (60-70 characters)",
        "meta_description": "SEO meta description in Malayalam (150-160 characters)",
        "og_title": "OG title in Malayalam (60-70 characters)",
        "og_description": "OG description in Malayalam (200 characters max)"
    }}
    
    BODY REQUIREMENTS:
    - Write 4-5 substantial paragraphs (each 3-5 sentences)
    - Use HTML format with <p> tags only (no headings unless absolutely necessary)
    - Professional editorial tone - like a quality Malayalam news editorial
    - Engaging introduction, detailed body paragraphs, and strong conclusion
    - Localized yet authentic Malayalam - should read like original Malayalam journalism, not translation
    
    REEL SCRIPT REQUIREMENTS:
    - Engaging, conversational tone suitable for social media
    - Hook the viewer in the first 3 seconds
    - Summarize the main story quickly and interestingly
    - End with a call to action (e.g., "Read more strictly on our website")
    """

        prompt += "\nReturn the JSON response with all fields filled."

        # Initialize the model
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            logger.info(f"Initialized Gemini model: {GEMINI_MODEL}")
        except Exception as model_error:
            error_msg = str(model_error)
            logger.error(f"Failed to initialize model {GEMINI_MODEL}: {error_msg}")
            
            # Check if it's a model name issue or API key issue
            if '403' in error_msg or 'leaked' in error_msg.lower() or 'PermissionDenied' in error_msg:
                logger.error("API KEY ERROR: Your Gemini API key is invalid or has been revoked.")
                return None
            
            # Try fallback model
            try:
                logger.info("Trying fallback model: gemini-flash-latest")
                model = genai.GenerativeModel('gemini-flash-latest')
                logger.info("Successfully initialized fallback model")
            except Exception as fallback_error:
                logger.error(f"Failed to initialize fallback model: {str(fallback_error)}")
                return None
        
        # Generate content
        try:
            logger.info(f"Calling Gemini API with model: {GEMINI_MODEL}")
            response = model.generate_content(prompt)
            logger.info("Gemini API call successful")
        except Exception as api_error:
            error_msg = str(api_error)
            logger.error(f"Gemini API call failed: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Check for specific error types
            if '403' in error_msg or 'leaked' in error_msg.lower() or 'PermissionDenied' in error_msg:
                logger.error("API KEY ERROR: Your Gemini API key is invalid or has been revoked. Please generate a new API key from Google AI Studio.")
            elif '404' in error_msg or 'NotFound' in error_msg:
                logger.error("MODEL ERROR: The specified Gemini model is not found. Please check the model name.")
            elif '429' in error_msg or 'quota' in error_msg.lower():
                logger.error("QUOTA ERROR: API quota exceeded. Please check your usage limits.")
            
            return None
        
        if response and response.text:
            generated_text = response.text.strip()
            logger.info(f"Gemini response received (length: {len(generated_text)})")
            
            # Try to parse JSON response
            import json
            import re
            
            # Extract JSON from the response (might have markdown code blocks)
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                try:
                    content_data = json.loads(json_match.group())
                    logger.info("Successfully parsed JSON from Gemini response")
                    
                    # Return structured data
                    return {
                        'title_malayalam': content_data.get('title_malayalam', ''),
                        'summary_malayalam': content_data.get('summary_malayalam', ''),
                        'summary_english': content_data.get('summary_english', ''),
                        'body_malayalam': content_data.get('body_malayalam', ''),
                        'instagram_reel_script': content_data.get('instagram_reel_script', ''),
                        'social_media_poster_text': content_data.get('social_media_poster_text', ''),
                        'social_media_caption': content_data.get('social_media_caption', ''),
                        'meta_title': content_data.get('meta_title', ''),
                        'meta_description': content_data.get('meta_description', ''),
                        'og_title': content_data.get('og_title', ''),
                        'og_description': content_data.get('og_description', ''),
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {str(e)}")
                    logger.error(f"Response was: {generated_text[:1000]}")
            else:
                logger.warning("No JSON found in Gemini response")
                logger.debug(f"Response was: {generated_text[:500]}")
            
            # Fallback: if JSON parsing fails, try to extract content manually
            logger.warning("JSON parsing failed, attempting to extract content from text")
            # Try to create a simple body from the response if it's not JSON
            if generated_text and len(generated_text) > 100:
                # Extract first few paragraphs if possible
                paragraphs = generated_text.split('\n\n')
                body_content = '\n'.join([f'<p>{p.strip()}</p>' for p in paragraphs[:5] if p.strip()])
                if body_content:
                    logger.info("Extracted content from text response")
                    return {
                        'title_malayalam': original_title,  # Keep original if no translation
                        'summary_malayalam': paragraphs[0][:200] if paragraphs else original_summary,
                        'summary_english': original_summary,
                        'body_malayalam': body_content,
                        'meta_title': original_title[:70],
                        'meta_description': (paragraphs[0][:160] if paragraphs else original_summary[:160]),
                        'og_title': original_title[:70],
                        'og_description': (paragraphs[0][:200] if paragraphs else original_summary[:200]),
                    }
            return None
        else:
            logger.error(f"Gemini returned empty or invalid response: {response}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating article with Gemini: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None


def generate_audio_for_article(article, voice_name='chirp'):
    """
    Generate audio for article body using Google Cloud Text-to-Speech.
    Uses Malayalam (ml-IN) voices with an energetic news anchor style.
    
    Args:
        article: Article instance with body content
        voice_name: Voice name to use (default: 'karthika')
                    Options: 'karthika', 'ml-IN-Wavenet-A', 'ml-IN-Wavenet-B', 
                            'ml-IN-Standard-A', 'ml-IN-Standard-B', etc.
    
    Returns:
        bool: True if audio was generated successfully, False otherwise
    """
    if not TTS_AVAILABLE:
        logger.warning("Google Cloud Text-to-Speech not available. Skipping audio generation.")
        return False
    
    # Check if Google Cloud service account credentials are configured
    # Google Cloud TTS requires service account credentials (JSON key file)
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        logger.warning("Google Cloud TTS service account credentials not configured. Set GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account JSON key file.")
        return False
    
    # Verify the credentials file exists
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not os.path.exists(creds_path):
        logger.warning(f"Google Cloud TTS credentials file not found at: {creds_path}. Please check the GOOGLE_APPLICATION_CREDENTIALS path in your .env file.")
        return False
    
    if not article.body or not article.body.strip():
        logger.warning(f"Article {article.id} has no body content. Skipping audio generation.")
        return False
    
    try:
        logger.info(f"Starting audio generation for article {article.id} with voice: {voice_name}")
        
        # Initialize the TTS client
        # Google Cloud TTS requires service account credentials (GOOGLE_APPLICATION_CREDENTIALS)
        # or can use default credentials if running on GCP
        client = texttospeech.TextToSpeechClient()
        
        # Extract text from HTML body (remove HTML tags)
        soup = BeautifulSoup(article.body, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Clean up the text
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if not text_content or len(text_content) < 50:
            logger.warning(f"Extracted text is too short for article {article.id}. Skipping audio generation.")
            return False
        
        # For long articles, truncate to avoid API limits
        # Google TTS has a 5000 byte limit for SSML input
        # Malayalam text uses more bytes per character (UTF-8 encoding)
        # SSML tags add overhead (~150-200 bytes)
        # So we limit to ~4000 characters for safety
        
        max_chars = 4000
        if len(text_content) > max_chars:
            logger.info(f"Article body is too long ({len(text_content)} chars), truncating to {max_chars} chars")
            # Find a good breaking point (end of sentence)
            truncated = text_content[:max_chars]
            last_period = truncated.rfind('.')
            last_question = truncated.rfind('?')
            last_exclamation = truncated.rfind('!')
            last_sentence_end = max(last_period, last_question, last_exclamation)
            
            if last_sentence_end > max_chars * 0.8:  # If we can find a sentence end in last 20%
                text_content = truncated[:last_sentence_end + 1]
            else:
                text_content = truncated + "..."
        
        # Double-check byte size (SSML will add ~200 bytes overhead)
        text_bytes = len(text_content.encode('utf-8'))
        ssml_overhead = 200  # Approximate SSML tag overhead
        max_bytes = 4800  # Leave some buffer
        
        if text_bytes + ssml_overhead > max_bytes:
            # Reduce more aggressively based on bytes
            target_bytes = max_bytes - ssml_overhead - 100  # Extra buffer
            # Truncate byte by byte to ensure we stay under limit
            text_encoded = text_content.encode('utf-8')
            if len(text_encoded) > target_bytes:
                # Decode up to target_bytes, handling UTF-8 boundaries
                truncated_bytes = text_encoded[:target_bytes]
                # Find last valid UTF-8 character boundary
                while truncated_bytes and truncated_bytes[-1] & 0xC0 == 0x80:
                    truncated_bytes = truncated_bytes[:-1]
                text_content = truncated_bytes.decode('utf-8', errors='ignore')
                # Try to end at sentence boundary
                last_period = text_content.rfind('.')
                if last_period > len(text_content) * 0.8:
                    text_content = text_content[:last_period + 1]
                else:
                    text_content = text_content + "..."
                logger.info(f"Truncated to {len(text_content.encode('utf-8'))} bytes to fit SSML limit")
        
        # Set up the voice parameters for Malayalam (ml-IN)
        # Map voice names to actual Google Cloud TTS voice names
        # Quality ranking: Chirp3-HD > Neural2 > WaveNet > Standard
        
        # Three best voices for news reading (in order of quality):
        # 1. Chirp3-HD-Despina - Highest quality, most natural (best for news)
        # 2. Neural2-A - High quality, excellent prosody
        # 3. Wavenet-A - Premium quality, widely available (current default)
        
        voice_mapping = {
            # Top 3 voices for news reading (best quality first)
            'chirp': 'ml-IN-Chirp3-HD-Despina',  # 🥇 Best quality - Most natural for news
            'neural2': 'ml-IN-Neural2-A',  # 🥈 High quality - Excellent prosody
            'wavenet': 'ml-IN-Wavenet-A',  # 🥉 Premium quality - Widely available
            
            # Legacy/alias names
            'karthika': 'ml-IN-Wavenet-A',  # Alias for WaveNet (current default)
            'best': 'ml-IN-Chirp3-HD-Despina',  # Alias for best quality voice
            'premium': 'ml-IN-Neural2-A',  # Alias for premium quality
            
            # Gender-based mappings (default to WaveNet for compatibility)
            'female': 'ml-IN-Wavenet-A',  # Female WaveNet voice
            'male': 'ml-IN-Wavenet-B',  # Male WaveNet voice
            
            # Alternative voices
            'female-alt': 'ml-IN-Wavenet-C',  # Alternative female WaveNet voice
            'chirp-alt': 'ml-IN-Chirp3-HD-Erinome',  # Alternative Chirp voice
            'neural2-alt': 'ml-IN-Neural2-C',  # Alternative Neural2 voice
            
            # Standard voices (lower cost options)
            'standard-female': 'ml-IN-Standard-A',  # Standard female voice
            'standard-male': 'ml-IN-Standard-B',  # Standard male voice
        }
        
        # Use mapped voice name or use directly if it's already a valid voice name
        actual_voice_name = voice_mapping.get(voice_name.lower(), voice_name)
        
        # Build smart fallback chain based on requested voice
        # Each voice type has its own fallback strategy
        if voice_name.lower() in ['chirp', 'best']:
            # Chirp fallback: Try Chirp first, then Neural2, then WaveNet
            voice_fallback_chain = [
                actual_voice_name,  # ml-IN-Chirp3-HD-Despina
                'ml-IN-Neural2-A',  # Fallback to Neural2
                'ml-IN-Wavenet-A',  # Fallback to WaveNet
                'ml-IN-Standard-A',  # Final fallback to Standard
            ]
        elif voice_name.lower() in ['neural2', 'premium']:
            # Neural2 fallback: Try Neural2 first, then WaveNet
            voice_fallback_chain = [
                actual_voice_name,  # ml-IN-Neural2-A
                'ml-IN-Wavenet-A',  # Fallback to WaveNet
                'ml-IN-Standard-A',  # Final fallback to Standard
            ]
        elif voice_name.lower() in ['wavenet', 'karthika', 'female']:
            # WaveNet fallback: Try WaveNet first, then Standard
            voice_fallback_chain = [
                actual_voice_name,  # ml-IN-Wavenet-A
                'ml-IN-Wavenet-C',  # Try alternative WaveNet voice
                'ml-IN-Standard-A',  # Final fallback to Standard
            ]
        else:
            # Default fallback for unknown voices
            voice_fallback_chain = [
                actual_voice_name,
                'ml-IN-Wavenet-A',
                'ml-IN-Standard-A',
            ]
        
        logger.info(f"Requested voice: {voice_name} -> Mapped to: {actual_voice_name}")
        logger.info(f"Fallback chain for {voice_name}: {voice_fallback_chain}")
        
        # Configure audio output with voice-specific settings to make each voice distinct
        # Each voice type gets slightly different settings to emphasize their unique characteristics
        voice_name_lower = voice_name.lower()
        
        if voice_name_lower in ['chirp', 'best']:
            # Chirp: Premium quality - smoother, more natural prosody
            # Use slightly slower rate to showcase natural flow
            speaking_rate = 1.05
            pitch = 1.5
            volume_gain_db = 1.5
            prosody_rate = "1.05"
            prosody_pitch = "+1.5st"
            emphasis_level = "moderate"  # Moderate emphasis to preserve natural flow
        elif voice_name_lower in ['neural2', 'premium']:
            # Neural2: High quality - excellent prosody and clarity
            # Balanced settings for clear, professional delivery
            speaking_rate = 1.1
            pitch = 2.0
            volume_gain_db = 2.0
            prosody_rate = "1.1"
            prosody_pitch = "+2st"
            emphasis_level = "strong"  # Strong emphasis for news anchor style
        elif voice_name_lower in ['wavenet', 'karthika', 'female']:
            # WaveNet: Premium quality - energetic and clear
            # Slightly faster and higher pitch for energetic news anchor feel
            speaking_rate = 1.15
            pitch = 2.5
            volume_gain_db = 2.5
            prosody_rate = "1.15"
            prosody_pitch = "+2.5st"
            emphasis_level = "strong"  # Strong emphasis for energetic delivery
        else:
            # Default settings for unknown voices
            speaking_rate = 1.1
            pitch = 2.0
            volume_gain_db = 2.0
            prosody_rate = "1.1"
            prosody_pitch = "+2st"
            emphasis_level = "strong"
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
            effects_profile_id=['headphone-class-device'],  # Optimized for listening
        )
        
        logger.info(f"Audio config for {voice_name}: rate={speaking_rate}, pitch={pitch}, volume={volume_gain_db}dB")
        
        # Escape XML/SSML special characters in text content
        escaped_text = html.escape(text_content)
        
        # Add SSML for news anchor style with voice-specific emphasis
        # This creates distinct, energetic, professional news anchor delivery for each voice
        ssml_text = f"""<speak>
            <prosody rate="{prosody_rate}" pitch="{prosody_pitch}" volume="loud">
                <emphasis level="{emphasis_level}">{escaped_text}</emphasis>
            </prosody>
        </speak>"""
        
        logger.info(f"SSML config for {voice_name}: rate={prosody_rate}, pitch={prosody_pitch}, emphasis={emphasis_level}")
        
        # Synthesize speech with fallback logic
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        
        # Try voices in fallback order until one works
        last_error = None
        response = None
        used_fallback = False
        
        for idx, attempt_voice in enumerate(voice_fallback_chain):
            try:
                # Configure the voice
                voice = texttospeech.VoiceSelectionParams(
                    language_code='ml-IN',
                    name=attempt_voice,
                )
                
                logger.info(f"Attempting audio synthesis with voice {attempt_voice} for article {article.id} (attempt {idx + 1}/{len(voice_fallback_chain)})")
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Success! Update actual_voice_name and break out of loop
                actual_voice_name = attempt_voice
                if idx > 0:
                    used_fallback = True
                    logger.warning(f"⚠️ Used fallback voice: {attempt_voice} (original requested: {voice_fallback_chain[0]})")
                    logger.warning(f"⚠️ This means {voice_fallback_chain[0]} is not available in your Google Cloud project")
                else:
                    logger.info(f"✅ Successfully used requested voice: {attempt_voice}")
                break
                
            except Exception as voice_error:
                last_error = voice_error
                error_msg = str(voice_error)
                
                # Check if it's a voice not found error
                if 'not found' in error_msg.lower() or 'invalid' in error_msg.lower() or '404' in error_msg:
                    logger.warning(f"Voice {attempt_voice} not available: {error_msg}")
                else:
                    logger.warning(f"Voice {attempt_voice} failed: {error_msg}")
                
                # If this is not the last fallback, try next one
                if idx < len(voice_fallback_chain) - 1:
                    logger.info(f"Trying next fallback voice...")
                    continue
                else:
                    # All voices failed, raise the last error
                    logger.error(f"All voice fallbacks failed. Last error: {error_msg}")
                    raise last_error
        
        if response is None:
            raise Exception("All voice fallbacks failed")
        
        # Log warning if fallback was used
        if used_fallback:
            logger.warning(f"⚠️ NOTE: Requested voice '{voice_fallback_chain[0]}' was not available. Used '{actual_voice_name}' instead.")
            logger.warning(f"⚠️ To use premium voices, ensure they are enabled in your Google Cloud project.")
            logger.warning(f"⚠️ This is why all voices might sound the same - they're all falling back to '{actual_voice_name}'")
        else:
            logger.info(f"✅ Successfully used requested voice '{actual_voice_name}' for article {article.id}")
        
        # Save the audio file with actual voice name in filename for comparison
        # Use actual_voice_name to reflect what was actually used (not just requested)
        voice_short_name = actual_voice_name.split('-')[-1] if '-' in actual_voice_name else actual_voice_name
        audio_filename = f'article_{article.id}_audio_{voice_name.lower()}_actual_{voice_short_name.lower()}.mp3'
        
        # Create audio file in memory
        audio_content = response.audio_content
        
        # Save to article's audio field
        # Note: This will overwrite previous audio, but filename includes voice name
        article.audio.save(
            audio_filename,
            ContentFile(audio_content),
            save=True
        )
        
        logger.info(f"Audio generated successfully for article {article.id} with voice {voice_name}: {audio_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating audio for article {article.id}: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def _generate_article_task_impl(article_id):
    """
    Internal implementation of article generation.
    Can be called directly or via Celery.
    Generates full article content from a fetched article using Gemini AI.
    """
    try:
        article = Article.objects.get(id=article_id)
        
        # Mark generation as started
        article.generation_started_at = timezone.now()
        article.save()
        
        logger.info(f"Starting article generation for Article {article_id} in Malayalam")
        
        # Store original English title for slug generation
        original_english_title = article.title
        
        # Fetch featured image from source URL (if not already present)
        if not article.featured_image and article.source_url:
            logger.info(f"Fetching featured image from source URL: {article.source_url}")
            fetch_and_save_featured_image(article)
        
        # Generate complete Malayalam content using Gemini AI
        logger.info(f"Starting Gemini generation for article {article_id}")
        # Generate full content in one go (legacy mode restored)
        generated_content = generate_article_with_gemini(article)
        
        if generated_content and isinstance(generated_content, dict):
            # Verify we have at least body content
            if generated_content.get('body_malayalam'):
                # Update all fields with Malayalam content
                article.title = generated_content.get('title_malayalam', article.title)
                article.summary = generated_content.get('summary_malayalam', article.summary)
                article.summary_english = generated_content.get('summary_english', '')
                article.body = generated_content.get('body_malayalam', '')
                article.instagram_reel_script = generated_content.get('instagram_reel_script', '')
                article.social_media_poster_text = generated_content.get('social_media_poster_text', '')
                article.social_media_caption = generated_content.get('social_media_caption', '')
                article.meta_title = generated_content.get('meta_title', '')
                article.meta_description = generated_content.get('meta_description', '')
                article.og_title = generated_content.get('og_title', '')
                article.og_description = generated_content.get('og_description', '')
                
                logger.info(f"Malayalam article content generated successfully using Gemini AI")
            else:
                logger.warning(f"Gemini returned content but body_malayalam is empty")
                generated_content = None  # Force fallback
        
        if not generated_content:
            # Fallback to basic content if Gemini fails
            logger.warning(f"Gemini generation failed for article {article_id}, using fallback content")
            if article.summary:
                article.body = f"""
<p>സഹകരണമില്ലായ്മ കാരണം ഈ ലേഖനത്തിന് ഉള്ളടക്കം ഇതുവരെ സൃഷ്ടിച്ചിട്ടില്ല. ദയവായി പിന്നീട് പരിശോധിക്കുക അല്ലെങ്കിൽ ഉള്ളടക്കം സ്വമേധയാ ചേർക്കുക.</p>
<p>മൂല സ്രോതസ്സ്: <a href="{article.source_url}" target="_blank">{article.source_url}</a></p>
"""
            else:
                article.body = f"""
<p>ലേഖന ഉള്ളടക്കം സൃഷ്ടിക്കുന്ന പ്രക്രിയ നടന്നുകൊണ്ടിരിക്കുന്നു. ദയവായി പിന്നീട് പരിശോധിക്കുക അല്ലെങ്കിൽ ഉള്ളടക്കം സ്വമേധയാ ചേർക്കുക.</p>
<p>മൂല സ്രോതസ്സ്: <a href="{article.source_url}" target="_blank">{article.source_url}</a></p>
"""
        
        # Generate slug from original English title (keep slug in English)
        if not article.slug:
            # Use original English title for slug generation
            article.slug = slugify(original_english_title)
            # Ensure uniqueness
            base_slug = article.slug
            counter = 1
            while Article.objects.filter(slug=article.slug).exclude(id=article.id).exists():
                article.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Ensure meta fields have content (use Malayalam title/summary if not generated)
        if not article.meta_title and article.title:
            article.meta_title = article.title[:70]  # Limit to 70 chars
        
        if not article.meta_description and article.summary:
            article.meta_description = article.summary[:160]  # Limit to 160 chars
        
        if not article.og_title and article.title:
            article.og_title = article.title[:70]
        
        if not article.og_description and article.summary:
            article.og_description = article.summary[:200]  # Limit to 200 chars
        
        # Auto-assign categories based on content
        logger.info(f"Auto-assigning categories to article {article_id}")
        auto_assign_categories(article)
        
        # Note: Audio generation is skipped here - will be generated when article is published
        # This saves costs by only generating audio for published articles
        
        # Mark as draft (ready for editing)
        article.status = 'draft'
        article.generation_completed_at = timezone.now()
        article.save()
        
        logger.info(f"Article generation completed for Article {article_id}")
        
        return {
            'success': True,
            'article_id': article_id,
            'status': 'draft'
        }
    
    except Article.DoesNotExist:
        logger.error(f"Article {article_id} not found")
        return {
            'success': False,
            'error': 'Article not found'
        }
    
    except Exception as e:
        logger.error(f"Error generating article {article_id}: {str(e)}")
        article = Article.objects.filter(id=article_id).first()
        if article:
            article.generation_completed_at = timezone.now()
            article.save()
        return {
            'success': False,
            'error': str(e)
        }


def generate_instagram_reel_audio(article, voice_name='chirp'):
    """
    Generate audio for Instagram Reel script using Google Cloud Text-to-Speech.
    
    Args:
        article: Article instance with instagram_reel_script
        voice_name: Voice name to use
    
    Returns:
        bool: True if audio was generated successfully, False otherwise
    """
    if not TTS_AVAILABLE:
        logger.warning("Google Cloud Text-to-Speech not available. Skipping reel audio generation.")
        return False
    
    if not article.instagram_reel_script or not article.instagram_reel_script.strip():
        logger.warning(f"Article {article.id} has no reel script. Skipping audio generation.")
        return False
        
    try:
        logger.info(f"Starting reel audio generation for article {article.id} with voice: {voice_name}")
        
        client = texttospeech.TextToSpeechClient()
        text_content = article.instagram_reel_script.strip()
        
        # Map voice names
        voice_mapping = {
            'chirp': 'ml-IN-Chirp3-HD-Despina',
            'neural2': 'ml-IN-Neural2-A',
            'wavenet': 'ml-IN-Wavenet-A',
            'karthika': 'ml-IN-Wavenet-A',
            'best': 'ml-IN-Chirp3-HD-Despina',
            'premium': 'ml-IN-Neural2-A',
        }

        # Build smart fallback chain based on requested voice
        if voice_name.lower() in ['chirp', 'best']:
            voice_fallback_chain = [
                'ml-IN-Chirp3-HD-Despina',
                'ml-IN-Neural2-A',
                'ml-IN-Wavenet-A',
                'ml-IN-Standard-A',
            ]
        elif voice_name.lower() in ['neural2', 'premium']:
            voice_fallback_chain = [
                'ml-IN-Neural2-A',
                'ml-IN-Wavenet-A',
                'ml-IN-Standard-A',
            ]
        else:
            voice_name_default = voice_mapping.get(voice_name.lower(), voice_name)
            voice_fallback_chain = [
                voice_name_default,
                'ml-IN-Wavenet-A',
                'ml-IN-Standard-A',
            ]

        # Audio config - optimize for social media (louder effectively)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.1, # Slightly faster for reels
            pitch=1.0,
            volume_gain_db=4.0, # Louder for social media
            effects_profile_id=['headphone-class-device'],
        )
        
        # SSML
        escaped_text = html.escape(text_content)
        ssml_text = f"""<speak>
            <prosody rate="1.1" pitch="+1st">
                {escaped_text}
            </prosody>
        </speak>"""
        
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        
        # Try voices in fallback order until one works
        response = None
        last_error = None
        used_voice_name = None
        
        for attempt_voice in voice_fallback_chain:
            try:
                logger.info(f"Attempting reel generation with voice: {attempt_voice}")
                
                voice = texttospeech.VoiceSelectionParams(
                    language_code='ml-IN',
                    name=attempt_voice,
                )
                
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # If we get here, it worked
                used_voice_name = attempt_voice
                logger.info(f"Successfully generated reel audio with voice: {attempt_voice}")
                break
                
            except Exception as inner_e:
                last_error = inner_e
                logger.warning(f"Failed to generate reel audio with voice {attempt_voice}: {str(inner_e)}")
                continue
                
        if not response:
            logger.error(f"All voice attempts failed for reel audio. Last error: {str(last_error)}")
            return False
        
        # Save audio
        voice_short_name = used_voice_name.split('-')[-1] if '-' in used_voice_name else used_voice_name
        audio_filename = f'reel_{article.id}_audio_{voice_short_name.lower()}.mp3'
        
        article.instagram_reel_audio.save(
            audio_filename,
            ContentFile(response.audio_content),
            save=True
        )
        
        logger.info(f"Reel audio saved to {audio_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating reel audio for article {article.id}: {str(e)}")
        return False


@shared_task
def generate_article_task(article_id):
    """
    Celery task wrapper for article generation.
    Calls the internal implementation.
    """
    return _generate_article_task_impl(article_id)

