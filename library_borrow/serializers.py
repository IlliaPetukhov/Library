from rest_framework import serializers
from library_borrow.models import *
from user.serializers import UserSerializer


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

class BorrowingSerializerGet(serializers.ModelSerializer):
    book = BookSerializer()
    user = UserSerializer()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active"
        ]

class BorrowingSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "expected_return_date",
            "book",
        ]

class BorrowingSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "actual_return_date",
            "book",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

