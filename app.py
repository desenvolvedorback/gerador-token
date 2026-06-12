from flask import Flask, render_template_string, request, redirect, url_for
import jwt
import datetime
import os
import json
import uuid

app = Flask(__name__)

DB_FILE = "chaves.json"

def carregar_chaves():
    """Carrega as chaves do arquivo JSON. Se não existir ou estiver vazio, retorna lista vazia."""
    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def salvar_chaves(chaves):
    """Salva a lista de chaves formatada como JSON indentado (estilo bonito)."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(chaves, f, indent=4, ensure_ascii=False)

# --- INTERFACE WEB COMPLETA COM FILTRO E BOTÃO DE COPIAR ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Gerenciador de Licenças SaaS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121214; color: #e1e1e6; padding: 30px; margin: 0; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1, h2 { color: #fff; }
        .card { background: #202024; padding: 25px; border-radius: 8px; border: 1px solid #29292e; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #a8a8b3; }
        input, select, .search-bar { padding: 10px; width: 100%; background: #121214; border: 1px solid #29292e; color: white; border-radius: 4px; box-sizing: border-box; }
        input:focus, .search-bar:focus { border-color: #04d361; outline: none; }
        
        .btn { padding: 10px 15px; border: none; cursor: pointer; border-radius: 4px; text-decoration: none; display: inline-block; font-weight: bold; font-size: 14px; }
        .btn-green { background: #04d361; color: #000; }
        .btn-green:hover { background: #029443; }
        .btn-red { background: #df4646; color: white; }
        .btn-red:hover { background: #c73232; }
        .btn-warning { background: #e1b12c; color: black; }
        .btn-copy { background: #4b6584; color: white; padding: 5px 10px; font-size: 12px; margin-left: 5px; }
        .btn-copy:active { background: #a5b1c2; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 15px; border: 1px solid #29292e; text-align: left; }
        th { background: #29292e; color: #04d361; }
        tr:nth-child(even) { background: #1a1a1e; }
        
        .token-box { 
            background: #121214; 
            padding: 8px; 
            border-radius: 4px; 
            font-family: monospace; 
            font-size: 12px; 
            color: #ff79c6; 
            word-break: break-all; 
            max-width: 400px;
            display: inline-block;
            vertical-align: middle;
        }
        .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
        .status-active { background: rgba(4, 211, 97, 0.2); color: #04d361; }
        .status-desativada { background: rgba(225, 177, 44, 0.2); color: #e1b12c; }
        .status-excluida { background: rgba(223, 70, 70, 0.2); color: #df4646; }
        .status-nao-usada { background: rgba(52, 152, 219, 0.2); color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Painel de Controle de Chaves Elites</h1>
        
        <div class="card">
            <h2>Gerar Nova Chave</h2>
            <form action="/gerar" method="POST">
                <div class="form-group">
                    <label>Nome do Cliente / Projeto:</label>
                    <input type="text" name="nome" required placeholder="Ex: Client VIP - Joao">
                </div>
                <div class="form-group">
                    <label>Descrição:</label>
                    <input type="text" name="descricao" placeholder="Ex: Acesso ao bot de automação">
                </div>
                <div class="form-group">
                    <label>Tempo de Validade (Dias - Digite 0 para Vitalício/Infinito):</label>
                    <input type="number" name="tempo" value="30" min="0" required>
                </div>
                <button type="submit" class="btn btn-green">Gerar Token Assinado</button>
            </form>
        </div>

        <div class="card">
            <h2>Chaves Cadastradas</h2>
            <div class="form-group">
                <input type="text" id="inputPesquisa" class="search-bar" onkeyup="filtrarChaves()" placeholder="🔍 Digite para pesquisar por Nome, Descrição ou Status...">
            </div>

            <table id="tabelaChaves">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Descrição</th>
                        <th>Status</th>
                        <th>Validade</th>
                        <th>Chave Completa (Token)</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in chaves %}
                    <tr class="linha-chave">
                        <td class="busca-nome"><strong>{{ c.nome }}</strong></td>
                        <td class="busca-desc">{{ c.descricao }}</td>
                        <td class="busca-status">
                            <span class="status-badge status-{{ c.status.replace(' ', '-') }}">{{ c.status }}</span>
                        </td>
                        <td>{{ c.validade }}</td>
                        <td>
                            <span class="token-box" id="token-{{ c.id }}">{{ c.token }}</span>
                            <button class="btn btn-copy" onclick="copiarToken('token-{{ c.id }}')">Copiar</button>
                        </td>
                        <td>
                            <div style="display: flex; gap: 5px;">
                                <a href="/alterar/{{ c.id }}/active" class="btn btn-green" style="padding: 5px 10px; font-size:12px;">Ativar</a>
                                <a href="/alterar/{{ c.id }}/desativada" class="btn btn-warning" style="padding: 5px 10px; font-size:12px;">Desativar</a>
                                <a href="/deletar/{{ c.id }}" class="btn btn-red" style="padding: 5px 10px; font-size:12px;">Deletar</a>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Função de Cópia com 1 Clique
        function copiarToken(idElemento) {
            const texto = document.getElementById(idElemento).innerText;
            navigator.clipboard.writeText(texto).then(() => {
                alert("Chave copiada para a área de transferência!");
            }).catch(err => {
                console.error('Erro ao copiar: ', err);
            });
        }

        // Sistema de Busca/Filtro Dinâmico em tempo real
        function filtrarChaves() {
            const input = document.getElementById("inputPesquisa").value.toLowerCase();
            const linhas = document.getElementsByClassName("linha-chave");

            for (let i = 0; i < linhas.length; i++) {
                const nome = linhas[i].querySelector(".busca-nome").innerText.toLowerCase();
                const desc = linhas[i].querySelector(".busca-desc").innerText.toLowerCase();
                const status = linhas[i].querySelector(".busca-status").innerText.toLowerCase();

                if (nome.includes(input) || desc.includes(input) || status.includes(input)) {
                    linhas[i].style.display = "";
                } else {
                    linhas[i].style.display = "none";
                }
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    chaves = carregar_chaves()
    return render_template_string(HTML_TEMPLATE, chaves=chaves)

@app.route('/gerar', methods=['POST'])
def gerar():
    nome = request.form['nome']
    descricao = request.form['descricao']
    tempo = int(request.form['tempo'])
    
    id_unico = str(uuid.uuid4())[:8]
    
    if tempo == 0:
        validade_str = "Infinito"
        exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=36500)
    else:
        exp_date = datetime.datetime.utcnow() + datetime.timedelta(days=tempo)
        validade_str = exp_date.strftime("%Y-%m-%d %H:%M")

    # Criando as claims do JWT
    payload = {
        "id": id_unico,
        "status": "nao usada",
        "exp": exp_date
    }
    
    # Assina o Token (Utilize sua secret ou chave RSA aqui)
    token = jwt.encode(payload, "SEGREDO_MESTRE_SUPER_SEGURO", algorithm="HS256")

    chaves = carregar_chaves()
    chaves.append({
        "id": id_unico,
        "nome": nome,
        "descricao": descricao,
        "status": "nao usada",
        "validade": validade_str,
        "token": token
    })
    
    salvar_chaves(chaves)
    return redirect(url_for('index'))

@app.route('/alterar/<id_chave>/<novo_status>')
def alterar_status(id_chave, novo_status):
    chaves = carregar_chaves()
    for c in chaves:
        if c['id'] == id_chave:
            # Trava de Segurança: Uma vez ativada (active), não pode voltar a ser "não usada"
            if c['status'] == 'active' and novo_status == 'nao usada':
                continue
            c['status'] = novo_status
    salvar_chaves(chaves)
    return redirect(url_for('index'))

@app.route('/deletar/<id_chave>')
def deletar(id_chave):
    chaves = carregar_chaves()
    chaves = [c for c in chaves if c['id'] != id_chave]
    salvar_chaves(chaves)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Roda localmente na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
