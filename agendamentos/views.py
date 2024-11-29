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
locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
from .forms import RegisterForm 


# Página inicial
def home(request):
    return render(request, 'home.html')

# Registro de usuários
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
@login_required
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

@login_required
def minhas_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user)

    if request.method == 'POST' and 'cancelar_reserva' in request.POST:
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
        reserva.delete()
        messages.success(request, 'Reserva cancelada com sucesso!')
        return redirect('minhas_reservas')

    return render(request, 'minhas_reservas.html', {'reservas': reservas})

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva atualizada com sucesso!')
            return redirect('minhas_reservas')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'editar_reserva.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    """Faz o logout do usuário e redireciona para a página inicial."""
    logout(request)
    return redirect('home')  # Redireciona para a página inicial após o logout

def barbeiro_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Credenciais específicas do barbeiro
        if username == 'aluno' and password == 'engenhariaweb':
            # Crie um usuário fictício para autenticação
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username='barbeiro')
            login(request, user)  # Loga o usuário fictício
            return redirect('area_barbeiro')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'barbeiro_login.html')

@login_required
def area_barbeiro(request):
    return render(request, 'area_barbeiro.html')

@login_required
def horarios_marcados(request):
    reservas = Reserva.objects.all().order_by('data', 'horario')
    return render(request, 'horarios_marcados.html', {'reservas': reservas})

@login_required
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

@login_required
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

@login_required
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

@login_required
def area_cliente(request):
    """
    View para a área do cliente.
    """
    return render(request, 'area_cliente.html')


from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
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

@login_required
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
