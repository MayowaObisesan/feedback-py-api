from django.template.loader import get_template


from feedback_api.celery import APP


@APP.task()
def send_new_user_email(email_data):
    from user.utils import send_email

    """ The background task that handles sending new user mail. """
    html_template = get_template("emails/new_user_email.html")
    text_template = get_template("emails/new_user_email.txt")
    html_alternative = html_template.render(email_data)
    text_alternative = text_template.render(email_data)
    send_email("New User", email_data.get("email"), html_alternative, text_alternative)


@APP.task()
def send_reset_email(email_data):
    from user.utils import send_email

    """ The background task that handles sending password reset mail. """
    html_template = get_template("emails/new_user_email.html")
    text_template = get_template("emails/new_user_email.txt")
    html_alternative = html_template.render(email_data)
    text_alternative = text_template.render(email_data)
    send_email("New User", email_data.get("email"), html_alternative, text_alternative)
