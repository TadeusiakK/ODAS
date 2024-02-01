import itertools
import random
import bcrypt
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(UserManager):
    def _create_user(self, first_name, last_name, login, password, **extra_fields):
        if not first_name:
            raise ValueError('The First name field must be set')
        if not last_name:
            raise ValueError('The Last name field must be set')
        if not login:
            raise ValueError('The Login field must be set')

        login = self.normalize_email(login)
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            login=login,
            **extra_fields
        )
        user.set_password(password)
        user.generate_unique_account_number()
        user.save(using=self._db)
        return user
    
    def create_user(self, first_name=None, last_name=None, login=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(first_name, last_name, login, password, **extra_fields)

    def create_superuser(self, first_name, last_name, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(first_name, last_name, login, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, blank='', default='')
    last_name = models.CharField(max_length=50, blank='', default='')
    login = models.EmailField(blank=True, default='', unique=True)
    account_number = models.CharField(max_length=32, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    combinations = models.JSONField(default=list)
    password_combinations = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateField(default=timezone.now)
    last_login = models.DateField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'login'
    EMAIL_FIELD = 'login'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.generate_unique_account_number()
        super().save(*args, **kwargs)
    
    def generate_unique_account_number(self):
        if not self.account_number:
            self.account_number = ''.join(str(random.randint(0, 9)) for _ in range(32))

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name

    def set_password(self, raw_password):
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        all_combinations = generate_combinations(raw_password, 6, 1000000)
        selected_combinations = select_random_combinations(all_combinations, 20)

        print(selected_combinations)

        self.combinations = selected_combinations

        hashed_combinations = []
        for combination in selected_combinations:
            partial_password = ''.join(raw_password[i] for i in combination)
            print(partial_password)
            hashed_password = bcrypt.hashpw(partial_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(hashed_password)
            hashed_combinations.append(hashed_password)

        self.password_combinations = hashed_combinations

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    
class Transfer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transfers_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transfers_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transfer_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transfer from {self.sender.login} to {self.recipient.login}'
    

def generate_combinations(raw_password, length, count_limit):
    all_combinations = itertools.combinations(range(len(raw_password)), length)
    limited_combinations = itertools.islice(all_combinations, count_limit)
    return list(limited_combinations)

def select_random_combinations(combinations, count):
    return random.sample(combinations, min(count, len(combinations)))
