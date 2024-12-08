import datetime
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from library_borrow.models import *
from library_borrow.serializers import (
    BookSerializer,
    BorrowingSerializerGet,
    PaymentSerializer,
)

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
        self.user = User.objects.create_user(
            username="test", password="<PASSWORD>", email="emain@gmail.com"
        )
        self.user = User.objects.create_user(
            username="test2", password="<PASSWORD2>", email="emain2@gmail.com"
        )

        self.client.force_authenticate(user=self.user)

        self.book_1 = Book.objects.create(
            title="Book 1", author="me", cover="HARD", inventory=3, daily_fee=3.12
        )
        self.book_2 = Book.objects.create(
            title="Book 2", author="me2", cover="HARD", inventory=2, daily_fee=3.13
        )

        self.borrowing_1 = Borrowing.objects.create(
            expected_return_date=datetime.date.today(),
            book=self.book_1,
            user=self.user,
            is_active=True,
        )
        self.borrowing_2 = Borrowing.objects.create(
            expected_return_date=datetime.date.today(),
            book=self.book_2,
            user=self.user,
            is_active=False,
        )

        self.payment_1 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing_1,
            session_url="https://checkout.stripe.com/c/pay/cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV#fidkdWxOYHwnPyd1blpxYHZxWjA0VFdmVz1MaExhYFNfSz13bUlrTzAyYDxnPWw3dEJiVExOfWFJQERkU39ScWo2dzBJbVRkYlx%2FYnB0bk5PMUdXMXRMQTU2cTFAMUN8R3xsSVBLQkhqaHZyNTVfbHRLMWZ%2FQCcpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
            session_id="cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV",
            money_to_pay=30.12,
        )
        self.payment_2 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing_2,
            session_url="https://checkout.stripe.com/c/pay/cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV#fidkdWxOYHwnPyd1blpxYHZxWjA0VFdmVz1MaExhYFNfSz13bUlrTzAyYDxnPWw3dEJiVExOfWFJQERkU39ScWo2dzBJbVRkYlx%2FYnB0bk5PMUdXMXRMQTU2cTFAMUN8R3xsSVBLQkhqaHZyNTVfbHRLMWZ%2FQCcpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl",
            session_id="cs_test_a16jyOwXKSxwhWGvxPfGctGi5k7fJs3yERFWuNzmyvqQ0BRfRiENs1H3vV",
            money_to_pay=30.12,
        )

    def test_book(self):
        response = self.client.get(BOOK_LIST_URL)
        serializer_1 = BookSerializer(self.book_1)
        serializer_2 = BookSerializer(self.book_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_1.data["title"], self.book_1.title)
        self.assertEqual(serializer_2.data["title"], self.book_2.title)
        self.assertNotEqual(serializer_2.data["title"], self.book_1.title)

    def test_post_book(self):
        response = self.client.post(
            BOOK_LIST_URL,
            data={
                "title": self.book_1.title,
                "author": self.book_1.author,
                "cover": self.book_1.cover,
                "inventory": self.book_1.inventory,
                "daily_fee": self.book_1.daily_fee,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrowing(self):
        response = self.client.get(BORROW_LIST_URL)
        serializer_1 = BorrowingSerializerGet(self.borrowing_1)
        serializer_2 = BorrowingSerializerGet(self.borrowing_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_1.data, response.data[0])
        self.assertEqual(serializer_2.data, response.data[1])
        self.assertNotEqual(serializer_1.data, response.data[1])

    def test_post_borrowing(self):
        response = self.client.post(
            BORROW_LIST_URL,
            data={
                "expected_return_date": self.borrowing_1.expected_return_date,
                "book": self.book_1.id,
                "user": self.user.id,
                "is_active": self.borrowing_1.is_active,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_borrowing_filter_by_is_active(self):
        response = self.client.get(BORROW_LIST_URL + f"?is_active=true")
        serializer_1 = BorrowingSerializerGet(self.borrowing_1)
        serializer_2 = BorrowingSerializerGet(self.borrowing_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)

    def test_borrowinguser_id_filter_if_not_admin(self):
        response = self.client.get(BORROW_LIST_URL + f"?user_id=999")
        self.assertNotEqual(len(response.data), 0)

    def test_payment(self):
        response = self.client.get(PAYMENT_LIST_URL)
        serializer_1 = PaymentSerializer(self.payment_1)
        serializer_2 = PaymentSerializer(self.payment_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_1.data, response.data[0])
        self.assertEqual(serializer_2.data, response.data[1])
        self.assertNotEqual(serializer_1.data, response.data[1])

    def test_post_payment(self):
        response = self.client.post(
            PAYMENT_LIST_URL,
            data={
                "status": self.payment_1.status,
                "type": self.payment_1.type,
                "borrowing": self.payment_1.borrowing.id,
                "session_url": self.payment_1.session_url,
                "session_id": self.payment_1.session_id,
                "money_to_pay": self.payment_1.money_to_pay,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
