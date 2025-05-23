from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask')
]