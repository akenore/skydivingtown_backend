"""
URL configuration for config project.

if need any help : 
    Dev: Muhammad Aslan 
    Email: joudakenore@gmail.com
    Email: csa@beandgo.io
    Phone: +216 55 000 359
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [


    path('superadmin/', admin.site.urls),
    # path('auth/', include('rest_framework.urls')),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('accounts/', include('allauth.urls')),
    path('tinymce/', include('tinymce.urls')),


    path('', include('public.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)


admin.site.site_header = "SuperAdmin"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Admin"
