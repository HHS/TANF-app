from django.core.mail import send_mail, send_mass_mail
from celery import shared_task
from django.conf import settings


@shared_task
def send_email(subject, message, sender, recipient_list):
    send_mail(
        subject,
        message,
        sender,
        recipient_list,
        fail_silently=False,
    )

@shared_task
def send_mass_email(subject, message, sender, recipient_list):
    send_mass_mail(
        subject,
        message,
        sender,
        recipient_list,
        fail_silently=False,
    )
