from django.db import models
import datetime as dt
from .utils import SubjectTypes, TruancyTypes


class Group(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class Student(models.Model):

    class Meta:
        permissions = (
                ('view_reports', 'Can view reports'),
        )

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.last_name + ", " + self.first_name


class Truancy(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=dt.date.today)
    subject = models.IntegerField(choices=SubjectTypes.choices(), null=True)
    issue = models.IntegerField(choices=TruancyTypes.choices(), default=TruancyTypes.ABSENT)
    discussed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Truancy'
        verbose_name_plural = 'Truancies'

    def __str__(self):
        return f"{TruancyTypes(self.issue).name}: " + self.student.full_name + ", " + str(self.date) + (" (!)" if not self.discussed else "")


class MissingWork(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=dt.date.today)
    subject = models.IntegerField(choices=SubjectTypes.choices(), null=True)
    count = models.IntegerField(default=1)
    discussed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Missing Work'
        verbose_name_plural = 'Missing Assignments'

    def __str__(self):
        return f"{SubjectTypes(self.subject).name}: ({self.count}) " + self.student.full_name + ", " + str(self.date) + (" (!)" if not self.discussed else "")
