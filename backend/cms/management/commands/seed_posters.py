
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
        # Template 1: Standard Article (Joe Root style)
        # Use settings.MEDIA_ROOT to find files reliably anywhere
        t1_path = os.path.join(settings.MEDIA_ROOT, 'templates', 'posters', 'template_01.png')
        if os.path.exists(t1_path):
            t1, created = PosterTemplate.objects.get_or_create(name="Standard Poster (Top Text)")
            # For ImageField, we set the name relative to MEDIA_ROOT (which is usually inside media/)
            # If MEDIA_ROOT is 'backend/media', then we just need 'templates/posters/template_01.png'
            t1.background_image.name = 'templates/posters/template_01.png'
            
            # Config based on the visual
            t1.text_config = {
                "text_fields": [
                    {
                        "name": "headline",
                        "x": 50,
                        "y": 100, 
                        "font_size": 80,
                        "color": "#FFFF00", # Yellow
                        "max_width": 900,
                        "align": "center"
                    },
                    {
                        "name": "summary",
                        "x": 50,
                        "y": 300,
                        "font_size": 50,
                        "color": "#FFFFFF",
                        "max_width": 900,
                        "align": "center"
                    }
                ]
            }
            
            t1.image_config = {
                "image_fields": [
                    {
                        "name": "featured_image",
                        "x": 0,
                        "y": 600, # Bottom half
                        "width": 1080,
                        "height": 1320, # Fill bottom?
                    }
                ]
            }
            t1.save()
            print(f"Created Template: {t1.name}")

        # Template 2: Breaking News
        t2_path = os.path.join(settings.MEDIA_ROOT, 'templates', 'posters', 'template_02.png')
        if os.path.exists(t2_path):
            t2, created = PosterTemplate.objects.get_or_create(name="Breaking News")
            t2.background_image.name = 'templates/posters/template_02.png'
            
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
            print(f"Created Template: {t2.name}")

if __name__ == "__main__":
    pass
