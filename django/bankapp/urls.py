from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logino/', views.logino_user, name='logino'),
    path('register/', views.register_user, name='register'),
    path('', views.home, name='home'),
    path('info/', views.info, name='info'),
    path('transfer/', views.transfer, name='transfer'),
    path('settings/', views.settings, name='settings'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]