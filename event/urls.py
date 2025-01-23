from django.urls import path, include
from event.views import *

urlpatterns = [
    path('new/', EventCreateView.as_view(), name='new_event'),
    path('update/<int:pk>/', EventUpdateView.as_view(), name='update_event'),
    path('delete/<int:pk>/', EventDeleteView.as_view(), name='delete_event'),
    path('list/', EventListView.as_view(), name='list_event'),
    path('search/', EventListView.as_view(), name='event_search'),
    path('<int:pk>/', EventDetailView.as_view(), name='event'),
    
    path('<int:event_pk>/subscriber/new/', SubscriberCreateView.as_view(), name='add_subscriber'),
    path('subscriber/<int:pk>/edit/', SubscriberUpdateView.as_view(), name='update_subscriber'),
    path('subscriber/<int:pk>/delete/', SubscriberDeleteView.as_view(), name='delete_subscriber'),
    path('<int:pk>/search/subscribers/', EventDetailView.as_view(), name='search_subscriber'),

]
