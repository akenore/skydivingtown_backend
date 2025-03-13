from django import forms
from django.core.exceptions import ValidationError
from contract.models import Company


class CompanyPublicForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CompanyPublicForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'mb-4 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})
        self.fields['email'].widget.attrs.update(
            {'class': 'mb-4 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})
        self.fields['phone'].widget.attrs.update(
            {'class': 'mb-4 block p-2.5 w-full z-20 text-sm text-gray-900 bg-gray-50 rounded-e-lg border-s-0 border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-s-gray-700  dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:border-blue-500'})
        self.fields['countryCode'].widget.attrs.update(
            {'class': 'mb-4 shrink-0 z-10 inline-flex items-center py-2.5 px-4 text-sm font-medium text-center text-gray-900 bg-gray-100 border border-gray-300 rounded-s-lg hover:bg-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-700 dark:text-white dark:border-gray-600'})
        self.fields['ref'].required = False
        self.fields['discount'].required = False
        self.fields['valid'].required = False

        self.fields['ref'].widget = forms.HiddenInput()
        self.fields['discount'].widget = forms.HiddenInput()
        self.fields['valid'].widget = forms.HiddenInput()
        self.fields['ref'].label = ''
        self.fields['discount'].label = ''
        self.fields['valid'].label = ''

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Company.objects.filter(name=name).exists():
            raise ValidationError("A company with this name already exists.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Company.objects.filter(email=email).exists():
            raise ValidationError("A company with this email already exists.")
        return email


class CompanyUpdateForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ('discount', 'valid')

    def __init__(self, *args, **kwargs):
        super(CompanyUpdateForm, self).__init__(*args, **kwargs)
        self.fields['discount'].widget.attrs.update(
            {'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})
        self.fields['valid'].widget.attrs.update(
            {'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'})
