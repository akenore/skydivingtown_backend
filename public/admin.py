from django.contrib import admin
from public.models import Page
from tinymce.widgets import TinyMCE
from django import forms

# class PageAdminForm(forms.ModelForm):
#     content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    
#     class Meta:
#         model = Page
#         fields = '__all__'

# class PageAdmin(admin.ModelAdmin):
#     form = PageAdminForm

# admin.site.register(Page, PageAdmin)
admin.site.register(Page)