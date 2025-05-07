from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Question, Answer, Tag, QuestionLike, AnswerLike
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import login
from app.models import Profile


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    return paginator.get_page(page_number)


def index(request):
    questions = Question.objects.new().annotate(
        answers_count=Count('answer_question')
    )
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page
    })



def hot(request):
    questions = Question.objects.hot().annotate(
        answers_count=Count('answer_question')
    )
    page = paginate(questions, request, 5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def question(request, question_id):
    question = get_object_or_404(
        Question.objects.annotate(
            answers_count=Count('answer_question')
        ).prefetch_related('tags'),
        pk=question_id
    )
    answers = question.answer_question.all().order_by('-created')
    page = paginate(answers, request, 3)

    return render(request, 'single_question.html', {
        'question': question,
        'answers': page.object_list,
        'page_obj': page
    })


def tag(request, tag_name):
    tag = get_object_or_404(Tag, title=tag_name)
    questions = Question.objects.tagged(tag_name).annotate(
        answers_count=Count('answer_question')
    )
    page = paginate(questions, request, 5)
    return render(request, 'tag.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tag_name': tag_name
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        profile = Profile(user=user)

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()
        login(request, user)
        return redirect('index')

    return render(request, 'signup.html')


@login_required
def ask(request):
    if request.method == 'POST':
        question = Question.objects.create(
            title=request.POST.get('title', 'New Question'),
            content=request.POST.get('text', 'Question text'),
            author=request.user
        )
        tags = request.POST.get('tags', '').split()
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(title=tag_name)
            question.tags.add(tag)
        return redirect('question', question_id=question.id)
    return render(request, 'ask.html')


@login_required
def add_answer(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=question_id)
        Answer.objects.create(
            content=request.POST.get('answer_text', ''),
            author=request.user,
            question=question
        )
        return redirect('question', question_id=question_id)
    return redirect('index')


@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question
    )
    if not created:
        like.delete()
    return redirect('question', question_id=question_id)


@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer
    )
    if not created:
        like.delete()
    return redirect('question', question_id=answer.question.id)

@login_required
def dislike_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'is_like': False}
    )
    if not created:
        like.is_like = not like.is_like
        like.save()
    return redirect('question', question_id=question_id)

@login_required
def dislike_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer,
        defaults={'is_like': False}
    )
    if not created:
        like.is_like = not like.is_like
        like.save()
    return redirect('question', question_id=answer.question.id)


@login_required
def mark_answer_helpful(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    if request.user == answer.question.author:
        answer.toggle_helpful()

    return redirect('question', question_id=answer.question.id)