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
    recipient_list = [employee.email_supervisor]

    subject = f'Tableau Access Request #{employee.id} Approval Head Cluster {role_type}'
    message = render_to_string('send_cluster.html', {
        'email_employee': employee.email_employee,
        'cluster_employee': employee.cluster,
        'direct_supervisor': employee.email_supervisor,
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

    subject = 'Tableau Access Request Denied'
    message = render_to_string('send_failed.html', {
        'recipient_list': email,
    })
    msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)
    msg.attach_alternative(message, "text/html")
    msg.send()

