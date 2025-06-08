from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from .views import custom_logout
from .views import CustomLoginView  
from .views import editar_usuario, deletar_cliente





urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('fazer_reserva/', views.fazer_reserva, name='fazer_reserva'),
    path('minhas_reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('editar_reserva_cliente/<int:reserva_id>/', views.editar_reserva_cliente, name='editar_reserva_cliente'),  # Para clientes
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('login_barbeiro/', views.barbeiro_login, name='barbeiro_login'),
    path('area_barbeiro/', views.area_barbeiro, name='area_barbeiro'),
    path('horarios_marcados/', views.horarios_marcados, name='horarios_marcados'),
    path('editar_reserva_barbeiro/<int:reserva_id>/', views.editar_reserva_barbeiro, name='editar_reserva_barbeiro'),  # Para barbeiros
    path('carregar_datas/', views.carregar_datas, name='carregar_datas'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login_success/', views.login_success, name='login_success'),
    path('area_cliente/', views.area_cliente, name='area_cliente'),
    path('minha_conta/', views.minha_conta, name='minha_conta'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/new/', views.give_feedback, name='give_feedback'),
     path('feedbacks/', views.list_feedbacks, name='feedbacks'),
    path('feedbacks/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('feedback/total/', views.feedback_total, name='feedback_total'),
    
    path('editar_usuario/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('deletar_cliente/<int:user_id>/', deletar_cliente, name='deletar_cliente'),

    path('area_gestor/', views.area_gestor, name='area_gestor'),
    path('criar_barbeiro/', views.criar_barbeiro, name='criar_barbeiro'),
    path('deletar_barbeiro/<int:user_id>/', views.deletar_barbeiro, name='deletar_barbeiro'),

    path('redirect/', views.redirecionar_usuario, name='redirect_usuario'),

    path('cancelar_reserva_barbeiro/<int:reserva_id>/', views.cancelar_reserva_barbeiro, name='cancelar_reserva_barbeiro'),
    path('politica-seguranca/', views.politica_seguranca, name='politica_seguranca'),
    path('politica-privacidade/', views.politica_privacidade, name='politica_privacidade'),

    # Cliente
path('editar_reserva_cliente/<int:reserva_id>/', views.editar_reserva_cliente, name='editar_reserva_cliente'),

# Gestor
path('editar_reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),

]

