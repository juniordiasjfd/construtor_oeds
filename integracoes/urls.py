from django.urls import path
from .views import ExportarOedsCSVView

urlpatterns = [
    path(
        "exportar-csv/",
        ExportarOedsCSVView.as_view(),
        name="exportar_oeds_csv",
    ),
]