from django import forms
from django.contrib import admin
from .models import Event, EventDate, EventOption, Subscriber, Payment
from datetime import timedelta
from django.utils.translation import gettext as _


class EventAdminForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label=_("Start Date")
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label=_("End Date")
    )
    max_subscribers = forms.IntegerField(
        required=False, label=_("Max Subscribers"))

    class Meta:
        model = Event
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        max_subscribers = self.cleaned_data.get('max_subscribers')

        if commit:
            instance.save()

        if start_date and end_date and max_subscribers is not None:
            EventDate.objects.filter(event=instance).delete()

            for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
                EventDate.objects.create(
                    event=instance, date=single_date, maxSubscribers=max_subscribers)

        return instance


class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 1


class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ['name', 'amount', 'published']
    inlines = [EventDateInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['start_date'].initial = None
            form.base_fields['end_date'].initial = None
            form.base_fields['max_subscribers'].initial = None
        return form


class EventOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'published']


admin.site.register(Event, EventAdmin)
admin.site.register(EventOption, EventOptionAdmin)
admin.site.register(Subscriber)
admin.site.register(Payment)
