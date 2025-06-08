from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import Reserva
from .forms import ReservaForm
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from datetime import date, timedelta
import locale
import os
import locale
from django.views.decorators.csrf import ensure_csrf_cookie
from functools import wraps
from django.conf import settings

# Decorador personalizado para forçar HTTPS
def require_https(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            return redirect(secure_url, permanent=True)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Em desenvolvimento, não forçamos HTTPS
if settings.DEBUG:
    def require_https(view_func):
        return view_func

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "C")

from .forms import RegisterForm 


from django.contrib.auth.decorators import login_required

from .models import Feedback

def home(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')[:3]  # Apenas os 5 mais recentes
    return render(request, 'home.html', {'feedbacks': feedbacks})

# Registro de usuários
@require_https
@ensure_csrf_cookie
def register(request):
    """
    View para registrar um novo usuário.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # Adiciona uma mensagem na sessão para a página de sucesso
            request.session['registration_success'] = 'Usuário registrado com sucesso! Faça login para continuar.'
            return redirect('login_success')  # Redireciona para a página de sucesso
        else:
            messages.error(request, 'Houve um erro ao tentar registrar. Verifique os dados e tente novamente.')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})


from django.contrib.auth.views import LoginView

@require_https
@ensure_csrf_cookie
class CustomLoginView(LoginView):
    """
    View personalizada para login que verifica e remove a mensagem de sucesso da sessão.
    """
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'registration_success' in self.request.session:
            context['registration_success'] = self.request.session.pop('registration_success')
        return context


# Fazer reserva
@require_https
@login_required
@ensure_csrf_cookie
def fazer_reserva(request):
    today = date.today()
    dates = [today + timedelta(days=i) for i in range(30)]  # Exemplo: 30 dias
    reservas = Reserva.objects.values_list('data', flat=True)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            try:
                reserva.save()
                messages.success(request, 'Reserva realizada com sucesso!')
                return redirect('minhas_reservas')
            except ValidationError as e:
                # Captura erros de validação e exibe como mensagem no frontend
                messages.error(request, e.message)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = ReservaForm()

    return render(request, 'fazer_reserva.html', {
        'form': form,
        'dates': dates,
        'reservas': reservas,
    })

    # Formatar as datas antes de enviá-las para o template
    formatted_dates = [
        {
            "date": d.isoformat(),  # Data no formato 'YYYY-MM-DD' para o atributo `data-date`
            "formatted": d.strftime("%d de %B")  # Data formatada para exibição
        }
        for d in dates
    ]

    return render(request, 'fazer_reserva.html', {
        'form': form,
        'dates': formatted_dates,
        'reservas': [r.isoformat() for r in reservas],  # Garantir o mesmo formato para comparação
    })


# Login de usuários (usando a LoginView do Django)
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    """
    View personalizada para login.
    """
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('login_success')  # Redireciona para a página de sucesso


# Login manual (opcional)
def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('fazer_reserva')  # Redireciona após login
        else:
            messages.error(request, 'Credenciais inválidas. Tente novamente.')
    return render(request, 'login.html')

@require_https
@login_required
@ensure_csrf_cookie
def minhas_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user)

    if request.method == 'POST' and 'cancelar_reserva' in request.POST:
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
        reserva.delete()
        messages.success(request, 'Reserva cancelada com sucesso!')
        return redirect('minhas_reservas')

    return render(request, 'minhas_reservas.html', {'reservas': reservas})

@require_https
@login_required
@ensure_csrf_cookie
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Apenas o gestor ou o próprio cliente pode editar
    if request.user != reserva.usuario and request.user.username != 'gestor':
        messages.error(request, 'Você não tem permissão para editar essa reserva.')
        return redirect('minhas_reservas')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva atualizada com sucesso!')
            if request.user.username == 'gestor':
                return redirect('area_gestor')
            else:
                return redirect('minhas_reservas')
    else:
        form = ReservaForm(instance=reserva)

    barbeiros = User.objects.filter(is_superuser=True).exclude(username='gestor')
    return render(request, 'editar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'barbeiros': barbeiros
    })


from django.contrib.auth import logout
from django.shortcuts import redirect

@require_https
def logout_view(request):
    """Faz o logout do usuário e redireciona para a página inicial."""
    logout(request)
    return redirect('home')  # Redireciona para a página inicial após o logout

@require_https
@ensure_csrf_cookie
def barbeiro_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Usa o sistema de autenticação do Django
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            if user.username == 'gestor':
                return redirect('area_gestor')
            else:
                return redirect('area_barbeiro')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'barbeiro_login.html')

@require_https
@login_required
@ensure_csrf_cookie
def area_barbeiro(request):
    return render(request, 'area_barbeiro.html')

@require_https
@login_required
@ensure_csrf_cookie
def horarios_marcados(request):
    if request.user.is_superuser and request.user.username != 'gestor':
        # barbeiro comum: vê apenas suas reservas
        reservas = Reserva.objects.filter(barbeiro=request.user).order_by('data', 'horario')
    elif request.user.username == 'gestor':
        # gestor já tem a área dele, então redirecionamos
        return redirect('area_gestor')
    else:
        # cliente não deve acessar
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')

    return render(request, 'horarios_marcados.html', {'reservas': reservas})

@require_https
@login_required
@ensure_csrf_cookie
def editar_reserva_barbeiro(request, reserva_id):
    reserva = Reserva.objects.get(pk=reserva_id)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva editada com sucesso!')
            return redirect('horarios_marcados')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'editar_reserva_barbeiro.html', {'form': form, 'reserva': reserva})

@require_https
@login_required
@ensure_csrf_cookie
def cancelar_reserva_barbeiro(request, reserva_id):
    reserva = Reserva.objects.get(pk=reserva_id)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva cancelada com sucesso!')
        return redirect('horarios_marcados')
    return render(request, 'cancelar_reserva_barbeiro.html', {'reserva': reserva})

def custom_logout(request):
    logout(request)
    return redirect(reverse('home'))  # Redirecione para a página 'home'

from django.http import JsonResponse
from datetime import date, timedelta

@require_https
@login_required
@ensure_csrf_cookie
def carregar_datas(request):
    year = int(request.GET.get("year"))
    month = int(request.GET.get("month"))
    first_day = date(year, month, 1)
    last_day = (first_day.replace(month=month+1) if month < 12 else first_day.replace(year=year+1, month=1)) - timedelta(days=1)

    # Gerar lista de datas e reservas no mês
    dates = []
    current_day = first_day
    while current_day <= last_day:
        dates.append({
            "date": current_day.isoformat(),
            "formatted": current_day.strftime("%d de %B"),
        })
        current_day += timedelta(days=1)

    reservas = Reserva.objects.filter(data__month=month, data__year=year).values_list('data', flat=True)

    return JsonResponse({
        "dates": dates,
        "reservas": [r.isoformat() for r in reservas],
    })

from django.shortcuts import render


def login_success(request):
    """
    Página de sucesso exibida após o login bem-sucedido.
    """
    return render(request, 'login_success.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@require_https
@login_required
@ensure_csrf_cookie
def area_cliente(request):
    """
    View para a área do cliente.
    """
    return render(request, 'area_cliente.html')


from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@require_https
@login_required
@ensure_csrf_cookie
def minha_conta(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suas informações foram atualizadas com sucesso!')
            return redirect('minha_conta')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'minha_conta.html', {'form': form})

from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserEditForm

@require_https
@login_required
@ensure_csrf_cookie
def minha_conta(request):
    user_form = UserEditForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_info' in request.POST:  # Atualizar informações do usuário
            user_form = UserEditForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Suas informações foram atualizadas com sucesso!')
                return redirect('minha_conta')
            else:
                messages.error(request, 'Corrija os erros abaixo.')
        elif 'change_password' in request.POST:  # Alterar senha
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantém o usuário logado após mudar a senha
                messages.success(request, 'Sua senha foi alterada com sucesso!')
                return redirect('minha_conta')
            else:
                messages.error(request, 'Corrija os erros abaixo.')

    return render(request, 'minha_conta.html', {
        'user_form': user_form,
        'password_form': password_form,
    })

from .models import Feedback
from .forms import FeedbackForm

def feedback_list(request):
    """
    Exibe a lista de feedbacks públicos.
    """
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'feedback_list.html', {'feedbacks': feedbacks})

@require_https
@login_required
@ensure_csrf_cookie
def give_feedback(request):
    """
    Permite que usuários logados enviem feedbacks.
    """
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Seu feedback foi enviado com sucesso!')
            return redirect('feedback_list')  # Redireciona para a lista de feedbacks
    else:
        form = FeedbackForm()

    return render(request, 'give_feedback.html', {'form': form})


@require_https
@login_required
@ensure_csrf_cookie
def list_feedbacks(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'feedbacks.html', {'feedbacks': feedbacks})

@require_https
@login_required
@ensure_csrf_cookie
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    return redirect('feedbacks')


@require_https
@login_required
@ensure_csrf_cookie
def feedback_total(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Seu feedback foi enviado com sucesso!')
            return redirect('feedback_total')
    else:
        form = FeedbackForm()
    return render(request, 'feedback_total.html', {'form': form, 'feedbacks': feedbacks})

def politica_seguranca(request):
    """
    View para exibir a política de segurança do site.
    """
    return render(request, 'politica_seguranca.html')

def politica_privacidade(request):
    """
    View para exibir a política de privacidade do site.
    """
    return render(request, 'politica_privacidade.html')


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Reserva

def eh_superusuario(user):
    return user.is_superuser

@require_https
@user_passes_test(eh_superusuario)
def area_gestor(request):
    barbeiros = User.objects.filter(is_superuser=True)
    reservas = Reserva.objects.all().select_related('barbeiro')
    return render(request, 'area_gestor.html', {'barbeiros': barbeiros, 'reservas': reservas})


from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404

@require_https
@user_passes_test(eh_superusuario)
def criar_barbeiro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        if username and senha:
            User.objects.create_user(username=username, password=senha, is_superuser=True)
            return redirect('area_gestor')
    return render(request, 'criar_barbeiro.html')


@require_https
@user_passes_test(eh_superusuario)
def deletar_barbeiro(request, user_id):
    barbeiro = get_object_or_404(User, id=user_id, is_superuser=True)
    if barbeiro.username != 'gestor':  # Protege o gestor principal
        barbeiro.delete()
    return redirect('area_gestor')

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Reserva

def eh_superusuario(user):
    return user.is_superuser

@user_passes_test(eh_superusuario)
def area_gestor(request):
    barbeiros = User.objects.filter(is_superuser=True)
    reservas = Reserva.objects.all().select_related('barbeiro')
    return render(request, 'area_gestor.html', {
        'barbeiros': barbeiros,
        'reservas': reservas
    })

def eh_gestor(user):
    return user.is_authenticated and user.is_superuser

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Reserva

from .models import Reserva, Feedback

@user_passes_test(eh_gestor)
def area_gestor(request):
    barbeiros = User.objects.filter(is_superuser=True).exclude(username='gestor')
    clientes = User.objects.filter(is_superuser=False)
    reservas = Reserva.objects.all().select_related('barbeiro', 'usuario')
    feedbacks = Feedback.objects.select_related('user').order_by('-created_at')

    return render(request, 'area_gestor.html', {
        'barbeiros': barbeiros,
        'clientes': clientes,
        'reservas': reservas,
        'feedbacks': feedbacks,
    })


@user_passes_test(eh_gestor)
def criar_barbeiro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        if username and senha:
            User.objects.create_user(username=username, password=senha, is_superuser=True)
            return redirect('area_gestor')
    return render(request, 'criar_barbeiro.html')

@user_passes_test(eh_gestor)
def deletar_barbeiro(request, user_id):
    barbeiro = get_object_or_404(User, id=user_id, is_superuser=True)
    if barbeiro.username != 'gestor':  # impede deletar o próprio gestor
        barbeiro.delete()
    return redirect('area_gestor')

@user_passes_test(eh_gestor)
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    barbeiros = User.objects.filter(is_superuser=True).exclude(username='gestor')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva atualizada com sucesso!')
            return redirect('area_gestor')
    else:
        form = ReservaForm(instance=reserva)

    return render(request, 'editar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'barbeiros': barbeiros,
    })


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirecionar_usuario(request):
    if request.user.username == 'gestor':
        return redirect('area_gestor')
    elif request.user.is_superuser:
        return redirect('area_barbeiro')
    else:
        return redirect('area_cliente')

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

@user_passes_test(eh_gestor)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('area_gestor')
    else:
        form = UserChangeForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form, 'usuario': usuario})


@user_passes_test(eh_gestor)
def deletar_cliente(request, user_id):
    usuario = get_object_or_404(User, id=user_id, is_superuser=False)
    usuario.delete()
    return redirect('area_gestor')

@require_https
@login_required
@ensure_csrf_cookie
def editar_reserva_cliente(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.user != reserva.usuario:
        messages.error(request, 'Você não tem permissão para editar essa reserva.')
        return redirect('minhas_reservas')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva atualizada com sucesso!')
            return redirect('minhas_reservas')
    else:
        form = ReservaForm(instance=reserva)

    return render(request, 'editar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'barbeiros': None,  # pode esconder esse campo no template se quiser
    })