from django import forms
from datetime import timedelta
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, F
from event.models import Event, EventDate, Subscriber


class NewEventForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Start Date')
            }
        ),
        required=False,
        label=_("Start Date")
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('End Date')
            }
        ),
        required=False,
        label=_("End Date")
    )
    max_subscribers = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Max Subscribers')
            }
        ),
        required=False, label=_("Max Subscribers"))

    class Meta:
        model = Event
        fields = '__all__'
        exclude = ['options']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Event name')
            }),
            'options': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox h-4 w-4 text-indigo-600 transition duration-150 ease-in-out'
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
        max_subscribers = self.cleaned_data.get('max_subscribers')

        if commit:
            instance.save()

        if start_date and end_date and max_subscribers is not None:
            EventDate.objects.filter(event=instance).delete()

            for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
                EventDate.objects.create(
                    event=instance, date=single_date, maxSubscribers=max_subscribers)

        return instance


class EventDateForm(forms.ModelForm):
    class Meta:
        model = EventDate
        fields = ['date', 'maxSubscribers']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': 'Date',
                'type': 'date'
            }),
            'maxSubscribers': forms.NumberInput(attrs={
                'class': 'ml-2 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': 'Max Subscribers'
            }),
        }


EventDateFormSet = inlineformset_factory(
    Event,
    EventDate,
    form=EventDateForm,
    extra=1,
    can_delete=True
)


class SubscriberForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        event_pk = kwargs.pop('event_pk', None)
        super().__init__(*args, **kwargs)
        if event_pk:
            self.fields['eventDate'].queryset = EventDate.objects.filter(
                event__pk=event_pk).annotate(
                subscriber_count=Count('subscribers')
            ).filter(
                subscriber_count__lt=F(
                    'maxSubscribers')
            )

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
                'placeholder': _('Name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Email')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': _('Phone')
            }),
            'birthDate': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
                'placeholder': 'Date',
                'type': 'date'
            }),
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
