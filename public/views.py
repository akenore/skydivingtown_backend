from datetime import datetime
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class AdminView(LoginRequiredMixin, TemplateView):
    template_name = "secure/index.html"


class Home(TemplateView):
    template_name = "public/index.html"
