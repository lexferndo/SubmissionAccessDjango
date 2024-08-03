import datetime
import json
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from main.helpers import add_to_cluster, send_cluster_email
from main.models import Commercial, Finance, Operation, Submission, Tech
import uuid
import ast
from asgiref.sync import sync_to_async
import tableauserverclient as TSC

TABLEAU_SERVER_URL = 'https://prod-apnortheast-a.online.tableau.com'
TOKEN_NAME = 'mirandamnlng'
TOKEN_VALUE = 'mc5rGZ2xSTKCssOAuV2jQg==:sM2O39nCUNwGxmNTBs4DL8ARCCHeWH4u'
SITE_ID = 'aspireblocks'

tableau_auth = TSC.PersonalAccessTokenAuth(token_name=TOKEN_NAME, personal_access_token=TOKEN_VALUE, site_id=SITE_ID)
server = TSC.Server(TABLEAU_SERVER_URL, use_server_version=True)

models = {
        'Commercial': Commercial,
        'Finance': Finance,
        'Operation': Operation,
        'Tech': Tech
    }

# Create your views here.
def home(request):
    cluster = [
        "Commercial",
        "Finance",
        "Corporate",
        "Operations",
        "Tech"
    ]

    commercial = [
        "Commercial L1",
        "Commercial L2",
        "Commercial L3",
        "Commercial L4",
        "Commercial L5"
    ]

    finance = [
        "Finance L1",
        "Finance L2",
        "Finance L3",
        "Finance L4",
        "Finance L5"
    ]

    operation = [
        "Operations L1",
        "Operations L2",
        "Operations L3",
        "Operations L4",
        "Operations L5"
    ]

    tech = [
        "Tech L1",
        "Tech L2",
        "Tech L3",
        "Tech L4",
        "Tech L5"
    ]

    context = {
        "cluster": cluster,
        "commercial": commercial,
        "finance": finance,
        "operation": operation,
        "tech": tech,
    }

    return render(request, 'index.html', context=context)


