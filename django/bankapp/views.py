from decimal import Decimal
import json
import re
import bcrypt
from django.core.cache import cache
from django.shortcuts import redirect, render
from .models import User, Transfer
from .forms import UserLoginForm
from .forms import UserRegisterForm
from .forms import TransferForm
from .forms import ChangePasswordForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import UserLoginoLoginForm, UserLoginoPasswordForm
import random
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

@login_required
def home(request):
    user_info = {
        'first_name': request.user.first_name,
        'total_amount': request.user.total_amount,
    }
    return render(request, 'bankapp/home.html', {'user_info': user_info})

@login_required
def info(request):
    user_info = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'login': request.user.login,
        'password': request.user.password,
        'account_number': request.user.account_number,
        'total_amount': request.user.total_amount,
    }
    return render(request, 'bankapp/info.html', {'user_info': user_info})
    
def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    message = None

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user_login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            if not re.match(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+", user_login):
                message = 'Nieprawidłowy format adresu email.'
            elif len(password) < 8:
                message = 'Hasło musi mieć co najmniej 8 znaków.'
            elif password != confirm_password:
                message = 'Hasła nie zgadzają się.'
            else:
                try:
                    User.objects.get(login=user_login)
                    message = 'Konto o podanym loginie już istnieje.'
                except User.DoesNotExist:
                    user = User.objects.create_user(login=user_login, password=password, first_name=first_name, last_name=last_name)
                    login(request, user)
                    message = 'Rejestracja udana. Zostałeś zalogowany.'

                    return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'bankapp/register.html', {'form': form, 'message': message})

def transfer(request):
    message = None
    transactions = None

    if request.method == 'POST':
        form = TransferForm(request.POST)

        if form.is_valid():
            try:
                sender_profile = User.objects.get(account_number=request.user.account_number)
                receiver_account_number = form.cleaned_data['receiver_account_number']

                if receiver_account_number == request.user.account_number:
                    message = 'Nie możesz przelać środków na własne konto.'
                    return render(request, 'bankapp/transfer.html', {'form': form, 'message': message, 'transactions': transactions})

                receiver_profile = User.objects.get(account_number=receiver_account_number)
            except User.DoesNotExist:
                message = 'Podany numer konta nie istnieje.'
                return render(request, 'bankapp/transfer.html', {'form': form, 'message': message, 'transactions': transactions})

            amount = form.cleaned_data['amount']

            if amount <= 0:
                message = 'Wprowadź poprawną wartość przelewu.'
            elif sender_profile.total_amount >= amount:
                transfer = form.save(commit=False)
                transfer.sender = sender_profile
                transfer.recipient = receiver_profile
                transfer.save()

                sender_profile.total_amount -= amount
                receiver_profile.total_amount += amount
                request.user.total_amount -= Decimal(amount)
                sender_profile.save()
                receiver_profile.save()

                message = 'Pomyślnie przesłano środki.'
            else:
                message = 'Niewystarczająca ilość środków na koncie.'

    else:
        form = TransferForm()

    transactions = Transfer.objects.filter(sender__account_number=request.user.account_number)

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
                    user = User.objects.get(login=request.user.login)
                    if user.check_password(old_password):
                        user.set_password(new_password)
                        user.save()
                        login(request, user)
                        message = 'Hasło zostało pomyślnie zmienione.'
                    else:
                        message = 'Aktualne hasło jest nieprawidłowe.'
                except User.DoesNotExist:
                    message = 'Użytkownik o podanym loginie nie istnieje.'
        else:
            message = 'Nieprawidłowe dane zmiany hasła. Spróbuj ponownie.'
    else:
        form = ChangePasswordForm()

    return render(request, 'bankapp/settings.html', {'change_password_form': form, 'message': message})


