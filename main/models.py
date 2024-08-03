from django.db import models

# Create your models here.

class Commercial(models.Model):
    roles = models.CharField()
    justification = models.CharField()
    approval = models.BooleanField(blank=True, null=True)
    submission = models.ForeignKey('Submission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Commercial'


class Finance(models.Model):
    roles = models.CharField()
    justification = models.CharField()
    approval = models.BooleanField(blank=True, null=True)
    submission = models.ForeignKey('Submission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Finance'


class Operation(models.Model):
    roles = models.CharField()
    justification = models.CharField()
    approval = models.BooleanField(blank=True, null=True)
    submission = models.ForeignKey('Submission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Operation'


class Submission(models.Model):
    email_employee = models.CharField()
    email_supervisor = models.CharField()
    cluster = models.CharField()
    cluster_submission = models.CharField()
    approval_supervisor = models.BooleanField(blank=True, null=True)
    approval_head = models.BooleanField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Submission'


class Tech(models.Model):
    roles = models.CharField()
    justification = models.CharField()
    approval = models.BooleanField(blank=True, null=True)
    submission = models.ForeignKey('Submission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Tech'