def create_submission(request):
    try:
        if request.method == 'POST':
            employee = request.POST.get('employee')
            supervisor = request.POST.get('supervisor')
            cluster = request.POST.get('cluster')
            commercial = json.loads(request.POST.get('commercial'))
            justi_commercial = request.POST.get('justi_commercial')
            finance = json.loads(request.POST.get('finance'))
            justi_finance = request.POST.get('justi_finance')
            operation = json.loads(request.POST.get('operation'))
            justi_operation = request.POST.get('justi_operation')
            tech = json.loads(request.POST.get('tech'))
            justi_tech = request.POST.get('justi_tech')

            cluster_list = []
            cluster_submission = []
            add_to_cluster('Commercial', commercial, justi_commercial, cluster_list)
            add_to_cluster('Finance', finance, justi_finance, cluster_list)
            add_to_cluster('Operation', operation, justi_operation, cluster_list)
            add_to_cluster('Tech', tech, justi_tech, cluster_list)

            if cluster_list:
                for index, data in enumerate(cluster_list):
                    cluster_submission.append(data['name'])

            submission = Submission.objects.create(
                email_employee= employee,
                email_supervisor= supervisor,
                cluster= cluster,
                cluster_submission= cluster_submission,
                approval_supervisor= None,
                approval_head= None,
                status= None
            )

            if commercial:
                Commercial.objects.create(
                    roles = commercial,
                    justification = justi_commercial,
                    approval = None,
                    submission = submission
                )
            
            if finance:
                Finance.objects.create(
                    roles = finance,
                    justification = justi_finance,
                    approval = None,
                    submission = submission
                )
            
            if operation:
                Operation.objects.create(
                    roles = operation,
                    justification = justi_operation,
                    approval = None,
                    submission = submission
                )
            
            if tech:
                Tech.objects.create(
                    roles = tech,
                    justification = justi_tech,
                    approval = None,
                    submission = submission
                )

            if submission:
                from_email = submission.email_employee
                recipient_list = [submission.email_supervisor]

                subject = 'Submission New Access'
                message = render_to_string('send_supervisor.html', {
                    'email_employee': submission.email_employee,
                    'cluster': cluster_list,
                    'id': submission.id
                })

                msg = EmailMultiAlternatives(
                    subject, message, from_email, recipient_list)
                msg.attach_alternative(message, "text/html")
                msg.send()

            return JsonResponse({"detail": "Data berhasil dibuat!"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def approval_supervisor(request, id, types):
    employee =  Submission.objects.filter(id=id).first()

    if types == 1:
        employee.approval_supervisor = True
    else:
        employee.approval_supervisor = False
    employee.save()

    cluster_list = []

    for index, data in enumerate(ast.literal_eval(employee.cluster_submission)):
        model = models.get(data)
        result = model.objects.filter(submission=id).first()
        add_to_cluster(data, ast.literal_eval(result.roles), result.justification, cluster_list)

    if employee.approval_supervisor == True:
        from_email = employee.email_employee
        recipient_list = ['babyshambless09@gmail.com']

        subject = 'Submission New Access'
        message = render_to_string('send_head.html', {
            'email_employee': employee.email_employee,
            'cluster': cluster_list,
            'id': employee.id

        })
        msg = EmailMultiAlternatives(
            subject, message, from_email, recipient_list)
        msg.attach_alternative(message, "text/html")
        msg.send()

        return render(request, 'respon_page.html')


async def approval_head(request, id, types):
    print(f"Starting to send employee at {datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')}")
    employee =  await sync_to_async(Submission.objects.filter(id=id).first)()
    print(f"Ending to send employee at {datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')}")

    if types == 1:
        employee.approval_head = True
    else:
        employee.approval_head = False
    await sync_to_async(employee.save)()

    if employee.approval_head == True:
        for index, data in enumerate(ast.literal_eval(employee.cluster_submission)):
            model = models.get(data)
            print(f"Starting to send email at {datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')}")
            result = await sync_to_async(model.objects.filter(submission=id).first)()
            await send_cluster_email(employee=employee, data=result, role_type=data)
            print(f"Ending to send email at {datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')}")

    return render(request, 'respon_page.html')

def fetch_all_users(server):
    all_users = []
    pagination_item = TSC.Pager(server.users)
    for user in pagination_item:
        all_users.append(user)
    return all_users

def fetch_all_groups(server):
    all_groups = []
    pagination_item = TSC.Pager(server.groups)
    for group in pagination_item:
        all_groups.append(group)
    return all_groups

async def add_user_to_group(server, id):
    try:
        employee = await sync_to_async(Submission.objects.filter(id=id).first)()

        with server.auth.sign_in(tableau_auth):
            print("Successfully signed in.")

            all_users = await sync_to_async(fetch_all_users)(server)
            print("RESULT USER>>", all_users)

            user = next((u for u in all_users if u.name == employee.email_employee), None)
            if user is None:
                print(f"User '{employee.email_employee}' not found.")
                return

            all_groups = await sync_to_async(fetch_all_groups)(server)
            print("RESULT GRUP>>", all_groups)

            for data in ast.literal_eval(employee.cluster_submission):
                model = models.get(data)
                result = await sync_to_async(model.objects.filter(submission=id).first)()
                for role in ast.literal_eval(result.roles):
                    group = next((g for g in all_groups if g.name == role), None)
                    if group is None:
                        print(f"Group '{role}' not found.")
                        return

                    await sync_to_async(server.groups.add_user)(group, user.id)

    except Exception as e:
        print(f"Error': {e}")

async def approval_cluster(request, id, types, cluster):
    model = models.get(cluster)
    result = await sync_to_async(model.objects.filter(submission=id).first)()
    result.approval = types == 1
    await sync_to_async(result.save)()

    employee = await sync_to_async(Submission.objects.filter(id=id).first)()

    approval_status = True
    for data in ast.literal_eval(employee.cluster_submission):
        model_2 = models.get(data)
        result_2 = await sync_to_async(model_2.objects.filter(submission=id).first)()
        if result_2 and not result_2.approval:
            approval_status = False
            break

    employee.status = approval_status
    await sync_to_async(employee.save)()

    if employee.status:
        await add_user_to_group(server, employee.id)

    return render(request, 'respon_page.html')


