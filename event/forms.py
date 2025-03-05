from django import forms
from datetime import datetime, timedelta
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, F
from event.models import Event, EventDate, EventTime, Subscriber, EventOption
import datetime


class NewEventForm(forms.ModelForm):
    # start_date = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={
    #             'type': 'date',
    #             'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
    #             'placeholder': _('Start Date')
    #         }
    #     ),
    #     required=False,
    #     label=_("Start Date")
    # )
    # end_date = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={
    #             'type': 'date',
    #             'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
    #             'placeholder': _('End Date')
    #         }
    #     ),
    #     required=False,
    #     label=_("End Date")
    # )

    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Event name'),
                'autocomplete': 'on'
            }),
            'options': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox transition duration-150 ease-in-out'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Price')
            }),
            'description': forms.Textarea(attrs={
                'class': 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Description')
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if commit:
            instance.save()

        if start_date and end_date:
            if instance.pk:
                EventDate.objects.filter(event=instance).delete()

            for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
                event_date = EventDate.objects.create(
                    event=instance, date=single_date)
                EventTime.objects.create(
                    event_date=event_date, time='09:00:00')

        return instance


class EventDateForm(forms.ModelForm):

    class Meta:
        model = EventDate
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': 'Date',
                'type': 'date', 'required': False
            }),
        }


class EventTimeForm(forms.ModelForm):
    class Meta:
        model = EventTime
        fields = ['time', 'maxSubscribers']
        widgets = {
            'time': forms.TimeInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': 'Time',
                'type': 'time'
            }),
            'maxSubscribers': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': 'Max Subscribers'
            }),
        }


EventDateFormSet = inlineformset_factory(
    Event,
    EventDate,
    form=EventDateForm,
    extra=1,
    can_delete=True,
)

EventTimeFormSet = inlineformset_factory(
    EventDate,
    EventTime,
    form=EventTimeForm,
    extra=1,
    can_delete=True,
)


class SubscriberForm(forms.ModelForm):
    

    def __init__(self, *args, **kwargs):
        event_pk = kwargs.pop('event_pk', None)
        super().__init__(*args, **kwargs)
        if event_pk:
            self.fields['eventDate'].queryset = EventDate.objects.filter(
                event__pk=event_pk
            ).annotate(subscriber_count=Count('event_times__subscribers')
                       ).filter(event_times__maxSubscribers__gt=F('subscriber_count')).distinct()

    class Meta:
        model = Subscriber
        fields = '__all__'
        widgets = {
            'eventDate': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            }),
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Name')
            }),
            'surname': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Surname')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Email')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Phone')
            }),
            'birthDate': forms.widgets.SelectDateWidget(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                
            },
            years=range(1970, 2025),
            empty_label=(_("Year"), _("Month"), _("Day")),
            ),
            'gender': forms.RadioSelect(attrs={
                'class': 'm-0',
            }),
            'altitude': forms.RadioSelect(attrs={
                'class': 'm-0',
            }),
            'skydiverOption': forms.RadioSelect(attrs={
                'class': 'm-0',
            }),
            'options': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox text-indigo-600 transition duration-150 ease-in-out'
            }),
            'country': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            }),
            'region': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('City')
            }),
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     day = cleaned_data.get('birth_day')
    #     month = cleaned_data.get('birth_month')
    #     year = cleaned_data.get('birth_year')

    #     if day and month and year:
    #         try:
    #             cleaned_data['birthDate'] = datetime.date(int(year), int(month), int(day))
    #         except ValueError:
    #             self.add_error('birthDate', 'Invalid date')
    #     return cleaned_data


class EventOptionForm(forms.ModelForm):

    class Meta:
        model = EventOption
        fields = "__all__"

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Name'),
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('300.00 TND')
            }),
        }
