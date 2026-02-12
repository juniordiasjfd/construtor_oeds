from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario  # Importe o SEU modelo aqui

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que aparecerão na lista do Admin
    list_display = ('username', 'email', 'is_staff', 'is_active')
    
    # Interface para gerenciar grupos (as duas caixas laterais que você pediu)
    filter_horizontal = ('groups', 'user_permissions')
    
    # Organização dos campos ao editar o usuário
    fieldsets = UserAdmin.fieldsets