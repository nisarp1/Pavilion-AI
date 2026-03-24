
import os
import django
import sys
from pathlib import Path

# Setup Django Path
BASE_DIR = Path(__file__).resolve().parent / 'backend'
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pavilion_gemini.settings')
django.setup()

from rss_fetcher.tasks import _fetch_articles_for_topic_task

print("Testing fetch for 'India Cricket'...")
try:
    result = _fetch_articles_for_topic_task('India Cricket')
    print(f"Result: {result}")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
