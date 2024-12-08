import os
from unicodedata import decimal
from urllib import request

from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter

from library_borrow.models import *
from library_borrow.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Book
import stripe

from .permissions import IsAdminOrReadOnly, ReadOnlyOrCreateIfAdmin

stripe.api_key = "sk_test_51QRcR8ImIdeVZN8rcgPhiY7ghbX1U2l3p4SRfOhm9wk7hfqg68NxHzRH9LxdX0RATDKUnjEWtgz3OS2rd67aT74h00aDptRPBD"


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrCreateIfAdmin]
    serializer_class = BookSerializer
    queryset = Book.objects.all()

class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        borrowing = Borrowing.objects.all()
        is_active_filter = self.request.query_params.get("is_active")

        if is_active_filter and is_active_filter.lower() == "true":
            borrowing = borrowing.filter(is_active=True)
        elif is_active_filter and is_active_filter.lower() == "false":
            borrowing = borrowing.filter(is_active=False)

        if self.request.user.is_staff:
            user_id_filter = self.request.query_params.get("user_id")
            if user_id_filter:
                try:
                    borrowing = borrowing.filter(user=int(user_id_filter))
                except Exception as e:
                    raise ValidationError(e)

        else:
            borrowing = borrowing.filter(user=self.request.user)

        return borrowing
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="The ID of the user to borrow",
            ),
            OpenApiParameter(
                name="is_active",
                description="Whether the user is active or not",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingSerializerGet
        elif self.request.method == "POST":
            return BorrowingSerializerPost
        return BorrowingSerializerUpdate


    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        expected_return_date = serializer.validated_data["expected_return_date"]

        borrowing = serializer.save(user=self.request.user)

        borrow_date = borrowing.borrow_date
        total_borrowed_days = (expected_return_date - borrow_date).days
        money_to_pay = int(total_borrowed_days) * book.daily_fee

        try:
            book = borrowing.book
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": book.title,
                            },
                            "unit_amount": int(money_to_pay * 100)
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url="http://localhost:8000/library-api-1/payments/",
                cancel_url="http://localhost:8000/library-api-1/payments/",
            )
            Payment.objects.create(
                status="PENDING",
                type="PAYMENT",
                borrowing=borrowing,
                session_url=session.url,
                session_id=session.id,
                money_to_pay=money_to_pay,
            )
            book.inventory = book.inventory - 1
            book.save()
            return Response({"session_url": session.url})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)


    def perform_update(self, serializer):
        borrowing = serializer.save()
        borrow = Borrowing.objects.get(id=borrowing.id)
        book = borrow.book
        expected_return_date = borrow.expected_return_date
        actual_return_date = borrow.actual_return_date

        if actual_return_date and borrow.is_active==True:
            book.inventory = book.inventory + 1
            borrow.is_active = False
            borrow.save()
            book.save()
        else:
            raise ValidationError({"error": "This book is already in the library."})
        total_fine_borrowed_days = (actual_return_date - expected_return_date).days

        if total_fine_borrowed_days > 0:
            fine_money_to_pay = total_fine_borrowed_days * book.daily_fee
            payments = Payment.objects.get(borrowing=borrowing)
            payments.status = "PENDING"
            payments.type = "FINE"
            payments.money_to_pay = fine_money_to_pay
            payments.save()

            try:
                book = borrowing.book
                session_fine = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": book.title,
                                },
                                "unit_amount": int(fine_money_to_pay * 100)
                            },
                            "quantity": 1,
                        },
                    ],
                    mode="payment",
                    success_url="http://localhost:8000/library-api-1/payments/",
                    cancel_url="http://localhost:8000/library-api-1/payments/",
                )
                payments.session_url = session_fine.url
                payments.session_id = session_fine.id
                payments.save()
                return Response({"session_url": session_fine.url})
            except stripe.error.StripeError as e:
                return Response({"error": str(e)}, status=400)





class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Payment.objects.filter(borrowing__user=self.request.user)
        return Payment.objects.all()