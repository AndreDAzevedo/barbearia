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


# Página inicial
def home(request):
    return render(request, 'home.html')

# Registro de usuários
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário registrado com sucesso! Faça login para continuar.')
            return redirect('login')  # Redireciona para a página de login
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

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
class CustomLoginView(LoginView):
    template_name = 'login.html'

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