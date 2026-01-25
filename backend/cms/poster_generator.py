
import os
import logging
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from .models import PosterTemplate

logger = logging.getLogger(__name__)

def wrap_text(text, font, max_width):
    """
    Wrap text to fit within max_width.
    Returns a list of lines.
    """
    lines = []
    
    # If text is empty, return empty list
    if not text:
        return lines
        
    words = text.split()
    if not words:
        return lines

    current_line = words[0]
    
    for word in words[1:]:
        # Check width of line with next word
        test_line = current_line + " " + word
        bbox = font.getbbox(test_line)
        # getbbox returns (left, top, right, bottom)
        w = bbox[2] - bbox[0]
        
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
            
    lines.append(current_line)
    return lines

def generate_poster(article, template_id=None):
    """
    Generate a social media poster for the article.
    If template_id is provided, uses that template.
    Otherwise, uses the first active template found.
    """
    try:
        # 1. Get Template
        if template_id:
            template = PosterTemplate.objects.get(id=template_id)
        else:
            template = PosterTemplate.objects.filter(is_active=True).first()
            
        if not template:
            logger.error("No active poster template found.")
            return False, "No active poster template found."
            
        if not template.background_image:
            logger.error(f"Template {template.name} has no background image.")
            return False, "Template has no background image."

        # 2. Open Template Image
        try:
            bg_image = Image.open(template.background_image.path).convert("RGBA")
        except Exception as e:
            logger.error(f"Failed to open template image: {e}")
            return False, f"Failed to open template image: {e}"
            
        # 3. Process Featured Image Overlay
        if article.featured_image:
            img_config_list = template.image_config.get('image_fields', [])
            
            # Default behavior if config is empty but we have an image
            # Put it in top half or center? Better to rely on config.
            # If config is empty, we might skip overlay or do a default center crop.
            
            for config in img_config_list:
                if config.get('name') == 'featured_image':
                    try:
                        # Load article image
                        article_img = Image.open(article.featured_image.path).convert("RGBA")
                        
                        target_w = config.get('width', 500)
                        target_h = config.get('height', 500)
                        pos_x = config.get('x', 0)
                        pos_y = config.get('y', 0)
                        
                        # Resize/Crop logic (Aspect Fill)
                        img_ratio = article_img.width / article_img.height
                        target_ratio = target_w / target_h
                        
                        if img_ratio > target_ratio:
                            # Image is wider - crop width
                            new_height = target_h
                            new_width = int(new_height * img_ratio)
                        else:
                            # Image is taller - crop height
                            new_width = target_w
                            new_height = int(new_width / img_ratio)
                            
                        # Resize
                        article_img = article_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Center Crop
                        left = (new_width - target_w) / 2
                        top = (new_height - target_h) / 2
                        right = (new_width + target_w) / 2
                        bottom = (new_height + target_h) / 2
                        
                        article_img = article_img.crop((left, top, right, bottom))
                        
                        # Paste onto background
                        bg_image.paste(article_img, (pos_x, pos_y), article_img)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process featured image overlay: {e}")

        # 4. Process Text Overlay
        draw = ImageDraw.Draw(bg_image)
        
        # Load Font
        font_path = os.path.join(settings.BASE_DIR, 'static/fonts/Manjari-Bold.ttf')
        if not os.path.exists(font_path):
             # Fallback to a system font if specific one not found
            font_path = "arial.ttf" # This might fail on linux, but PIL has defaults
            logger.warning("Manjari-Bold.ttf not found, using default.")

        text_config_list = template.text_config.get('text_fields', [])
        
        # Default if no config: Just print headlines in center
        if not text_config_list:
             # Basic default placement
             text_config_list = [
                 {"name": "headline", "x": 50, "y": 50, "font_size": 60, "color": "#FFFFFF", "max_width": bg_image.width - 100}
             ]
             
        for config in text_config_list:
            field_name = config.get('name')
            
            text_content = ""
            if field_name == 'headline':
                text_content = article.social_media_poster_text or article.title
            elif field_name == 'summary':
                text_content = article.social_media_caption or article.summary
            elif field_name == 'slug':
                text_content = f"@{article.source_feed}" if article.source_feed else "@pavilionend.in"
            
            if not text_content:
                continue
                
            # Font settings
            font_size = config.get('font_size', 40)
            text_color = config.get('color', '#FFFFFF')
            max_width = config.get('max_width', bg_image.width)
            x = config.get('x', 0)
            y = config.get('y', 0)
            align = config.get('align', 'left')
            
            try:
                if "Manjari" in font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
            except IOError:
                font = ImageFont.load_default()

            # Wrap text
            lines = wrap_text(text_content, font, max_width)
            
            # Draw lines
            current_y = y
            line_height_factor = 1.2
            
            for line in lines:
                # Calculate text width for alignment
                bbox = font.getbbox(line)
                line_w = bbox[2] - bbox[0]
                line_h = bbox[3] - bbox[1] # Approximate height
                
                draw_x = x
                if align == 'center':
                    draw_x = x + (max_width - line_w) / 2
                elif align == 'right':
                    draw_x = x + (max_width - line_w)
                
                # Draw text with outline for better visibility
                outline_color = "#000000"
                outline_width = 2
                draw.text((draw_x-outline_width, current_y), line, font=font, fill=outline_color)
                draw.text((draw_x+outline_width, current_y), line, font=font, fill=outline_color)
                draw.text((draw_x, current_y-outline_width), line, font=font, fill=outline_color)
                draw.text((draw_x, current_y+outline_width), line, font=font, fill=outline_color)
                
                draw.text((draw_x, current_y), line, font=font, fill=text_color)
                
                current_y += font_size * line_height_factor

        # 5. Save Result
        buffer = BytesIO()
        bg_image = bg_image.convert('RGB') # Remove alpha for JPEG
        bg_image.save(buffer, format='JPEG', quality=95)
        
        filename = f"poster_{article.id}_{template.id}.jpg"
        
        # Save to article model
        article.generated_poster.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        return True, article.generated_poster.url
        
    except Exception as e:
        logger.error(f"Error generating poster: {e}", exc_info=True)
        return False, str(e)
