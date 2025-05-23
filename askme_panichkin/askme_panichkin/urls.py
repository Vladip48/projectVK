"""
URL configuration for askme_panichkin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),

    path('question/<int:question_id>/like/', views.like_question, name='like_question'),
    path('question/<int:question_id>/dislike/', views.dislike_question, name='dislike_question'),
    path('answer/<int:answer_id>/like/', views.like_answer, name='like_answer'),
    path('answer/<int:answer_id>/dislike/', views.dislike_answer, name='dislike_answer'),
    path('answer/<int:answer_id>/mark-helpful/', views.mark_answer_helpful, name='mark_answer_helpful'),
    path('question/<int:question_id>/answer/', views.add_answer, name='add_answer'),
]
