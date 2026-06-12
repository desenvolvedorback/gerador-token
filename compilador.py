import base64
import os
from cryptography.fernet import Fernet

def blindar_projeto():
    print("--- 🛡️ COMPILADOR DE BLINDAGEM SaaS 🛡️ ---")
    
    # 1. Configurações Iniciais
    arquivo_original = input("Nome do arquivo original (ex: meu_script.py): ")
    if not os.path.exists(arquivo_original):
        print("[-] Erro: Arquivo original não encontrado.")
        return

    token_alvo = input("Insira o TOKEN gerado no Termux para este cliente: ").strip()
    
    # 2. Gerar a Chave de Criptografia baseada no Token
    # Usamos os últimos 32 caracteres do token para criar uma chave Fernet válida
    try:
        chave_derivada = base64.urlsafe_b64encode(token_alvo[-32:].encode())
        fernet = Fernet(chave_derivada)
    except Exception as e:
        print(f"[-] Erro ao derivar chave do token: {e}")
        return

    # 3. Ler e Criptografar o código original
    with open(arquivo_original, "r", encoding="utf-8") as f:
        codigo_puro = f.read()
    
    codigo_criptografado = fernet.encrypt(codigo_puro.encode())

    # 4. Construir o Arquivo Final (O que vai para a nuvem)
    # Aqui montamos o Bloco Barreira + O código blindado
    template_blindado = f'''# -*- coding: utf-8 -*-
import jwt, requests, time, threading, sys, base64
from cryptography.fernet import Fernet

# ==========================================================
# BLOCO BARREIRA DE PROTEÇÃO (ANTI-TAMPER & KILL-SWITCH)
# ==========================================================
TOKEN_LICENCA = "{token_alvo}"
SECRET_MESTRE = "SEGREDO_MESTRE_SUPER_SEGURO"
URL_STATUS = "https://sua-api.com/check" # Opcional: Se for usar check online

def _check_loop():
    while True:
        try:
            # Aqui você pode adicionar uma checagem via requests em um JSON online
            # Se status != 'active', sys.exit(1)
            time.sleep(300)
        except: sys.exit(1)

def _protecao_total():
    try:
        # 1. Valida Assinatura do Token
        payload = jwt.decode(TOKEN_LICENCA, SECRET_MESTRE, algorithms=["HS256"])
        if payload.get("status") != "active":
            print("[-] LICENCA INVALIDA OU EXPIRADA"); sys.exit(1)
        
        # 2. Inicia Kill-Switch em segundo plano
        threading.Thread(target=_check_loop, daemon=True).start()
        
        # 3. Deriva chave e desbloqueia o resto do arquivo
        _k = base64.urlsafe_b64encode(TOKEN_LICENCA[-32:].encode())
        return Fernet(_k)
    except:
        print("[-] ERRO CRITICO: CODIGO INCOMPLETO OU VIOLADO"); sys.exit(1)

_f = _protecao_total()
# ==========================================================

# MASSA DE BYTES CRIPTOGRAFADA (O SEU codigo ESTÁ AQUI DENTRO)
_DADOS_BLINDADOS = {codigo_criptografado}

try:
    exec(_f.decrypt(_DADOS_BLINDADOS).decode())
except Exception as e:
    print("[-] ERRO DE INTEGRIDADE"); sys.exit(1)
'''

    # 5. Salvar o arquivo final
    nome_saida = "projeto_blindado.py"
    with open(nome_saida, "w", encoding="utf-8") as f:
        f.write(template_blindado)

    print(f"\n[+] SUCESSO! Arquivo '{nome_saida}' gerado.")
    print("[!] Se alguém remover o topo do arquivo, o '_DADOS_BLINDADOS' vira lixo ilegível.")
    print("[!] Se o Token for alterado, a chave de descriptografia quebra.")

if __name__ == "__main__":
    blindar_projeto()
