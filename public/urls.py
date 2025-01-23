from django.urls import path
from public.views import *
from contract.views import CompanyPublicCreateView

urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('new-company/', CompanyPublicCreateView.as_view(), name='new_company'),
]
