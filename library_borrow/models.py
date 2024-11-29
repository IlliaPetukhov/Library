from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    COVER_CHOICES = [
        ("HARD", "Hard"),
        ("SOFT", "Soft"),
    ]
    cover = models.CharField(
        max_length=100,
        choices=COVER_CHOICES,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField()

    def __str__(self):
        return f"{self.title}, {self.author}, {self.daily_fee}"

class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.book}, {self.user}, {self.actual_return_date}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ]
    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine"),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=100)
    type = models.CharField(choices=TYPE_CHOICES, max_length=100)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField()
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField()
    def __str__(self):
        return f"{self.status}, {self.type}, {self.borrowing}, {self.session_id}"


