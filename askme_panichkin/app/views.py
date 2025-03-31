from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import random


# Генерация тестовых данных
def generate_questions(count=30):
    tags = ['python', 'css', 'html', 'javascript', 'bootstrap', 'sql']
    questions = []
    for i in range(1, count + 1):
        questions.append({
            'title': f'Question title {i}',
            'id': i,
            'text': f'This is detailed text for question #{i}. ' * 5,
            'rating': random.randint(0, 100),
            'answers_count': random.randint(0, 15),
            'img_path': 'img/image.jpg',
            'tags': random.sample(tags, k=random.randint(1, 3))
        })
    return questions


def generate_answers(count=3):
    answers = []
    for i in range(1, count + 1):
        answers.append({
            'text': f'This is answer #{i}. ' * 10,
            'rating': random.randint(-5, 20),
            'is_correct': random.choice([True, False]),
            'author': f'user{random.randint(1, 100)}'
        })
    return answers


QUESTIONS = generate_questions()
HOT_QUESTIONS = sorted(QUESTIONS, key=lambda x: x['rating'], reverse=True)


# Основные view-функции
def index(request):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(QUESTIONS, 5)
    page = paginator.get_page(page_num)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def hot(request):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(HOT_QUESTIONS, 5)
    page = paginator.get_page(page_num)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def question(request, question_id):
    question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not question:
        return render(request, '404.html', status=404)

    # Добавляем ответы к вопросу
    question['answers'] = generate_answers(random.randint(1, 5))

    return render(request, 'single_question.html', {
        'question': question
    })


def tag(request, tag_name):
    tagged_questions = [q for q in QUESTIONS if tag_name in q['tags']]
    page_num = request.GET.get('page', 1)
    paginator = Paginator(tagged_questions, 5)
    page = paginator.get_page(page_num)
    return render(request, 'tag.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tag_name': tag_name
    })


# Авторизация
def login_view(request):
    error = None
    if request.method == 'POST':
        error = "Wrong password!"
        return render(request, 'login.html', {'error': error})
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        error = "This email is already registered!"
        return render(request, 'signup.html', {'error': error})
    return render(request, 'signup.html')


# Создание вопроса
def ask(request):
    if request.method == 'POST':
        # Создаем новый вопрос-заглушку
        new_id = len(QUESTIONS) + 1
        new_question = {
            'title': request.POST.get('title', 'New Question'),
            'id': new_id,
            'text': request.POST.get('text', 'Question text'),
            'rating': 0,
            'answers_count': 0,
            'img_path': 'img/image.jpg',
            'tags': ['new', 'question']
        }
        QUESTIONS.append(new_question)
        return redirect('question', question_id=new_id)
    return render(request, 'ask.html')


# Обработка ответов
def add_answer(request, question_id):
    if request.method == 'POST':
        question = next((q for q in QUESTIONS if q['id'] == question_id), None)
        if question:
            new_answer = {
                'text': request.POST.get('answer_text', ''),
                'rating': 0,
                'is_correct': False,
                'author': 'current_user'
            }
            if 'answers' not in question:
                question['answers'] = []
            question['answers'].append(new_answer)
            question['answers_count'] = len(question['answers'])
        return redirect('question', question_id=question_id)
    return redirect('index')

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    return paginator.get_page(page_number)