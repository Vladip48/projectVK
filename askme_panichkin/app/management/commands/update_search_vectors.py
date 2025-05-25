from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from questions.models import Question

class Command(BaseCommand):
    help = 'Update search vectors for questions'

    def handle(self, *args, **options):
        Question.objects.update(
            search_vector=SearchVector('title', 'content')
        )