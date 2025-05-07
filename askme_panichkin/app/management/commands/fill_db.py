import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = 'Fills the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio for filling the database')

    def create_username(self, i):
        return f'user_{i}_{random.randint(1000, 9999)}'

    def create_email(self, i):
        return f'user_{i}_{random.randint(1000, 9999)}@example.com'

    def create_question_title(self, i):
        return f'Question {i}: {random.choice(["How to", "Why does", "What is"])} {random.choice(["Python", "Django", "Database"])}'

    def create_question_content(self, i):
        return f"Detailed content for question {i}. " * 5

    def create_answer_content(self, i):
        return f"Comprehensive answer {i} explaining the solution. " * 5

    def create_users(self):
        users = []
        for i in range(1, self.ratio + 1):
            username = self.create_username(i)
            email = self.create_email(i)
            if not User.objects.filter(username=username).exists():
                users.append(User(username=username, email=email, password='password'))

        User.objects.bulk_create(users)
        return User.objects.all()

    def create_profiles(self, users):
        profiles = []
        for user in users:
            if not Profile.objects.filter(user=user).exists():
                profiles.append(Profile(
                    user=user,
                    avatar=None
                ))
        Profile.objects.bulk_create(profiles)

    def create_tags(self):
        tags = []
        for i in range(1, self.ratio + 1):
            tag_name = f'tag_{i}_{random.randint(100, 999)}'
            if not Tag.objects.filter(title=tag_name).exists():
                tags.append(Tag(title=tag_name))
        Tag.objects.bulk_create(tags)
        return Tag.objects.all()

    def create_questions(self, users):
        questions = []
        for i in range(1, self.ratio * 10 + 1):
            questions.append(Question(
                title=self.create_question_title(i),
                content=self.create_question_content(i),
                author=random.choice(users)
            ))
        Question.objects.bulk_create(questions)
        return Question.objects.all()

    def create_answers(self, questions, users):
        answers = []
        for i in range(1, self.ratio * 100 + 1):
            answers.append(Answer(
                content=self.create_answer_content(i),
                author=random.choice(users),
                question=random.choice(questions),
                helpful=random.random() > 0.9
            ))
        Answer.objects.bulk_create(answers)
        return Answer.objects.all()

    def create_question_likes(self, questions, users):
        existing_pairs = set(QuestionLike.objects.values_list('user_id', 'question_id'))
        new_likes = []
        attempts = 0
        max_attempts = self.ratio * 100 * 2

        while len(new_likes) < self.ratio * 100 and attempts < max_attempts:
            user = random.choice(users)
            question = random.choice(questions)
            if (user.id, question.id) not in existing_pairs:
                new_likes.append(QuestionLike(user=user, question=question))
                existing_pairs.add((user.id, question.id))
            attempts += 1

        QuestionLike.objects.bulk_create(new_likes)

    def create_answer_likes(self, answers, users):
        existing_pairs = set(AnswerLike.objects.values_list('user_id', 'answer_id'))
        new_likes = []
        attempts = 0
        max_attempts = self.ratio * 100 * 2

        while len(new_likes) < self.ratio * 100 and attempts < max_attempts:
            user = random.choice(users)
            answer = random.choice(answers)
            if (user.id, answer.id) not in existing_pairs:
                new_likes.append(AnswerLike(user=user, answer=answer))
                existing_pairs.add((user.id, answer.id))
            attempts += 1

        AnswerLike.objects.bulk_create(new_likes)

    def handle(self, *args, **options):
        self.ratio = options['ratio']
        self.stdout.write('Starting to fill the database...')

        with transaction.atomic():
            users = list(self.create_users())
            self.create_profiles(users)

            tags = list(self.create_tags())

            questions = list(self.create_questions(users))
            for question in questions:
                selected_tags = random.sample(tags, k=random.randint(1, 5))
                question.tags.add(*selected_tags)

            answers = list(self.create_answers(questions, users))

            self.create_question_likes(questions, users)
            self.create_answer_likes(answers, users)

        self.stdout.write(self.style.SUCCESS(f'Successfully filled database with ratio {self.ratio}'))