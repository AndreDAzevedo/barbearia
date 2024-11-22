from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reserva

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['servico', 'data', 'horario']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'servico': 'Serviço',
            'data': 'Data',
            'horario': 'Horário',
        }
