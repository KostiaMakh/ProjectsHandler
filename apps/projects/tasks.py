from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

from ecopol.celery import app
from django.template import loader


@app.task
def send_report(subject, message):
    """
    summary: send report with trading errors
    """
    html = loader.render_to_string('mails/mail.html', {
        'message': message
    })
    send_mail(
        subject=subject,
        message=strip_tags(html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['kostiamakh@gmail.com', ],
        fail_silently=False,
        html_message=html
    )
