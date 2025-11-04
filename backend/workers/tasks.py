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
from cms.models import Article
from slugify import slugify
import logging
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

logger = logging.getLogger(__name__)

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
            
            # Create filename
            filename = f"article_{article.id}_featured.{file_ext}"
            
            # Save to article
            article.featured_image.save(
                filename,
                ContentFile(img_data.read()),
                save=True
            )
            
            logger.info(f"Featured image saved for article {article.id}: {filename}")
            
        except Exception as e:
            logger.error(f"Invalid image file for article {article.id}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading featured image for article {article.id}: {str(e)}")


def generate_article_with_gemini(article):
    """
    Generate article content in Malayalam using Google Gemini AI.
    Creates professional, editorial Malayalam content with all required fields.
    Returns a dictionary with all generated content.
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured")
        return None
    
    try:
        # Get original English content for context
        original_title = article.title  # Keep original for slug generation
        original_summary = article.summary if article.summary and article.summary.strip() else "No summary provided"
        
        # Main prompt for generating complete Malayalam article
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

Return the JSON response with all fields filled."""

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
        generated_content = generate_article_with_gemini(article)
        
        if generated_content and isinstance(generated_content, dict):
            # Verify we have at least body content
            if generated_content.get('body_malayalam'):
                # Update all fields with Malayalam content
                article.title = generated_content.get('title_malayalam', article.title)
                article.summary = generated_content.get('summary_malayalam', article.summary)
                article.summary_english = generated_content.get('summary_english', '')
                article.body = generated_content.get('body_malayalam', '')
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


@shared_task
def generate_article_task(article_id):
    """
    Celery task wrapper for article generation.
    Calls the internal implementation.
    """
    return _generate_article_task_impl(article_id)

