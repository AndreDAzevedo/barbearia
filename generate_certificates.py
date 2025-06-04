import os
from OpenSSL import crypto

def generate_self_signed_cert():
    # Cria o diretório de certificados se não existir
    if not os.path.exists('certificates'):
        os.makedirs('certificates')

    # Gera uma chave privada
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # Cria um certificado auto-assinado
    cert = crypto.X509()
    cert.get_subject().C = "BR"
    cert.get_subject().ST = "São Paulo"
    cert.get_subject().L = "São Paulo"
    cert.get_subject().O = "Barbearia"
    cert.get_subject().OU = "Desenvolvimento"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Válido por 1 ano
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # Salva o certificado
    with open("certificates/barbearia.crt", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    # Salva a chave privada
    with open("certificates/barbearia.key", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    print("Certificados gerados com sucesso em 'certificates/'")

if __name__ == '__main__':
    generate_self_signed_cert() 