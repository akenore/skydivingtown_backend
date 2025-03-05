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


@require_http_methods(["GET"])
def add_event_date_form(request):
    index = int(request.GET.get('index', 0))
    form = EventDateForm(prefix=f'eventdate_set-{index}')
    
    # Create a time formset for this new date
    form.eventtime_formset = EventTimeFormSet(prefix=f'time_{index}')
    
    context = {
        'form': form,
        'forloop': {'counter0': index}
    }
    html = render_to_string('event/forms/partials/event_date_form.html', context, request=request)
    return HttpResponse(html)


@require_http_methods(["GET"])
def add_event_time_form(request):
    date_index = int(request.GET.get('date_index', 0))
    
    # Get the current count of time forms for this date
    prefix = f'time_{date_index}'
    total_forms_name = f'{prefix}-TOTAL_FORMS'
    
    # Default to index 0 if we can't determine the count
    time_index = 0
    if total_forms_name in request.GET:
        time_index = int(request.GET.get(total_forms_name, 0))
    
    form = EventTimeForm(prefix=f'{prefix}-{time_index}')
    
    context = {
        'form': form,
        'date_index': date_index,
        'time_index': time_index
    }
    html = render_to_string('event/forms/partials/event_time_form.html', context, request=request)
    return HttpResponse(html)


@require_http_methods(["DELETE"])
def remove_event_date_form(request, pk):
    try:
        event_date = EventDate.objects.get(pk=pk)
        event_date.delete()
        return HttpResponse(status=204)
    except EventDate.DoesNotExist:
        return HttpResponse(status=404)


@require_http_methods(["DELETE"])
def remove_event_date_form(request, pk):
    event_date = get_object_or_404(EventDate, pk=pk)
    event_date.delete()
    return HttpResponse(status=204)


def remove_event_time_form(request, pk):
    if request.method == "DELETE":
        event_time = get_object_or_404(EventTime, pk=pk)
        event_time.delete()
        # HTMX needs some response, so we return an empty response with a 200 status
        return HttpResponse('', status=200, content_type="text/html")
    return HttpResponse(status=400)


class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = NewEventForm
    template_name = "event/forms/event.html"
    success_url = reverse_lazy('list_event')
    success_message = _("Event created successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['eventdate_formset'] = EventDateFormSet(self.request.POST)
            
            # For each date form, create its time formset
            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                date_form.eventtime_formset = EventTimeFormSet(
                    self.request.POST, prefix=prefix)
        else:
            context['eventdate_formset'] = EventDateFormSet()
            
            # For each date form, create its time formset
            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                date_form.eventtime_formset = EventTimeFormSet(prefix=prefix)
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        eventdate_formset = context['eventdate_formset']
        
        # Flag to track if all forms are valid
        all_valid = form.is_valid() and eventdate_formset.is_valid()
        
        # Check if all time formsets are valid
        for date_form in eventdate_formset:
            if date_form.cleaned_data and not date_form.cleaned_data.get('DELETE', False):
                if not date_form.eventtime_formset.is_valid():
                    all_valid = False
                    break
        
        if all_valid:
            # Save the main event
            self.object = form.save()
            
            # Save event dates
            for i, date_form in enumerate(eventdate_formset):
                if date_form.cleaned_data and not date_form.cleaned_data.get('DELETE', False):
                    # Save the event date
                    event_date = date_form.save(commit=False)
                    event_date.event = self.object
                    event_date.save()
                    
                    # Save the time formset for this date
                    time_formset = date_form.eventtime_formset
                    time_instances = time_formset.save(commit=False)
                    
                    # Set the event_date for each time instance and save
                    for time_instance in time_instances:
                        time_instance.event_date = event_date
                        time_instance.save()
                    
                    # Handle any deleted times
                    for time_form in time_formset.deleted_forms:
                        if time_form.instance.pk:
                            time_form.instance.delete()
            
            return super().form_valid(form)
        
        # If not all forms are valid, return form_invalid
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
            
            # For each date form, create its time formset
            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                if date_form.instance.pk:
                    # If this is an existing date, use its instance for the time formset
                    date_form.eventtime_formset = EventTimeFormSet(
                        self.request.POST, instance=date_form.instance, prefix=prefix)
                else:
                    # For new dates being added
                    date_form.eventtime_formset = EventTimeFormSet(
                        self.request.POST, prefix=prefix)
        else:
            context['eventdate_formset'] = EventDateFormSet(instance=self.object)
            
            # For each date form, create its time formset
            for i, date_form in enumerate(context['eventdate_formset']):
                prefix = f'time_{i}'
                if date_form.instance.pk:
                    date_form.eventtime_formset = EventTimeFormSet(
                        instance=date_form.instance, prefix=prefix)
                else:
                    date_form.eventtime_formset = EventTimeFormSet(prefix=prefix)
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        eventdate_formset = context['eventdate_formset']
        
        # Flag to track if all forms are valid
        all_valid = form.is_valid() and eventdate_formset.is_valid()
        
        # Check if all time formsets are valid
        for date_form in eventdate_formset:
            if date_form.cleaned_data and not date_form.cleaned_data.get('DELETE', False):
                if not date_form.eventtime_formset.is_valid():
                    all_valid = False
                    break
        
        if all_valid:
            # Save the main event
            self.object = form.save()
            
            # Process the date formset
            eventdate_formset.instance = self.object
            
            # Handle deleted dates
            for date_form in eventdate_formset.deleted_forms:
                if date_form.instance.pk:
                    date_form.instance.delete()
            
            # Save remaining dates and their times
            for i, date_form in enumerate(eventdate_formset):
                if date_form.cleaned_data and not date_form.cleaned_data.get('DELETE', False):
                    # Save the event date
                    event_date = date_form.save(commit=False)
                    event_date.event = self.object
                    event_date.save()
                    
                    # Save the time formset for this date
                    time_formset = date_form.eventtime_formset
                    time_formset.instance = event_date
                    
                    # Handle deleted times
                    for time_form in time_formset.deleted_forms:
                        if time_form.instance.pk:
                            time_form.instance.delete()
                    
                    # Save remaining times
                    time_instances = time_formset.save(commit=False)
                    for time_instance in time_instances:
                        time_instance.event_date = event_date
                        time_instance.save()
            
            messages.success(self.request, self.success_message)
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
