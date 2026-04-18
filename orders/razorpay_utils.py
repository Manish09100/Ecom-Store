import razorpay
from django.conf import settings


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount, currency='INR', receipt=None):
    client = get_razorpay_client()
    data = {
        'amount': int(amount * 100),  # Razorpay expects amount in paise
        'currency': currency,
        'receipt': receipt or '',
    }
    return client.order.create(data=data)


def verify_razorpay_signature(payment_data):
    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature(payment_data)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
