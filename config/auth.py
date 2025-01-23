from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from allauth.account.forms import LoginForm, SignupForm, ResetPasswordForm, ChangePasswordForm, ResetPasswordKeyForm


class SignIn(LoginForm):

    def __init__(self, *args, **kwargs):
        super(SignIn, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update(
            {'placeholder': _("Username"), 'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})
        self.fields['password'].widget.attrs.update(
            {'placeholder': '••••••••', 'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})


class ChangePassword(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)
        self.fields['oldpassword'].widget.attrs.update(
            {'placeholder': '••••••••', 'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})
        self.fields['password1'].widget.attrs.update(
            {'placeholder': '••••••••', 'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})


class ResetPassword(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(ResetPassword, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'placeholder': _('Email address'), 'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})