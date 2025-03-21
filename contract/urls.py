from django.urls import path, include
from contract.views import CompanyCreateView, CompanyUpdateView, CompanyDeleteView, CompanyListView


urlpatterns = [
    path('add/', CompanyCreateView.as_view(), name='add_company'),
    path('update/<int:pk>/', CompanyUpdateView.as_view(), name='update_company'),
    path('delete/<int:pk>/', CompanyDeleteView.as_view(), name='delete_company'),
    path('list/', CompanyListView.as_view(), name='list_company'),
    path('search/', CompanyListView.as_view(), name='company_search'),
]
