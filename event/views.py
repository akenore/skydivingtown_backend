from datetime import datetime
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.forms.models import inlineformset_factory
from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from event.models import Event, EventOption, Subscriber, EventDate, EventTime
from event.forms import NewEventForm, EventDateFormSet, EventTimeFormSet, SubscriberForm, EventOptionForm, EventDateForm, EventTimeForm

from_email = settings.DEFAULT_FROM_EMAIL
admin_emails = settings.ADMIN_LIST_EMAILS


class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = NewEventForm
    template_name = "event/forms/event.html"
    success_url = reverse_lazy('list_event')
    success_message = _("Event created successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['eventdate_formset'] = EventDateFormSet(
                self.request.POST, instance=self.object)
            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                if date_form.instance.pk:
                    date_form.eventtime_formset = EventTimeFormSet(
                        self.request.POST, instance=date_form.instance, prefix=prefix)
                else:
                    date_form.eventtime_formset = EventTimeFormSet(
                        self.request.POST, prefix=prefix)
        else:
            context['eventdate_formset'] = EventDateFormSet(
                instance=self.object)

            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                if date_form.instance.pk:
                    date_form.eventtime_formset = EventTimeFormSet(
                        instance=date_form.instance, prefix=prefix)
                else:
                    date_form.eventtime_formset = EventTimeFormSet(
                        prefix=prefix)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        eventdate_formset = context['eventdate_formset']

        if form.is_valid() and eventdate_formset.is_valid():
            self.object = form.save()
            eventdate_formset.instance = self.object
            eventdates = eventdate_formset.save()

            for i, event_date in enumerate(eventdates):
                date_form = eventdate_formset.forms[i]
                if hasattr(date_form, 'eventtime_formset'):
                    time_formset = date_form.eventtime_formset
                    if time_formset.is_bound and time_formset.is_valid():
                        for time_form in time_formset:
                            if time_form.is_valid() and time_form.cleaned_data and not time_form.cleaned_data.get('DELETE', False):
                                time_instance = time_form.save(commit=False)
                                time_instance.event_date = event_date
                                time_instance.save()

            return super().form_valid(form)

        return self.form_invalid(form)


class EventUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Event
    form_class = NewEventForm
    template_name = "event/forms/event.html"
    success_message = _("Event updated successfully.")

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['eventdate_formset'] = EventDateFormSet(
                self.request.POST, instance=self.object)
            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                if date_form.instance.pk:
                    date_form.eventtime_formset = EventTimeFormSet(
                        self.request.POST, instance=date_form.instance, prefix=prefix)
                else:
                    date_form.eventtime_formset = EventTimeFormSet(
                        self.request.POST, prefix=prefix)
        else:
            context['eventdate_formset'] = EventDateFormSet(
                instance=self.object)

            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                if date_form.instance.pk:
                    date_form.eventtime_formset = EventTimeFormSet(
                        instance=date_form.instance, prefix=prefix)
                else:
                    date_form.eventtime_formset = EventTimeFormSet(
                        prefix=prefix)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        eventdate_formset = context['eventdate_formset']

        if form.is_valid() and eventdate_formset.is_valid():
            self.object = form.save()
            eventdate_formset.instance = self.object
            eventdates = eventdate_formset.save()

            for i, event_date in enumerate(eventdates):
                date_form = eventdate_formset.forms[i]
                if hasattr(date_form, 'eventtime_formset'):
                    time_formset = date_form.eventtime_formset
                    if time_formset.is_bound and time_formset.is_valid():
                        for time_form in time_formset:
                            if time_form.is_valid() and time_form.cleaned_data and not time_form.cleaned_data.get('DELETE', False):
                                time_instance = time_form.save(commit=False)
                                time_instance.event_date = event_date
                                time_instance.save()

            return super().form_valid(form)

        return self.form_invalid(form)


class EventDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('list_event')
    success_message = _("Unfortunately, this event has been deleted")

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(EventDeleteView, self).delete(request, *args, **kwargs)


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    ordering = ['-published']
    paginate_by = 10
    template_name = "event/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Event.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).order_by('-published')
        return Event.objects.all().order_by('-published')

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('q'):
            self.template_name = "event/partial/data.html"
        return super().render_to_response(context, **response_kwargs)


class EventDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = Event
    template_name = "event/detail.html"
    context_object_name = 'event'
    success_message = _("List has been updated successfully.")
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        subscribers = Subscriber.objects.filter(
            eventDate__event=self.object).order_by('-published')
        if query:
            subscribers = subscribers.filter(name__icontains=query)
        paginator = Paginator(subscribers, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['query'] = query
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('q'):
            self.template_name = "event/partial/data_subscribers.html"
        return super().render_to_response(context, **response_kwargs)


class SubscriberCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = "event/forms/subscriber.html"
    success_message = _("Subscriber has been added successfully.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event_pk'] = self.kwargs.get('pk')
        return kwargs

    def get_success_url(self):
        return reverse('event', kwargs={'pk': self.object.eventDate.event.pk})


class SubscriberUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = "event/forms/subscriber.html"
    success_message = _("Subscriber has been updated successfully.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event_pk'] = self.object.eventDate.event.pk
        return kwargs

    def get_success_url(self):
        return reverse('event', kwargs={'pk': self.object.eventDate.event.pk})


class SubscriberDeleteView(DeleteView):
    model = Subscriber
    success_message = _("Unfortunately, this client has been deleted")

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(EventDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('event', kwargs={'pk': self.object.eventDate.event.pk})


class EventOptionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = EventOption
    form_class = EventOptionForm
    success_url = reverse_lazy('option')
    success_message = _("Option has been added successfully.")
    template_name = "event/forms/option.html"


class EventOptionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = EventOption
    form_class = EventOptionForm
    success_url = reverse_lazy('option')
    success_message = _("Option has been added successfully.")
    template_name = "event/forms/option.html"


class EventOptionListView(ListView):
    model = EventOption
    ordering = ['-published']
    paginate_by = 10
    template_name = "event/options/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return EventOption.objects.filter(
                Q(name__icontains=query) |
                Q(amount__icontains=query)
            ).order_by('-published')
        return EventOption.objects.all().order_by('-published')

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('q'):
            self.template_name = "event/options/data.html"
        return super().render_to_response(context, **response_kwargs)


class EventOptionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = EventOption
    success_url = reverse_lazy('option')
    success_message = _("Unfortunately, this option has been deleted")

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(EventDeleteView, self).delete(request, *args, **kwargs)


class ExportSubscribersView(View):
    def get(self, request, event_pk, export_type):
        event = get_object_or_404(Event, pk=event_pk)

        try:
            subscribers = Subscriber.objects.filter(eventDate__event=event)
        except Exception:
            try:
                subscribers = Subscriber.objects.filter(event=event)
            except Exception:
                subscribers = Subscriber.objects.filter(
                    id__in=event.get_subscriber_ids())
        data = []
        for subscriber in subscribers:
            options = ', '.join([option.name for option in subscriber.options.all(
            )]) if subscriber.options.exists() else ''
            subscriber_data = {
                _('Gender'): subscriber.get_gender_display(),
                _('Full name'): f"{subscriber.name} \n {subscriber.surname}",
                _('Information'): f"{_('Email')}: {subscriber.email} \n {_('Phone')}: {subscriber.phone} \n {_('Age')}: {subscriber.birthDate} \n {_('Country')}: {subscriber.country.name} \n {_('Region')}: {subscriber.region} \n {_('Gender')}: {subscriber.get_gender_display()}",
                _('Jump info'): f"{_('Altitude')}: {subscriber.get_altitude_display()} \n {_('Skydiver Option')}: {subscriber.get_skydiverOption_display()} \n {_('Options')}: {options} \n {_('Date')}: {subscriber.eventDate.date} \n {_('Time')}: {subscriber.eventTime.time}",

            }

            try:
                if hasattr(subscriber, 'payments'):
                    payment_validated = subscriber.payments.first(
                    ).validated if subscriber.payments.exists() else False
                    subscriber_data[_('Payment Validated')] = _(
                        'Yes') if payment_validated else _('No')
            except Exception:
                subscriber_data[_('Payment Validated')] = _('Unknown')

            data.append(subscriber_data)

        if export_type == 'excel':
            df = pd.DataFrame(data)
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename={event.name}_subscribers.xlsx'
            df.to_excel(response, index=False)
            return response

        elif export_type == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={event.name}_subscribers.pdf'

            doc = SimpleDocTemplate(response, pagesize=landscape(letter))
            elements = []

            table_data = list(data[0].keys())
            table_data = [list(data[0].keys())]
            for item in data:
                table_data.append(list(item.values()))

            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 13),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 13),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)

            doc.build(elements)
            return response

        return HttpResponse('Invalid export type', status=400)
