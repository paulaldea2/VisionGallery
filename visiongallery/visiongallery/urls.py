"""visiongallery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve

import django

from app.views import *
from app.rest_api import *

mediaUrl = settings.MEDIA_URL
mediaUrl = mediaUrl.replace('/', '')
staticUrl = settings.STATIC_URL
staticUrl = staticUrl.replace('/', '')

urlpatterns = [
    path('react/', TemplateView.as_view(template_name='index.html') ),

    path('main/', main),

    path('login/', login),
    path('authenticate/', authenticate),
    path('register/', register),
    path('recover_account/step_1/', recover_first),
    path('recover_account/step_2/', recover_second),
    path('recover_account/step_3/', recover_third),
    
    path('home/', home),

    path('upload/', UploadPhotoView, name = 'TestPhoto'),
    path('gallery/', GalleryView, name="gallery"),
    path("photo/<path:path>/", PhotoView, name="photo"),
    path("rmph/<path:path>/", DeletePhotoView, name="delphoto"),
    
    path('maps/', maps),
    
    path('settings/general/', settings_general, name="settingsGeneral"),
    path('settings/account/', settings_account, name="settingsAccount"),
    path('settings/password/', settings_password, name="settingsPassword"),
    path('settings/security/', settings_security, name="settingsSecurity"),
    path('settings/statistics/', settings_statistics, name="settingsStatistics"),
    path('settings/accessibility/', settings_accessibility, name="settingsAccessibility"),
    path('settings/api/', settings_api, name="settingsApi"),

    path('settings/access_check/', access_check),
    path('rmph/', remove_phone),
    path('rmpp/', remove_pp),
    path('rmsr/', delete_account),

    path('privacy/', privacy),
    path('password_guide/', strong_password_guide),

    path('api/v1/users/<str:username>/public/info/', api_get_public_user_info),
    path('api/v1/users/<str:username>/info/', api_get_user_info),
    path('api/v1/photos/emotions/<str:emotion>/info/', api_get_photos_of_emotion),
    path('api/v1/photos/<str:photo_name>/info/', api_get_photo),
    path('api/v1/photos/new/', api_upload_photo),
    path('api/v1/photos/emotions/new/<str:photo_name>/', api_update_emotion),
    path('api/v1/photos/db/<str:photo_name>/', api_delete_photo),
    
    re_path(fr'^{mediaUrl}/(?P<path>.*)$', serve,{ 'document_root' : settings.MEDIA_ROOT}),
    re_path(fr'^{staticUrl}/(?P<path>.*)$', serve,{ 'document_root' : settings.STATICFILES_DIRS[0]}),

    path('logout/', logout),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', redirectToMain),
    # re_path(r'^search/', app_views.viewimages, name='ind'),
]

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIR)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
