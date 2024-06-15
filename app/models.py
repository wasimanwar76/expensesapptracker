from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class MonthlyEarning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"{self.user.username} - {self.month}: ${self.amount}"
    
    
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Housing', 'Housing'),
        ('Transportation', 'Transportation'),
        ('Food', 'Food'),
        ('Utilities', 'Utilities'),
        ('Medical & Healthcare', 'Medical & Healthcare'),
        ('Saving, Investing, & Debt Payments', 'Saving, Investing, & Debt Payments'),
        ('Personal Spending', 'Personal Spending'),
        ('Recreation & Entertainment', 'Recreation & Entertainment'),
        ('Miscellaneous', 'Miscellaneous'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateField()


