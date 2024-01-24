from django import forms
from django.core.exceptions import ValidationError
from .models import Transfer

class UserLoginForm(forms.Form):
    login = forms.CharField(max_length=50, label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Hasło')

    def clean_login(self):
        login = self.cleaned_data.get('login')
        return login

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password

class UserRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50, label='Imię')
    last_name = forms.CharField(max_length=50, label='Nazwisko')
    login = forms.CharField(max_length=50, label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Hasło')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Potwierdź hasło')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        return last_name

    def clean_login(self):
        login = self.cleaned_data.get('login')
        return login

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        return confirm_password


class TransferForm(forms.ModelForm):
    receiver_account_number = forms.CharField(max_length=32, label='Konto odbiorcy', widget=forms.TextInput(attrs={'style': 'width: 300px;'}))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Kwota')

    class Meta:
        model = Transfer
        fields = ['amount', 'receiver_account_number']

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Stare Hasło')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Nowe Hasło')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Potwierdź nowe hasło')

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        return new_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        return confirm_password

