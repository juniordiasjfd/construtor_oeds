from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Registro de Usuário
    path('registrar/', views.UsuarioCreate.as_view(), name='registrar'),
    path('registrar/sucesso/', views.UsuarioCreateDone.as_view(), name='registrar_done'),

    # Solução para o erro 404: Redireciona chamadas automáticas do Django para sua rota correta
    path('accounts/login/', RedirectView.as_view(pattern_name='login', permanent=True)),

    # Fluxo de Recuperação de Senha (Nomes e caminhos padronizados)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Gerenciamento (Coordenador)
    path('gerenciar/todos/', views.UsuarioListarTodosView.as_view(), name='gerenciar_usuarios_todos'),
    path('gerenciar/aprovar/<int:pk>/', views.UsuarioAprovarView.as_view(), name='aprovar_usuario'),
]