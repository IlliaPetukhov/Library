import os
from unicodedata import decimal
from urllib import request

from django.shortcuts import render
from rest_framework import viewsets


from library_borrow.models import *
from library_borrow.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Book
import stripe

stripe.api_key = "sk_test_51QRcR8ImIdeVZN8rcgPhiY7ghbX1U2l3p4SRfOhm9wk7hfqg68NxHzRH9LxdX0RATDKUnjEWtgz3OS2rd67aT74h00aDptRPBD"


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingSerializerGet
        return BorrowingSerializerPost

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
            return Response({"session_url": session.url})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)


    def perform_update(self, serializer):
        expected_return_date = serializer.validated_data["expected_return_date"]
        actual_return_date = serializer.validated_data["actual_return_date"]
        borrowing = serializer.save()
        total_fine_borrowed_days = (actual_return_date - expected_return_date).days

        if total_fine_borrowed_days != 0:
            book = serializer.validated_data["book"]
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
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer