
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pavilion_gemini.settings")
django.setup()

from django.core.management.base import BaseCommand
from cms.models import PosterTemplate
import os

from django.conf import settings

class Command(BaseCommand):
    help = 'Seeds initial social media poster templates'

    def handle(self, *args, **options):
        self.create_templates()

    def create_templates(self):
        from django.core.files import File
        
        # Define source directory for templates (part of the codebase, not media volume)
        fixtures_dir = os.path.join(settings.BASE_DIR, 'cms', 'fixtures', 'posters')
        
        # Template 1: Standard Article (Joe Root style)
        t1_filename = 'template_01.png'
        t1_path = os.path.join(fixtures_dir, t1_filename)
        
        if os.path.exists(t1_path):
            t1, created = PosterTemplate.objects.get_or_create(name="Standard Poster (Top Text)")
            if created or not t1.background_image:
                # Open the file and save it to the model (this copies it to MEDIA_ROOT)
                with open(t1_path, 'rb') as f:
                    t1.background_image.save(f"templates/posters/{t1_filename}", File(f), save=True)
                
            # Config based on the visual
            t1.text_config = {
                "text_fields": [
                    {
                        "name": "headline",
                        "x": 50,
                        "y": 80, 
                        "font_size": 85,
                        "color": "#FFFF00", # Yellow
                        "max_width": 980,
                        "align": "center"
                    },
                    {
                        "name": "summary",
                        "x": 50,
                        "y": 380,
                        "font_size": 55,
                        "color": "#FFFFFF",
                        "max_width": 980,
                        "align": "center"
                    }
                ]
            }
            
            t1.image_config = {
                "image_fields": [
                    {
                        "name": "featured_image",
                        "x": 0,
                        "y": 550, # Moved UP to overlap slightly with bottom of text area if needed, but mostly fill bottom
                        "width": 1080,
                        "height": 1370, # Increased height
                        "remove_background": True,
                        "fit_mode": "contain",
                        "align_vertical": "bottom"
                    }
                ]
            }
            t1.save()
            print(f"Created/Updated Template: {t1.name}")
        else:
            print(f"Warning: Template source file not found at {t1_path}")

        # Template 2: Breaking News
        t2_filename = 'template_02.png'
        t2_path = os.path.join(fixtures_dir, t2_filename)
        
        if os.path.exists(t2_path):
            t2, created = PosterTemplate.objects.get_or_create(name="Breaking News")
            if created or not t2.background_image:
                with open(t2_path, 'rb') as f:
                    t2.background_image.save(f"templates/posters/{t2_filename}", File(f), save=True)
            
            t2.text_config = {
                "text_fields": [
                    {
                        "name": "headline",
                        "x": 50,
                        "y": 250, 
                        "font_size": 70,
                        "color": "#009999", # Teal/Cyan
                        "max_width": 900,
                        "align": "left"
                    },
                     {
                        "name": "summary",
                        "x": 50,
                        "y": 400, 
                        "font_size": 60,
                        "color": "#FFFFFF",
                        "max_width": 900,
                        "align": "left"
                    }
                ]
            }
            
            t2.image_config = {
                "image_fields": [
                    {
                        "name": "featured_image",
                        "x": 0,
                        "y": 600,
                        "width": 1080,
                        "height": 1000
                    }
                ]
            }
            t2.save()
            print(f"Created/Updated Template: {t2.name}")
        else:
            print(f"Warning: Template source file not found at {t2_path}")

if __name__ == "__main__":
    pass
