from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

app_name = 'touchbase'

urlpatterns = [
        path('', views.index, name='index'),
        path('select-group/', views.select_group, name='select_group'),
        path('clear-group/', views.clear_group, name='clear_group'),
        path('hr/', views.hr, name='hr'),
        path('dashboard/', views.dashboard, name='dashboard'),
        path('contact/', views.contact, name='contact'),
        path('contact/submit', views.contact_submit, name='contact_submit'),
]
