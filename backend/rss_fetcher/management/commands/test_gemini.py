from django.core.management.base import BaseCommand
import google.generativeai as genai
from django.conf import settings

class Command(BaseCommand):
    help = 'Test Gemini API connection'

    def handle(self, *args, **options):
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.stdout.write(f"Checking API Key: {'Found' if api_key else 'Missing'}")
        
        if not api_key:
            self.stdout.write(self.style.ERROR("GEMINI_API_KEY is not set!"))
            return

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            self.stdout.write("Sending test request to Gemini...")
            response = model.generate_content("Say 'Hello from Railway!'")
            self.stdout.write(self.style.SUCCESS(f"Success! Response: {response.text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Gemini Error: {str(e)}"))
