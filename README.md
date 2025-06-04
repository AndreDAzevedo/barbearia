# Sistema de Agendamento para Barbearia

## Configuração do Ambiente

### 1. Instalação das Dependências
```bash
pip install django
pip install django-sslserver
pip install django-extensions
pip install crispy-forms
pip install crispy-bootstrap5
pip install whitenoise
pip install dj-database-url
```

### 2. Configuração do SSL

#### 2.1 Gerar Certificados SSL
```bash
# Criar diretório para certificados
mkdir certificates

# Gerar chave privada
openssl genrsa -out certificates/barbearia.key 2048

# Gerar CSR (Certificate Signing Request)
openssl req -new -key certificates/barbearia.key -out certificates/barbearia.csr

# Gerar certificado auto-assinado
openssl x509 -req -days 365 -in certificates/barbearia.csr -signkey certificates/barbearia.key -out certificates/barbearia.crt
```

#### 2.2 Configurações de Segurança
O projeto está configurado com as seguintes políticas de segurança:

- Todas as páginas são HTTPS por padrão
- Páginas de política de segurança e privacidade são HTTP
- Cookies seguros habilitados para HTTPS
- Proteção CSRF habilitada
- Proteção XSS habilitada
- HSTS desabilitado para permitir HTTP nas páginas de política

### 3. Configuração do Nginx

#### 3.1 Estrutura de Arquivos
```
.
├── Dockerfile.nginx
├── nginx.conf
├── certificates/
│   ├── barbearia.crt
│   └── barbearia.key
└── docker-compose.yml
```

#### 3.2 Configuração do Nginx
O Nginx está configurado para:
- Servir o site via HTTPS na porta 443
- Redirecionar automaticamente HTTP para HTTPS
- Manter páginas de política em HTTP
- Proxy reverso para o servidor Django

#### 3.3 Executando com Docker
```bash
# Construir e iniciar os containers
docker-compose up --build

# Executar em background
docker-compose up -d

# Parar os containers
docker-compose down
```

#### 3.4 Portas
- HTTP: 80
- HTTPS: 443

#### 3.5 Certificados
Os certificados SSL devem ser colocados no diretório `certificates/`:
- `barbearia.crt`: Certificado SSL
- `barbearia.key`: Chave privada

### 4. Executando o Servidor

#### 4.1 Modo de Desenvolvimento
```bash
# Servidor normal (HTTP)
python manage.py runserver

# Servidor com SSL (HTTPS)
python manage.py runserver_plus --cert-file certificates/barbearia.crt --key-file certificates/barbearia.key
```

### 5. Páginas e Protocolos

#### 5.1 Páginas HTTPS (Protegidas)
- Login/Autenticação
- Registro de usuários
- Área do cliente
- Área do barbeiro
- Agendamentos
- Minha conta
- Feedback e avaliações

#### 5.2 Páginas HTTP (Não Protegidas)
- Política de segurança
- Política de privacidade

### 6. Configurações de Formulários
O projeto utiliza:
- crispy-forms para formulários mais bonitos
- crispy-bootstrap5 como template pack

### 7. Configurações de Banco de Dados
- Suporte a PostgreSQL via dj-database-url
- Fallback para SQLite em desenvolvimento

### 8. Configurações de Sessão
- Cookies seguros habilitados
- Timeout de sessão: 2 horas
- Sessão expira ao fechar o navegador
- Proteção CSRF habilitada

### 9. Observações Importantes
1. Em produção, use certificados emitidos por uma Autoridade Certificadora confiável
2. Mantenha suas chaves privadas seguras
3. Configure o servidor web (Apache/Nginx) para redirecionar automaticamente as páginas sensíveis para HTTPS
4. Mantenha seus certificados atualizados
5. Em produção, ajuste as configurações de segurança conforme necessário