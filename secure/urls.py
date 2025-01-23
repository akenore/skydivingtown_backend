from django.urls import path, include
from secure.views import AdminView


urlpatterns = [
    path('', AdminView.as_view(), name="myadmin"),
    path('events/', include('event.urls')),
    path('companies/', include('contract.urls'))

]
