from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.conf import settings

class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created')

    def hot(self):
        return self.annotate(likes_=Count('likes')).order_by('-likes_')

    def tagged(self, tag_title):
        print('got')
        return self.filter(tags__title=tag_title).order_by('-created')

    def all(self):
        return super().all()


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', related_name='question_tags')
    objects = QuestionManager()

    def __str__(self):
        return self.title

    def answer_count(self):
        return self.answer_question.count()

    def like_count(self):
        return self.likes.filter(is_like=True).count()

    def dislike_count(self):
        return self.likes.filter(is_like=False).count()

    def get_absolute_url(self):
        return reverse('AskMe:question_detail', args=[self.id])

    class Meta:
        db_table = 'question'


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


class AnswerManager(models.Manager):
    def get_answers(self, question):
        return self.filter(question=question).order_by('-created')


class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_question')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    helpful = models.BooleanField(default=False)

    objects = AnswerManager()

    def toggle_helpful(self):
        self.helpful = not self.helpful
        self.save()
        return self.helpful

    def __str__(self):
        return f'Answer to {self.question.title} {self.author.username}'

    def like_count(self):
        return self.likes.filter(is_like=True).count()

    def dislike_count(self):
        return self.likes.filter(is_like=False).count()

    class Meta:
        db_table = 'answer'



class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True)  # True for like, False for dislike
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')


class TagManager(models.Manager):
    def popular(self):
        return self.annotate(questions_=Count('question_tags')).order_by('-questions_')[:20]


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True)
    objects = TagManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tag'



class ProfileManager(models.Manager):
    def top_users(self):
        return self.select_related('user').annotate(answer_cnt=Count('user__answers')).order_by('-answer_cnt')[:10]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    objects = ProfileManager()

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'profile'
