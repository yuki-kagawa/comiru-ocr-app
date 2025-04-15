from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'ocr'

urlpatterns = [
    path('img_upload/', views.img_upload, name='img_upload'),
    path('', views.dashboard, name='dashboard')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)