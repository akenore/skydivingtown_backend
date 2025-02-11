from django.urls import path, include
from public.views import *

urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('myadmin/', AdminView.as_view(), name="myadmin"),
    path('myadmin/', include([
         path('events/', include('event.urls')),
         path('companies/', include('contract.urls')),
         ])
         ),
]
