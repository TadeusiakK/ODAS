from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='blank'),
    path('login/', views.login_user, name='login'),
    path('home/', views.home, name='home'),
    path('info/', views.info, name='info'),
    path('transfer/', views.transfer, name='transfer'),
    path('settings/', views.settings, name='settings'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout, name='logout'),
]