from contract.forms import CompanyPublicForm, CompanyUpdateForm
from contract.models import Company
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
import requests
import logging

logger = logging.getLogger(__name__)


from_email = settings.DEFAULT_FROM_EMAIL
admin_emails = settings.ADMIN_LIST_EMAILS


class CompanyCreateView(SuccessMessageMixin, CreateView):
    model = Company
    form_class = CompanyPublicForm
    success_message = _(
        "Company Created Successfully. Your request is being reviewed by our team. You will receive your access code shortly.")
    template_name = "contract/forms/add.html"

    def get_success_url(self):
        return reverse('list_company')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.initial_discount = form.instance.discount
        return form

    def form_valid(self, form, **kwargs):

        response = super().form_valid(form)
        # admin_subject = _("Skydiving Town: a new company registered")
        # admin_message_text = _(
        #     "A new company has been registered. Please review the details below:\n\n"
        #     "Name: {name}\n"
        #     "Email: {email}\n"
        #     "Phone: {phone}\n"
        #     "Ref: {ref}\n"
        #     "\n\nThank you for your attention."
        # ).format(
        #     name=form.instance.name,
        #     email=form.instance.email,
        #     phone=form.instance.phone,
        #     ref=form.instance.ref
        # )

        # admin_message_html = get_template('contract/email/admin.html').render({
        #     'name': form.instance.name,
        #     'email': form.instance.email,
        #     'phone': form.instance.phone,
        #     'ref': form.instance.ref,
        # })

        # admin_send = EmailMultiAlternatives(
        #     admin_subject,
        #     admin_message_text,
        #     from_email,
        #     admin_emails,
        #     headers={
        #         'Reply-To': 'contact@skydivingtown.com',
        #         'Return-Path': 'contact@skydivingtown.com',
        #         'X-Sender': from_email,
        #     }
        # )
        # admin_send.attach_alternative(admin_message_html, "text/html")
        # admin_send.send()

        try:
            country_code_number = int(form.instance.countryCode.lstrip('+'))
        except (ValueError, IndexError) as e:
            messages.error(self.request, _("Invalid country code format"))
            return response

        api_key = settings.BREVO_API_KEY
        api_company_url = "https://api.brevo.com/v3/companies"

        payload = {
            "attributes": {
                "email": form.instance.email,
                "ref": form.instance.ref,
                "phone_number": form.instance.phone,
            },
            "name": form.instance.name,
            "countryCode": country_code_number,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key
        }

        try:
            brevo_response = requests.post(
                api_company_url,
                json=payload,
                headers=headers
            )
            brevo_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            messages.error(self.request, _("Brevo API Error: ") + str(e))
            logger.error(f"Brevo API Failure: {str(e)}")
        return response


class CompanyUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Company
    form_class = CompanyUpdateForm
    template_name = "contract/forms/update.html"

    def get_success_url(self):
        return reverse('list_company')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.initial_discount = form.instance.discount
        self.initial_valid = form.instance.valid
        return form

    def form_valid(self, form, **kwargs):
        response = super().form_valid(form)
        if self.initial_discount != form.instance.discount:
            messages.success(self.request, _(
                'Discount value has been updated.'))

            client_subject = _("Skydiving Town: A Discount Has Been Applied!")
            client_message_text = _(
                "Your discount has been successfully applied. Please find the details below:\n\n"
                "Discount Amount: {discount}\n"
                "Reference: {ref}\n"
                "Use this reference when subscribing to the event to receive a discount"
                "\n\nThank you for your continued support!"
            ).format(
                discount=form.instance.discount,
                ref=form.instance.ref
            )
            client_email = [form.instance.email]
            client_message_html = get_template('contract/email/discount_update.html').render({
                'discount': form.instance.discount,
                'ref': form.instance.ref,
            })

            client_send = EmailMultiAlternatives(
                client_subject,
                client_message_text,
                from_email,
                client_email,
                headers={
                    'Reply-To': 'contact@skydivingtown.com',
                    'Return-Path': 'contact@skydivingtown.com',
                    'X-Sender': from_email,
                }
            )
            client_send.attach_alternative(client_message_html, "text/html")
            client_send.send()
        else:
            messages.info(self.request, _('No change in the discount value.'))
        if self.initial_valid != form.instance.valid:
            messages.success(self.request, _('The company is validated.'))
        return response


class CompanyDeleteView(SuccessMessageMixin, DeleteView):
    model = Company
    success_url = reverse_lazy('list_company')
    success_message = _('Unfortunately, this company has been deleted')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(CompanyDeleteView, self).delete(request, *args, **kwargs)


class CompanyListView(ListView):
    model = Company
    paginate_by = 10
    template_name = "contract/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')

        if query:
            return Company.objects.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            ).order_by('-published')
        return Company.objects.all().order_by('-published')

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('q'):
            self.template_name = "contract/partial/data.html"
        return super().render_to_response(context, **response_kwargs)
