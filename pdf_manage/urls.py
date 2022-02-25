from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='pdf_manage-home'),
    path('about/', views.about, name='pdf_manage-about'),
    path('upload/', views.upload_multiple_files, name='pdf_manage-fileupload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

