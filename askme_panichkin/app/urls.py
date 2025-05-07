from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/like/', views.like_question, name='like_question'),
    path('answer/<int:answer_id>/like/', views.like_answer, name='like_answer'),
    path('question/<int:question_id>/add_answer/', views.add_answer, name='add_answer'),
    path('question/<int:question_id>/dislike/', views.dislike_question, name='dislike_question'),
    path('answer/<int:answer_id>/dislike/', views.dislike_answer, name='dislike_answer'),
    path('answer/<int:answer_id>/mark_helpful/', views.mark_answer_helpful, name='mark_answer_helpful'),
]