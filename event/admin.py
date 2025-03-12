from django import forms
from django.contrib import admin
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
from .models import Event, EventDate, EventTime, EventOption, Subscriber, Payment
from datetime import timedelta, datetime
from django.utils.translation import gettext as _


class EventTimeInline(NestedTabularInline):
    model = EventTime
    extra = 1
    fields = ['time', 'maxSubscribers']


class EventDateInline(NestedStackedInline):
    model = EventDate
    extra = 1
    inlines = [EventTimeInline]
    fields = ['date']


class EventAdmin(NestedModelAdmin):
    inlines = [EventDateInline]
    list_display = ['name', 'amount', 'published']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        existing_dates = set()
        if change:
            existing_dates = set(
                obj.event_dates.values_list('date', flat=True))

        new_dates = set()
        if hasattr(form, 'nested_formsets'):
            for nested_formset in form.nested_formsets:
                if nested_formset.instance:
                    new_dates.add(nested_formset.instance.date)

        dates_to_delete = existing_dates - new_dates
        if dates_to_delete:
            for date in dates_to_delete:
                event_date = EventDate.objects.filter(event=obj, date=date).first()
                if event_date:
                    if event_date.subscribers.exists() or event_date.event_times.exists():
                        self.message_user(
                            request,
                            f"Cannot delete EventDate {event_date.date} because it has related Subscribers.",
                            level='error',
                        )
                    else:
                        event_date.delete()


class EventOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'published']


admin.site.register(Event, EventAdmin)
admin.site.register(EventOption, EventOptionAdmin)
admin.site.register(Subscriber)
admin.site.register(Payment)