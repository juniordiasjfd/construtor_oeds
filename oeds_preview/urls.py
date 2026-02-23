from django.urls import path
from .views import OedPreviewDetailView, OedDownloadZipView, OedDownloadPDFView

app_name = 'oeds_preview'

urlpatterns = [
    path('<int:pk>/', OedPreviewDetailView.as_view(), name='oed_preview'),
    path('<int:pk>/download/', OedDownloadZipView.as_view(), name='oed_download_zip'),
    path('<int:pk>/download-pdf/', OedDownloadPDFView.as_view(), name='oed_download_pdf'),
]