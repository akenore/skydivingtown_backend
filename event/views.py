from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template

from event.models import Event, EventOption, Subscriber
from event.forms import NewEventForm, EventDateFormSet, SubscriberForm, EventOptionForm

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
            context['eventdate_formset'] = EventDateFormSet(self.request.POST)
        else:
            context['eventdate_formset'] = EventDateFormSet()
        context['view'] = 'EventCreateView'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        eventdate_formset = context['eventdate_formset']
        if eventdate_formset.is_valid():
            self.object = form.save()
            eventdate_formset.instance = self.object
            eventdate_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class EventUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Event
    form_class = NewEventForm
    template_name = "event/forms/event.html"
    # success_url = reverse_lazy('list_event')
    success_message = _("Event updated successfully.")

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['eventdate_formset'] = EventDateFormSet(
                self.request.POST, instance=self.object)
        else:
            context['eventdate_formset'] = EventDateFormSet(
                instance=self.object)
        context['view'] = 'EventUpdateView'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        eventdate_formset = context['eventdate_formset']
        if eventdate_formset.is_valid():
            self.object = form.save()
            eventdate_formset.instance = self.object
            eventdate_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


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
        # return reverse('event', kwargs={'pk': self.kwargs['pk']})
        return self.request.path


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
    paginate_by = 1
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
