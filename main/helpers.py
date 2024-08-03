import ast
from celery import shared_task
from .models import Submission
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from asgiref.sync import sync_to_async
from django.conf import settings

@shared_task
def add_to_cluster(name, types, justi, cluster):
    if len(types) > 0:
        cluster_entry = {
            'name': name,
            'types': [],
            'justif': justi
        }
        for type_value in types:
            cluster_entry['types'].append(type_value)
        cluster.append(cluster_entry)

        return cluster

@shared_task
async def send_cluster_email(employee, data, role_type):
    cluster = []
    add_to_cluster(role_type, ast.literal_eval(data.roles), data.justification, cluster)

    from_email = employee.email_employee
    recipient_list = ['miranda.rosely@sci.ui.ac.id']

    subject = f'Submission New Access Cluster {role_type}'
    message = render_to_string('send_cluster.html', {
        'email_employee': employee.email_employee,
        'cluster': cluster,
        'id': employee.id,
        'cluster_name': role_type
    })
    msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)
    msg.attach_alternative(message, "text/html")
    await sync_to_async(msg.send)()


@shared_task
def send_message_failed(email):
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    subject = 'Your Submission Access'
    message = "GAGAL YA"
    msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)
    msg.attach_alternative(message, "text/html")
    msg.send()

