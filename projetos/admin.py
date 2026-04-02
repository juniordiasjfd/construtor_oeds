from django.contrib import admin
from .models import StatusOed
from .models import Dashboard


@admin.register(StatusOed)
class StatusOedAdmin(admin.ModelAdmin):
    # Campos que aparecerão na lista do Admin
    list_display = ('nome', 'only_coordenador_can_edit')
    search_fields = ('nome',)
    list_filter = ('only_coordenador_can_edit',)
    ordering = ('nome',)

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    search_fields = ("nome",)



