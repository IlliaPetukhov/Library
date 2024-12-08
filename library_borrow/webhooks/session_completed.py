from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import stripe

from library_borrow.models import Payment

stripe.api_key = "sk_test_51QRcR8ImIdeVZN8rcgPhiY7ghbX1U2l3p4SRfOhm9wk7hfqg68NxHzRH9LxdX0RATDKUnjEWtgz3OS2rd67aT74h00aDptRPBD"
endpoint_secret = (
    "whsec_020bd9f416bc4ffd4a65b588d0f62753e634aa720e50e3e1a58315d989cb94ea"
)
SUPPORTED_EVENTS = [
    "checkout.session.completed",
    "checkout.session.expired",
]


class SessionCompletedAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            if event["type"] not in SUPPORTED_EVENTS:
                return Response({"message": "Event ignored"}, status=200)
        except ValueError:
            return Response({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Invalid signature"}, status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session["id"]
            try:
                payment = Payment.objects.get(session_id=session_id)
                payment.status = "PAID"
                if payment.type == "FINE":
                    payment.type = "PAYMENT"
                payment.money_to_pay = 0.0
                payment.save()
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found"}, status=404)

        elif event["type"] == "checkout.session.expired":
            session_not_active = event["data"]["object"]
            session_id_not_active = session_not_active["id"]
            try:
                payment_not_active = Payment.objects.get(
                    session_id=session_id_not_active
                )
                payment_not_active.delete()
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found"}, status=404)

        return Response({"status": "success"}, status=200)
