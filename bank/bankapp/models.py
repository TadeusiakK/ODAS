from django.db import models
import bcrypt
import uuid
from django.utils import timezone

class UserProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=60)
    account_number = models.CharField(max_length=32, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.login

    def set_password(self, raw_password):
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def generate_unique_account_number(self):
        if not self.account_number:
            self.account_number = uuid.uuid4().hex[:32]

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = uuid.uuid4().hex[:32]
        super().save(*args, **kwargs)


class Transfer(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transfers_sent')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transfers_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transfer_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Transfer from {self.sender.login} to {self.recipient.login}'