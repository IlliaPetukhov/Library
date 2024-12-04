import os
from unicodedata import decimal

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

stripe.api_key = settings.STRIPE_SECRET_KEY


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        expected_return_date = serializer.validated_data["expected_return_date"]
        user = serializer.validated_data["user"]

        borrowing = serializer.save()

        borrow_date = borrowing.borrow_date
        total_borrowed_days = (expected_return_date - borrow_date).days
        money_to_pay = int(total_borrowed_days) * book.daily_fee

        try:
            stripe.api_key = "sk_test_51QRcR8ImIdeVZN8rcgPhiY7ghbX1U2l3p4SRfOhm9wk7hfqg68NxHzRH9LxdX0RATDKUnjEWtgz3OS2rd67aT74h00aDptRPBD"
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
                success_url="http://127.0.0.1:8000/success/",
                cancel_url="http://127.0.0.1:8000/cancel/",
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




class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer