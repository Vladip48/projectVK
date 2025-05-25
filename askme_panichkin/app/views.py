from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .models import Question, Answer, Tag, QuestionLike, AnswerLike, Profile
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from .forms import LoginForm, SignUpForm, ProfileEditForm, QuestionForm, AnswerForm
from django.http import JsonResponse

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

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            return redirect(reverse('question', kwargs={'question_id': question.id}) + f'#answer-{answer.id}')
    else:
        form = AnswerForm()

    return render(request, 'single_question.html', {
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
        'form': form
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
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('index'))


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            tags = form.cleaned_data['tags'].split(',')
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(title=tag_name)
                    question.tags.add(tag)

            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm()
    return render(request, 'ask.html', {'form': form})


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            if form.cleaned_data.get('new_password'):
                update_session_auth_hash(request, request.user)

            return redirect('profile_edit')
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'profile_edit.html', {'form': form})

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
        question=question,
        defaults={'is_like': True}
    )

    if not created:
        if like.is_like:
            like.delete()
        else:
            like.is_like = True
            like.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'likes': question.like_count(),
            'dislikes': question.dislike_count()
        })
    return redirect('question', question_id=question_id)


@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer,
        defaults={'is_like': True}
    )

    if not created:
        if like.is_like:
            like.delete()
        else:
            like.is_like = True
            like.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'likes': answer.like_count(),
            'dislikes': answer.dislike_count()
        })
    return redirect('question', question_id=answer.question.id)


@login_required
def dislike_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'is_like': False}
    )

    if not created:
        if not like.is_like:
            like.delete()
        else:
            like.is_like = False
            like.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'likes': question.like_count(),
            'dislikes': question.dislike_count()
        })
    return redirect('question', question_id=question_id)


@login_required
def dislike_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer,
        defaults={'is_like': False}
    )

    if not created:
        if not like.is_like:
            like.delete()
        else:
            like.is_like = False
            like.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'likes': answer.like_count(),
            'dislikes': answer.dislike_count()
        })
    return redirect('question', question_id=answer.question.id)


@login_required
def mark_answer_helpful(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    if request.user == answer.question.author:
        helpful = answer.toggle_helpful()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'helpful': helpful
            })

    return redirect('question', question_id=answer.question.id)