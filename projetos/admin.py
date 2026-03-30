from django.contrib import admin
from .models import StatusOed

@admin.register(StatusOed)
class StatusOedAdmin(admin.ModelAdmin):
    # Campos que aparecerão na lista do Admin
    list_display = ('nome', 'only_coordenador_can_edit')
    search_fields = ('nome',)
    list_filter = ('only_coordenador_can_edit',)
    ordering = ('nome',)