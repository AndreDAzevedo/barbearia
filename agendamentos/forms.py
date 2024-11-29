from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reserva


class RegisterForm(UserCreationForm):
    """
    Formulário para registro de novos usuários.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Insira um endereço de e-mail válido.',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': None,  # Remove o texto de ajuda padrão do campo username
            'password1': None,  # Remove o texto de ajuda padrão do campo password1
            'password2': None,  # Remove o texto de ajuda padrão do campo password2
        }


class ReservaForm(forms.ModelForm):
    """
    Formulário para gerenciamento de reservas de serviços.
    """
    class Meta:
        model = Reserva
        fields = ['servico', 'data', 'horario']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'servico': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'servico': 'Serviço',
            'data': 'Data',
            'horario': 'Horário',
        }


class UserEditForm(forms.ModelForm):
    """
    Formulário personalizado para permitir que os usuários editem informações relevantes da conta.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail',
            'first_name': 'Primeiro Nome',
            'last_name': 'Último Nome',
        }
