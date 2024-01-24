from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import HttpResponse
from .models import UserProfile, Transfer
from .forms import UserLoginForm
from .forms import UserRegisterForm
from .forms import TransferForm
from .forms import ChangePasswordForm
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import re
import math
from zxcvbn import zxcvbn
from decimal import Decimal

user_profile_instance = UserProfile()


def home(request):
    user_info = {
        'first_name': user_profile_instance.first_name,
        'total_amount': user_profile_instance.total_amount,
    }
    return render(request, 'bankapp/home.html', {'user_info': user_info})

def info(request):
    user_info = {
        'first_name': user_profile_instance.first_name,
        'last_name': user_profile_instance.last_name,
        'login': user_profile_instance.login,
        'password': user_profile_instance.password,
        'account_number': user_profile_instance.account_number,
        'total_amount': user_profile_instance.total_amount,
    }
    return render(request, 'bankapp/info.html', {'user_info': user_info})

def transfer(request):
    message = None
    transactions = None

    if request.method == 'POST':
        form = TransferForm(request.POST)

        if form.is_valid():
            try:
                sender_profile = UserProfile.objects.get(account_number=user_profile_instance.account_number)
                receiver_account_number = form.cleaned_data['receiver_account_number']
                receiver_profile = UserProfile.objects.get(account_number=receiver_account_number)
            except UserProfile.DoesNotExist:
                message = 'Podany numer konta nie istnieje.'
                return render(request, 'bankapp/transfer.html', {'form': form, 'message': message, 'transactions': transactions})

            if sender_profile.total_amount >= form.cleaned_data['amount']:
                transfer = form.save(commit=False)
                transfer.sender = sender_profile
                transfer.recipient = receiver_profile
                transfer.save()

                sender_profile.total_amount -= form.cleaned_data['amount']
                receiver_profile.total_amount += form.cleaned_data['amount']
                user_profile_instance.total_amount -= Decimal(form.cleaned_data['amount'])
                sender_profile.save()
                receiver_profile.save()

                message = 'Pomyślnie przesłano środki.'
            else:
                message = 'Niewystarczająca ilość środków na koncie.'

    else:
        form = TransferForm()

    transactions = Transfer.objects.filter(sender__account_number=user_profile_instance.account_number)

    return render(request, 'bankapp/transfer.html', {'form': form, 'message': message, 'transactions': transactions})

def settings(request):
    message = None

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if len(new_password) < 8:
                message = 'Nowe hasło musi mieć co najmniej 8 znaków.'
            elif new_password != confirm_password:
                message = 'Nowe hasło i potwierdzenie hasła nie zgadzają się.'
            else:
                try:
                    user = UserProfile.objects.get(login=user_profile_instance.login)
                    if user.check_password(old_password):
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Hasło zostało pomyślnie zmienione.')
                        return redirect('settings')
                    else:
                        message = 'Aktualne hasło jest nieprawidłowe.'
                except UserProfile.DoesNotExist:
                    message = 'Użytkownik o podanym loginie nie istnieje.'
        else:
            message = 'Nieprawidłowe dane zmiany hasła. Spróbuj ponownie.'
    else:
        form = ChangePasswordForm()

    return render(request, 'bankapp/settings.html', {'change_password_form': form, 'message': message})



def logout(request):
    user_profile_instance = UserProfile()
    return redirect('login') 

def register_user(request):
    global user_profile_instance 
    message = None

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            if not re.match(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+", login):
                message = 'Nieprawidłowy format adresu email.'
            elif len(password) < 8:
                message = 'Hasło musi mieć co najmniej 8 znaków.'
            elif password != confirm_password:
                message = 'Hasła nie zgadzają się.'
            else:
                try:
                    UserProfile.objects.get(login=login)
                    message = 'Konto o podanym loginie już istnieje.'
                except UserProfile.DoesNotExist:
                    new_profile = UserProfile()
                    new_profile.first_name = first_name
                    new_profile.last_name = last_name
                    new_profile.login = login
                    new_profile.generate_unique_account_number()
                    new_profile.set_password(password)
                    new_profile.save()
                    user_profile_instance = new_profile
                    user_profile_instance.save()

                    message = 'Rejestracja udana. Możesz się teraz zalogować.'
                    print(user_profile_instance.first_name)
                    print(user_profile_instance.last_name)
                    print(user_profile_instance.account_number)

                    return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'bankapp/register.html', {'form': form, 'message': message})

def login_user(request):
    message = None
    max_login_attempts = 5
    lockout_time = 60

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        locked_out_key = f'locked_out_{request.POST.get("login")}'
        locked_out_time = cache.get(locked_out_key)

        if locked_out_time and locked_out_time > timezone.now():
            remaining_time = (locked_out_time - timezone.now()).seconds
            message = f'Zbyt wiele nieudanych prób. Spróbuj ponownie za {remaining_time} sekund.'
        else:
            if form.is_valid():
                login = form.cleaned_data['login']
                password = form.cleaned_data['password']

                if not re.match(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+", login):
                    message = 'Nieprawidłowy format adresu email.'
                else:
                    try:
                        user = UserProfile.objects.get(login=login)
                        if user.check_password(password):
                            user_profile_instance.first_name = user.first_name
                            user_profile_instance.last_name = user.last_name
                            user_profile_instance.login = user.login
                            user_profile_instance.password = user.password
                            user_profile_instance.account_number = user.account_number
                            user_profile_instance.total_amount = user.total_amount
                            message = 'Zalogowano pomyślnie!'
                            cache.delete(locked_out_key)
                            return redirect('home')
                        else:
                            cache_key = f'login_attempts_{login}'
                            attempts = cache.get(cache_key, 0) + 1
                            cache.set(cache_key, attempts, timeout=lockout_time)

                            if attempts >= max_login_attempts:
                                lockout_time = timezone.now() + timedelta(seconds=lockout_time)
                                cache.set(locked_out_key, lockout_time, timeout=None)
                                message = f'Zbyt wiele nieudanych prób. Spróbuj ponownie za {lockout_time.second} sekund.'
                            else:
                                message = 'Nieprawidłowy email lub hasło.'
                    except UserProfile.DoesNotExist:
                        message = 'Nieprawidłowy email lub hasło.'
    else:
        form = UserLoginForm()

    return render(request, 'bankapp/login.html', {'form': form, 'message': message})

