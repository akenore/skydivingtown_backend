from datetime import datetime
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from event.models import Event, EventDate, EventTime
from django.db.models import Count
from collections import defaultdict


class AdminView(LoginRequiredMixin, TemplateView):
    template_name = "public/secure/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_event = Event.objects.order_by('-published').first()

        latest_event_date = None
        latest_event_times = []
        total_subscribers_latest_event = 0
        event_dates_data = defaultdict(int)

        if latest_event:
            event_dates = latest_event.event_dates.all()
            latest_event_times = EventTime.objects.filter(event_date__in=event_dates)
            total_subscribers_latest_event = sum(event_time.subscribers.count() for event_time in latest_event_times)

            for event_time in latest_event_times:
                event_dates_data[event_time.event_date.date] += event_time.subscribers.count()

        chart_data = [
            {"x": date.strftime('%a') + ' ' + date.strftime('%d/%m'), "y": count}
            for date, count in event_dates_data.items()
        ]

        context.update({
            "latest_event": latest_event,
            "latest_event_date": latest_event_date,
            "latest_event_times": latest_event_times,
            "total_subscribers_latest_event": total_subscribers_latest_event,
            "chart_data": chart_data,
        })

        return context


class Home(TemplateView):
    template_name = "public/index.html"
