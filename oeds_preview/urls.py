from django.urls import path
from .views import OedPreviewDetailView

app_name = 'oeds_preview'

urlpatterns = [
    path('<int:pk>/', OedPreviewDetailView.as_view(), name='oed_preview'),
]