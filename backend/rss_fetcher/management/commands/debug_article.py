from django.core.management.base import BaseCommand
from workers.tasks import _generate_article_task_impl
import traceback

class Command(BaseCommand):
    help = 'Debug article generation for a specific ID'

    def add_arguments(self, parser):
        parser.add_argument('article_id', type=int)

    def handle(self, *args, **options):
        article_id = options['article_id']
        self.stdout.write(f"Debugging generation for Article {article_id}...")
        try:
            result = _generate_article_task_impl(article_id)
            self.stdout.write(self.style.SUCCESS(f"Result: {result}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"CRASH: {str(e)}"))
            self.stdout.write(traceback.format_exc())
