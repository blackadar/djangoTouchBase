import csv
import datetime
from django.contrib import admin
from django.db.models import Count, Case, When, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.db import models
from .models import Student, Truancy, MissingWork, Group
from django.forms.models import ModelForm
from .utils import SubjectTypes, TruancyTypes
from django.forms import TextInput, Textarea
admin.site.site_header = "TouchBase"
admin.site.site_title = "TouchBase"


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export to .csv"


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should return True if data differs from initial.
        By always returning true even unchanged inlines will get validated and saved."""
        return True


class TruancyInline(admin.TabularInline):
    formfield_overrides = {  # Makes the 'Notes' field bigger by default
            models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 75})},
    }
    model = Truancy
    # form = AlwaysChangedModelForm
    ordering = ['date', ]
    extra = 0


class MissingWorkInline(admin.TabularInline):
    formfield_overrides = {  # Makes the 'Notes' field bigger by default
            models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 75})},
    }
    model = MissingWork
    # form = AlwaysChangedModelForm
    ordering = ['date', ]
    extra = 0


class StudentInline(admin.TabularInline):
    model = Student
    # form = AlwaysChangedModelForm
    ordering = ['last_name', 'first_name']
    fields = ['last_name', 'first_name', 'group']
    show_change_link = True
    # readonly_fields = ['last_name', 'first_name']
    extra = 0
    raw_id_fields = ['group']
    # can_delete = False


class StudentAdmin(admin.ModelAdmin, ExportCsvMixin):

    list_filter = ('group', )

    formfield_overrides = {  # Makes the 'Notes' field bigger by default
            models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 75})},
    }

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        timedelta = 8  # (days)
        gt_low = datetime.date.today() - datetime.timedelta(days=timedelta)
        queryset = super().get_queryset(request)
        qrs = [Count(Case(When(Q(truancy__date__gt=gt_low) & Q(truancy__issue=TruancyTypes.ABSENT), then=1))),
               Count(Case(When(Q(truancy__date__gt=gt_low) & Q(truancy__issue=TruancyTypes.TARDY), then=1))),
               Count(Case(When(Q(truancy__date__gt=gt_low) & Q(truancy__issue=TruancyTypes.SKIP), then=1))),
               Coalesce(Sum('missingwork__count', filter=Q(missingwork__date__gt=gt_low), distinct=True), 0),
        ]
        queryset = queryset.annotate(
                _recent_absences=qrs[0],
                _recent_tardies=qrs[1],
                _recent_skips=qrs[2],
                _recent_missing_work=qrs[3],
                _total_recent_issues=qrs[0] + qrs[1] + qrs[2] + qrs[3],
                _total_issues=Count('truancy', distinct=True) + qrs[3],
        )
        return queryset

    def recent_absences(self, obj):
        return obj._recent_absences

    def recent_tardies(self, obj):
        return obj._recent_tardies

    def recent_skips(self, obj):
        return obj._recent_skips

    def recent_missing_work(self, obj):
        return obj._recent_missing_work

    def total_recent_issues(self, obj):
        return obj._total_recent_issues

    def total_issues(self, obj):
        return obj._total_issues

    recent_absences.short_description = 'Absences*'
    recent_tardies.short_description = 'Tardies*'
    recent_skips.short_description = 'Skips*'
    recent_missing_work.short_description = 'Work*'
    total_recent_issues.short_description = 'Total Recent'
    total_issues.short_description = 'Total'

    search_fields = ('first_name', 'last_name')
    inlines = (TruancyInline, MissingWorkInline, )
    list_display = ('__str__', 'recent_absences', 'recent_tardies', 'recent_skips', 'recent_missing_work', 'total_recent_issues', 'total_issues')
    # actions = ('export_as_csv',)

    recent_absences.admin_order_field = '_recent_absences'
    recent_tardies.admin_order_field = '_recent_tardies'
    recent_skips.admin_order_field = '_recent_skips'
    recent_missing_work.admin_order_field = '_recent_missing_work'
    total_recent_issues.admin_order_field = '_total_recent_issues'
    total_issues.admin_order_field = '_total_issues'

    ordering = ['last_name', 'first_name']


class TruancyAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ('student__first_name', 'student__last_name', 'date', 'subject')
    list_display = ('student', 'subject', 'date', 'issue', 'discussed')
    list_filter = ('student__group', 'subject', 'discussed', 'issue', 'date')
    ordering = ['-date', 'student__last_name', 'student__first_name', 'discussed']
    actions = ['make_discussed']

    def make_discussed(self, request, queryset):
        queryset.update(discussed=True)
    make_discussed.short_description = "Mark selected as discussed"


class GroupAdmin(admin.ModelAdmin):
    inlines = (StudentInline, )
    ordering = ['name']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
                _student_count=Count('student', distinct=True)
        )
        return queryset

    def student_count(self, obj):
        return obj._student_count

    list_display = ['__str__', 'student_count']
    student_count.admin_order_field = '_student_count'


class MissingWorkAdmin(admin.ModelAdmin):
    search_fields = ('student__first_name', 'student__last_name', 'date', 'subject')
    list_display = ('student', 'date', 'subject', 'count', 'discussed')
    list_filter = ('student__group', 'discussed', 'subject', 'date')
    ordering = ['-date', 'student__last_name', 'student__first_name']
    actions = ['make_discussed']
    def make_discussed(self, request, queryset):
        queryset.update(discussed=True)

    make_discussed.short_description = "Mark selected as discussed"


admin.site.register(Student, StudentAdmin)
admin.site.register(Truancy, TruancyAdmin)
admin.site.register(MissingWork, MissingWorkAdmin)
admin.site.register(Group, GroupAdmin)
