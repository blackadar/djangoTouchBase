import datetime
import bleach

from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import is_safe_url
from django.conf import settings

from .models import Student, Group, Truancy, MissingWork
from .utils import TruancyTypes, SubjectTypes
from .forms import GroupForm

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

def index(request):
    today = datetime.date.today()
    truancies_today = Truancy.objects.filter(Q(date=today)).count()
    absent_today = Student.objects.filter(Q(truancy__date=today) & Q(truancy__issue=TruancyTypes.ABSENT) & Q(truancy__subject=SubjectTypes.HOMEROOM)).distinct().count()
    ud_t = Truancy.objects.filter(discussed=False).count()
    ud_m = MissingWork.objects.filter(discussed=False).count()
    context = {
            'current_time': datetime.datetime.now().hour,
            'absent_today': absent_today,
            'truancies_today': truancies_today,
            'to_discuss': ud_m + ud_t,
    }

    return render(request, 'touchbase/index.html', context)


@login_required
@permission_required('touchbase.view_reports')
def hr(request):
    today = datetime.date.today()
    hr_absences = Student.objects.filter(Q(truancy__date=today) & Q(truancy__issue=TruancyTypes.ABSENT) &
                                         Q(truancy__subject=SubjectTypes.HOMEROOM)).distinct()
    context = {
            'hr_absences': hr_absences,
    }

    if 'selected_group' in request.session.keys() and request.session['selected_group'] is not None:
        context['group'] = Group.objects.all().get(pk=request.session['selected_group'])
        context['hr_absences'] = context['hr_absences'].filter(group_id=context['group'])

    return render(request, 'touchbase/hr.html', context)


@login_required
@permission_required('touchbase.view_reports')
def dashboard(request):
    timedelta = 8  # (days)
    gt_low = datetime.date.today() - datetime.timedelta(days=timedelta)
    relevant = Truancy.objects.filter(date__gt=gt_low)
    absences = relevant.filter(issue=TruancyTypes.ABSENT)
    tardies = relevant.filter(issue=TruancyTypes.TARDY)
    skips = relevant.filter(issue=TruancyTypes.SKIP)
    context = {
            'd_absences': [],
            'd_skips': [],
            'd_tardies': [],
            'dates': [],

            'g_absences': [],
            'g_skips': [],
            'g_tardies': [],
            'groups': [],

            't_absences': absences.count(),
            't_skips': skips.count(),
            't_tardies': tardies.count(),
    }

    for day in daterange(gt_low, datetime.date.today()):
        context['d_absences'].append(absences.filter(date=day).count())
        context['d_skips'].append(skips.filter(date=day).count())
        context['d_tardies'].append(tardies.filter(date=day).count())
        context['dates'].append(str(day))

    for group in Group.objects.all():
        context['groups'].append(group.name)
        context['g_absences'].append(absences.filter(student__group=group).count())
        context['g_skips'].append(skips.filter(student__group=group).count())
        context['g_tardies'].append(tardies.filter(student__group=group).count())

    context['g_pack'] = zip(context['groups'], context['g_absences'], context['g_skips'], context['g_tardies'])

    print(context)

    return render(request, 'touchbase/dashboard.html', context)


@login_required
@permission_required('touchbase.view_reports')
def select_group(request):
    form = GroupForm(request.GET)

    try:  # If there is a GET parameter for next, consume it and move it to session variables.
        nxt = request.GET['next']
        request.session['next'] = nxt
    except KeyError:
        pass

    if form.is_valid():
        request.session['selected_group'] = form.cleaned_data['group'].id
        try:
            nxt = request.session['next']  # If next was set above, the form was completed, so now redirect!
        except KeyError:
            nxt = None
        if is_safe_url(nxt, allowed_hosts=settings.ALLOWED_HOSTS, require_https=request.is_secure()):
            return redirect(nxt)
        else:
            return HttpResponseRedirect('/')

    return render(request, 'touchbase/select_group.html', {'form': form})

@login_required
@permission_required('touchbase.view_reports')
def clear_group(request):
    try:
        request.session['selected_group'] = None
    except KeyError:
        pass

    try:
        nxt = request.GET['next']
        if is_safe_url(nxt, allowed_hosts=settings.ALLOWED_HOSTS, require_https=request.is_secure()):
            return redirect(nxt)
        else:
            return HttpResponseRedirect('/')
    except KeyError:
        pass

    return HttpResponseRedirect('/')


def contact(request):
    return render(request, 'touchbase/contact.html')


def contact_submit(request):
    name = bleach.clean(request.POST['name'])
    email = bleach.clean(request.POST['email'])
    message = bleach.clean(request.POST['message'])
    dt = datetime.datetime.now()
    send_mail(f'CF: {name}', f'This is an automated message from TouchBase contact form.\n'
                             f'{name} requests an account for {email} with the following details:\n'
                             f'"{message}"\n'
                             f'This was {dt}.\n'
                             f"Let's get them up and running ASAP!", from_email=settings.EMAIL_HOST_USER,
                             recipient_list=settings.EMAIL_FORM_CONTACT_LIST
              )
    return HttpResponseRedirect('/')
