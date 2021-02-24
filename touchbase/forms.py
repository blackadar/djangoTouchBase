from django import forms
from .models import Group


class GroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
