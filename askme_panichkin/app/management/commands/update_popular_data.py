from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from questions.models import Tag, Question, Answer
from users.models import User
from datetime import timedelta


class Command(BaseCommand):
    help = 'Update popular tags and best users cache'

    def handle(self, *args, **options):
        three_months_ago = timezone.now() - timedelta(days=90)
        popular_tags = Tag.objects.filter(
            questions__created_at__gte=three_months_ago
        ).annotate(
            num_questions=Count('questions')
        ).order_by('-num_questions')[:10]

        cache.set('popular_tags', list(popular_tags), 3600)

        one_week_ago = timezone.now() - timedelta(days=7)

        top_question_authors = User.objects.filter(
            questions__votes__created_at__gte=one_week_ago
        ).annotate(
            total_votes=Count('questions__votes')
        ).order_by('-total_votes')[:5]

        top_answer_authors = User.objects.filter(
            answers__votes__created_at__gte=one_week_ago
        ).annotate(
            total_votes=Count('answers__votes')
        ).order_by('-total_votes')[:5]

        best_users = list(top_question_authors) + list(top_answer_authors)
        best_users = sorted(
            best_users,
            key=lambda u: getattr(u, 'total_votes', 0),
            reverse=True
        )[:10]

        cache.set('best_users', best_users, 3600)

        self.stdout.write(self.style.SUCCESS('Successfully updated cache'))