import os
import sys
from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.servers.basehttp import WSGIServer
import ssl

class Command(RunserverCommand):
    help = 'Runs the development server with SSL support.'

    def handle(self, *args, **options):
        self.cert_file = os.path.join('certificates', 'barbearia.crt')
        self.key_file = os.path.join('certificates', 'barbearia.key')

        if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
            self.stderr.write(self.style.ERROR(
                'Certificate files not found. Please generate them first.'))
            sys.exit(1)

        options['addrport'] = '0.0.0.0:8000'
        super().handle(*args, **options)

    def inner_run(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            f'Starting development server at https://{options["addrport"]}/'))
        self.stdout.write(self.style.SUCCESS(
            f'Using SSL certificate: {self.cert_file}'))
        self.stdout.write(self.style.SUCCESS(
            f'Using SSL key: {self.key_file}'))

        WSGIServer.socket = ssl.wrap_socket(
            WSGIServer.socket,
            certfile=self.cert_file,
            keyfile=self.key_file,
            server_side=True
        )

        super().inner_run(*args, **options) 