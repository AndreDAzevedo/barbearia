from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime, time


class Reserva(models.Model):
    SERVICOS = [
        ('Cabelo', 'Cabelo - R$50'),
        ('Barba', 'Barba - R$40'),
        ('Cabelo e Barba', 'Cabelo e Barba - R$70'),
    ]

    DURACAO_SERVICOS = {
        'Cabelo': timedelta(minutes=40),
        'Barba': timedelta(minutes=30),
        'Cabelo e Barba': timedelta(minutes=70),
    }

    EXPEDIENTE_INICIO = time(9, 0)  # 9:00
    EXPEDIENTE_FIM = time(19, 0)    # 19:00
    ALMOCO_INICIO = time(12, 0)     # 12:00
    ALMOCO_FIM = time(13, 0)        # 13:00

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_cliente')
    barbeiro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_barbeiro', limit_choices_to={'is_superuser': True})
    servico = models.CharField(max_length=50, choices=SERVICOS)
    data = models.DateField()
    horario = models.TimeField()

    def clean(self):
        """Validações personalizadas para reserva."""

        # Verifica se o serviço é válido
        if not self.servico or self.servico not in self.DURACAO_SERVICOS:
            raise ValidationError('Serviço inválido ou não selecionado.')

        # 1. Verifica se está dentro do horário de expediente
        if self.horario < self.EXPEDIENTE_INICIO or self.horario >= self.EXPEDIENTE_FIM:
            raise ValidationError('Reservas só podem ser feitas entre 9:00 e 19:00.')

        # 2. Verifica se está no horário de almoço
        if self.ALMOCO_INICIO <= self.horario < self.ALMOCO_FIM:
            raise ValidationError('Reservas não são permitidas durante o horário de almoço (12:00 - 13:00).')

        # 3. Calcula o horário de término
        fim_reserva = (
            datetime.combine(self.data, self.horario) + self.DURACAO_SERVICOS[self.servico]
        ).time()

        if fim_reserva > self.EXPEDIENTE_FIM:
            raise ValidationError('O horário de término da reserva ultrapassa o expediente (até 19:00).')

        # 4. Verifica conflito de horário com o mesmo barbeiro
        reservas_existentes = Reserva.objects.filter(
            data=self.data,
            barbeiro=self.barbeiro
        ).exclude(pk=self.pk)

        for reserva in reservas_existentes:
            inicio_existente = reserva.horario
            fim_existente = (
                datetime.combine(reserva.data, reserva.horario) + self.DURACAO_SERVICOS[reserva.servico]
            ).time()

            if self.horario < fim_existente and fim_reserva > inicio_existente:
                raise ValidationError(
                    f"Conflito de horário: o barbeiro '{self.barbeiro.username}' já tem uma reserva neste período."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {self.servico} - {self.data} {self.horario} com {self.barbeiro.username}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField("Mensagem")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
