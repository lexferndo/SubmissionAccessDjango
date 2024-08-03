from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/create-subsimission', views.create_submission, name='create_submission'),
    path('update-supervisor/<int:id>/<int:types>', views.approval_supervisor, name='approval_supervisor'),
    path('update-head/<int:id>/<int:types>', views.approval_head, name='approval_head'),
    path('update-cluster/<int:id>/<int:types>/<str:cluster>', views.approval_cluster, name='approval_cluster'),
]
