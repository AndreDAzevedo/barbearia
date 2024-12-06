from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from .views import custom_logout
from .views import CustomLoginView



urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('fazer_reserva/', views.fazer_reserva, name='fazer_reserva'),
    path('minhas_reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('editar_reserva_cliente/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),  # Para clientes
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




    path('cancelar_reserva_barbeiro/<int:reserva_id>/', views.cancelar_reserva_barbeiro, name='cancelar_reserva_barbeiro'),
]

