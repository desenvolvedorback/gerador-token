import jwt
import sys
import base64
from cryptography.fernet import Fernet

# EXEMPLO DE DADO CRUCIAL DO SEU SAAS CRIPTOGRAFADO (Pode ser uma URL, token de API, etc.)
# Sem um token válido, isso aqui é apenas lixo ilegível.
DADOS_VITAIS_CRIPTOGRAFADOS = b'gAAAAABmN_X...[Seu bloco de dados altamente secreto aqui]...'

def verificar_e_desbloquear(token_usuario):
    try:
        # 1. Decodifica o JWT usando o segredo definido no seu Termux
        payload = jwt.decode(token_usuario, "SEGREDO_MESTRE_SUPER_SEGURO", algorithms=["HS256"])
        
        # 2. Verifica se o status vindo do payload está ativo
        # (Em uma arquitetura robusta, você pode fazer um fetch numa API/JSON antes de validar)
        if payload.get("status") != "active":
            print("[-] ERRO: Licença inativa, excluída ou revogada.")
            sys.exit(1)
            
        # 3. ANTI-TAMPER: Usa os últimos 32 caracteres do token como chave criptográfica
        # Se o invasor tentar burlar o 'if' acima forçando o código a continuar,
        # a linha abaixo vai falhar catastroficamente porque a chave derivada estará errada.
        chave_derivada = base64.urlsafe_b64encode(token_usuario[-32:].encode())
        fernet = Fernet(chave_derivada)
        
        dados_desbloqueados = fernet.decrypt(DADOS_VITAIS_CRIPTOGRAFADOS).decode()
        return dados_desbloqueados

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        print("[-] ERRO: Token expirado ou assinatura digital corrompida/falsificada.")
        sys.exit(1)
    except Exception:
        print("[-] ERRO CRÍTICO: Código incompleto ou integridade violada!")
        sys.exit(1)

if __name__ == "__main__":
    token = input("Insira seu token de acesso: ").strip()
    
    # O SaaS só ganha vida se a função injetar as variáveis descriptografadas
    CONFIG_VITAL = verificar_e_desbloquear(token)
    
    print("[+] Validação com sucesso! Iniciando rotinas...")
    # Execução do seu SaaS usando a CONFIG_VITAL...
