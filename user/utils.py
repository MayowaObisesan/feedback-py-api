from hashlib import blake2b
from hmac import compare_digest

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .models import User


class RegistrationCode:
    """
    The object that signs and verifies Registration codes
    Gotten from Python official doc. - hashlib documentation - May 19, 2023.
    """
    @staticmethod
    def sign(raw_data: str, enc_key: str):
        """ Sign the raw data """
        h = blake2b(digest_size=settings.DIGEST_SIZE, key=bytes(str(enc_key), "utf-8"))
        h.update(raw_data.encode("utf-8"))
        return h.hexdigest()

    @classmethod
    def verify(cls, raw_data: str, enc_key: str, signed_data: str):
        """ Verify the signed raw_data """
        good_signed = cls.sign(raw_data, enc_key)
        return compare_digest(good_signed, signed_data)
    pass


def generate_and_send_email_code(user_obj: User, email_type: str = "CREATE"):
    from .tasks import send_new_user_email, send_reset_email

    # Generate the code to send to the user
    # user_reg_code = get_random_string(7)
    user_reg_code = RegistrationCode().sign(
        user_obj.email+str(user_obj.last_resend_code_datetime), user_obj.eid
    )

    email_data: dict = {
        "code": user_reg_code.upper(),
        "email": user_obj.email,
        "firstname": user_obj.firstname,
        "lastname": user_obj.lastname
    }

    if email_type == "CREATE":
        send_new_user_email(email_data)
    elif email_type == "RESET":
        send_reset_email(email_data)
    return user_reg_code


def send_email(subject, recipient, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_DEFAULT_FROM, [recipient])
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)
