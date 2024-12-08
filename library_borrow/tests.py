import sys
from django.contrib.auth import get_user_model
import datetime
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from library_borrow.models import *
from library_borrow.serializers import BookSerializer

BOOK_LIST_URL = "/library-api-1/books/"
BORROW_LIST_URL = "/library-api-1/borrowings/"
PAYMENT_LIST_URL = "/library-api-1/payments/"

class AllModelsForUnauthorizedUsers(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_books(self):
        response = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_borrowings(self):
        response = self.client.get(BORROW_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payments(self):
        response = self.client.get(PAYMENT_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AllModelsForAuthorizedUsers(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="<PASSWORD>", email="emain@gmail.com")
        self.client.force_authenticate(user=self.user)

        self.book_1 = Book.objects.create(
            title="Book 1",
            author="me",
            cover="HARD",
            inventory=3,
            daily_fee=3.12)
        self.book_2 = Book.objects.create(
            title="Book 2",
            author="me2",
            cover="HARD",
            inventory=2,
            daily_fee=3.13)

        self.borrowing_1 = Borrowing.objects.create(
            expected_return_date=datetime.date.today(),
            book=self.book_1,
            user=self.user,
            is_active=True
        )
        self.borrowing_2 = Borrowing.objects.create(
            expected_return_date=datetime.date.today(),
            book=self.book_2,
            user=self.user,
            is_active=False
        )

        self.payment_1 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing_1,
            session_url="https://checkout.stripe.com/c/pay/cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV#fidkdWxOYHwnPyd1blpxYHZxWjA0VFdmVz1MaExhYFNfSz13bUlrTzAyYDxnPWw3dEJiVExOfWFJQERkU39ScWo2dzBJbVRkYlx%2FYnB0bk5PMUdXMXRMQTU2cTFAMUN8R3xsSVBLQkhqaHZyNTVfbHRLMWZ%2FQCcpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
            session_id="cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV",
            money_to_pay=30.12
        )
        self.payment_2 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing_2,
            session_url="https://checkout.stripe.com/c/pay/cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV#fidkdWxOYHwnPyd1blpxYHZxWjA0VFdmVz1MaExhYFNfSz13bUlrTzAyYDxnPWw3dEJiVExOfWFJQERkU39ScWo2dzBJbVRkYlx%2FYnB0bk5PMUdXMXRMQTU2cTFAMUN8R3xsSVBLQkhqaHZyNTVfbHRLMWZ%2FQCcpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
            session_id="cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV",
            money_to_pay=30.12
        )

    def test_book(self):
        response = self.client.get(BOOK_LIST_URL)
        serializer_1 = BookSerializer(self.book_1)
        serializer_2 = BookSerializer(self.book_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_1.data["title"], self.book_1.title)
        self.assertEqual(serializer_2.data["title"], self.book_2.title)
        self.assertNotEqual(serializer_2.data["title"], self.book_1.title)

    def test_borrowing(self):
        response = self.client.get(BORROW_LIST_URL)
        serializer_1 = BookSerializer(self.borrowing_1)
        serializer_2 = BookSerializer(self.borrowing_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