def logino_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    message = None
    max_login_attempts = 5
    lockout_time = 60

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        ip_address = request.META.get('REMOTE_ADDR')
        locked_out_key = f'locked_out_{ip_address}'

        locked_out_time = cache.get(locked_out_key)

        if locked_out_time and locked_out_time > timezone.now():
            remaining_time = (locked_out_time - timezone.now()).seconds
            message = f'Zbyt wiele nieudanych prób. Spróbuj ponownie za {remaining_time} sekund.'
        else:
            if form.is_valid():
                user_login = form.cleaned_data['login']
                password = form.cleaned_data['password']

                if not re.match(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+", user_login):
                    message = 'Nieprawidłowy format adresu email.'
                else:
                    user = authenticate(request, login=user_login, password=password)
                    if user is not None:
                        login(request, user)
                        cache.delete(locked_out_key)
                        return redirect('home')
                    else:
                        cache_key = f'login_attempts_{ip_address}'
                        attempts = cache.get(cache_key, 0) + 1
                        cache.set(cache_key, attempts, timeout=lockout_time)

                        if attempts >= max_login_attempts:
                            lockout_time = timezone.now() + timedelta(seconds=lockout_time)
                            cache.set(locked_out_key, lockout_time, timeout=None)
                            message = f'Zbyt wiele nieudanych prób. Spróbuj ponownie za {lockout_time.second} sekund.'
                        else:
                            message = 'Nieprawidłowy email lub hasło.'
    else:
        form = UserLoginForm()

    return render(request, 'bankapp/logino.html', {'form': form, 'message': message})

def password_check_result(password, encoded_password_combination):
    decoded_password_combination = encoded_password_combination.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), decoded_password_combination)

combination_info = {'combination': '', 'password_combination': ''}

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    message = None
    max_login_attempts = 5
    lockout_time = 60
    global combination_info

    if request.method == 'POST':
        form_login = UserLoginoLoginForm(request.POST)
        form_password = UserLoginoPasswordForm(request.POST)

        form_action = request.POST.get('formAction')

        if form_action == 'view_info':
            if form_login.is_valid():
                user_login = form_login.cleaned_data['login']

                if not re.match(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+", user_login):
                    message = 'Nieprawidłowy format adresu email.'
                    form_login.add_error('login', message)
                    return render(request, 'bankapp/login.html', {'form_login': form_login, 'form_password': form_password, 'message': message})

                try:
                    user = User.objects.get(login=user_login)
                except User.DoesNotExist:
                    message = 'Użytkownik o podanym loginie nie istnieje.'
                    form_login.add_error('login', message)
                    return render(request, 'bankapp/login.html', {'form_login': form_login, 'form_password': form_password, 'message': message})

                combination_info_response = get_combination(request, user_login)
                combination_info = json.loads(combination_info_response.content)

        elif form_action == 'login':
            if form_login.is_valid() and form_password.is_valid():
                user_login = form_login.cleaned_data['login']
                user_password = form_password.cleaned_data['password']

                try:
                    user = User.objects.get(login=user_login)
                except User.DoesNotExist:
                    message = 'Użytkownik o podanym loginie nie istnieje.'
                    form_login.add_error('login', message)
                    return render(request, 'bankapp/login.html', {'form_login': form_login, 'form_password': form_password, 'message': message})

                encoded_password_combination = combination_info['password_combination']

                try:
                    if password_check_result(user_password, encoded_password_combination):
                        login(request, user)
                        combination_info = {'combination': '', 'password_combination': ''}
                        return redirect('home')
                    else:
                        message = 'Nieprawidłowe hasło.'
                        combination_info = {'combination': '', 'password_combination': ''}
                        return render(request, 'bankapp/login.html', {'form_login': form_login, 'form_password': form_password, 'message': message})
                except (UnicodeEncodeError, ValueError) as e:
                    message = 'Wystąpił błąd podczas sprawdzania hasła wygeneruj nową kombinację'
                    return render(request, 'bankapp/login.html', {'form_login': form_login, 'form_password': form_password, 'message': message})

        else:
            pass
    else:
        form_login = UserLoginoLoginForm()
        form_password = UserLoginoPasswordForm()

    return render(request, 'bankapp/login.html', {'form_login': form_login, 'form_password': form_password, 'message': message, 'combination_info': combination_info})


import random
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_combination(request, login):
    user = get_object_or_404(User, login=login)

    if user.combinations:
        random_combination_index = random.randint(0, len(user.combinations) - 1)
        combination = user.combinations[random_combination_index]
        password_combination = user.password_combinations[random_combination_index]
        return JsonResponse({'combination': combination, 'password_combination': password_combination})

    return JsonResponse({'combination': '','password_combination': ''})

