from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
import requests  # Importa a biblioteca requests
import re  # Adiciona a importação do módulo re
from bin import verificar_bin
from ip import buscar_informacoes_ip
from youtube import youtube_app  # Importa a blueprint do youtube.py
from youtube2 import youtube2_app  # Importa a blueprint do youtube2.py

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta'

# Registra as blueprints
app.register_blueprint(youtube_app, url_prefix='/youtube')  # Registrar a blueprint do youtube
app.register_blueprint(youtube2_app, url_prefix='/youtube2')  # Registrar a blueprint do youtube2

def verificar_credenciais(usuario, senha):
    with open('usuarios.txt', 'r') as f:
        for linha in f:
            login, senha_arquivo = linha.strip().split('|')
            if login == usuario and senha_arquivo == senha:
                return True
    return False

@app.route('/')
def home():
    return render_template('index.html')  # Renderiza a página de login

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if verificar_credenciais(usuario, senha):
        session['logged_in'] = True
        print(f"Usuário {usuario} logado com sucesso.")  # Log do login
        return redirect(url_for('main'))
    else:
        return "Usuário ou senha inválidos!", 401  # Retorna erro 401 para login inválido

# Middleware para verificar se o usuário está logado
@app.before_request
def require_login():
    allowed_routes = ['home', 'login']  # Permite acesso a estas rotas sem login
    if request.endpoint not in allowed_routes and not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona para a página de login

@app.route('/bin')
def bin_page():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    return render_template('bin.html', message=None)

@app.route('/check_bin', methods=['POST'])
def check_bin():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    bin_number = request.form['bin']
    return verificar_bin(bin_number)

@app.route('/ip')
def ip_page():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    return render_template('ip.html', message=None)

@app.route('/check_ip', methods=['POST'])
def check_ip():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    ip_address = request.form.get('ip')
    resultado = buscar_informacoes_ip(ip_address, is_dono=False, is_vip=True)
    return render_template('ip.html', message=resultado)

# CONSULTA CPF
@app.route('/consultar_cpf', methods=['GET', 'POST'])
def consultar_cpf():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        print(f"Consultando CPF: {cpf}")  # Log do CPF que está sendo consultado
        
        if not cpf:
            return jsonify({'status': 'error', 'message': '🤔 Cadê o CPF?'}), 400

        try:
            # Chamada à API externa para consultar o CPF
            response = requests.get(f'http://api2.minerdapifoda.xyz:8080/api/cpf3?cpf={cpf}')
            print(f"Resposta da API: {response.status_code} - {response.text}")  # Log da resposta da API
            
            if response.status_code != 200:
                return jsonify({'status': 'error', 'message': '❌ Não foi encontrado informações para o CPF informado.'}), 404
            
            cpf_data = response.json().get('Resultado')
            print(f"Dados do CPF: {cpf_data}")  # Log dos dados recebidos
            
            # Inicializa um dicionário para armazenar os resultados
            resultados = {}
            
            # Utiliza expressões regulares para extrair os dados
            cpf_match = re.search(r'CPF:\s*([\d\-]+)', cpf_data)
            nome_match = re.search(r'Nome:\s*(.*)', cpf_data)
            sexo_match = re.search(r'Sexo:\s*(.*)', cpf_data)
            data_nascimento_match = re.search(r'Data de Nascimento:\s*(.*)', cpf_data)

            # Verifica se todas as correspondências foram feitas
            if cpf_match and nome_match and sexo_match and data_nascimento_match:
                resultados['cpf'] = cpf_match.group(1)
                resultados['nome'] = nome_match.group(1)
                resultados['sexo'] = sexo_match.group(1)
                resultados['data_nascimento'] = data_nascimento_match.group(1)
            else:
                return jsonify({'status': 'error', 'message': '❌ Dados não encontrados para o CPF informado.'}), 404

            # Cria a mensagem de resultado
            resultado_mensagem = (
                f"CPF: {resultados['cpf']}\n"
                f"Nome: {resultados['nome']}\n"
                f"Sexo: {resultados['sexo']}\n"
                f"Data de Nascimento: {resultados['data_nascimento']}"
            )
            return jsonify({'status': 'success', 'data': resultado_mensagem}), 200

        except Exception as e:
            print(f"Erro ao consultar CPF: {e}")  # Log do erro
            return jsonify({'status': 'error', 'message': '❌ Ocorreu um erro ao consultar o CPF.'}), 500

    return render_template('cpf.html')
# CONSULTA TELEFONE
@app.route('/consultar_tel', methods=['GET', 'POST'])
def consultar_tel():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    if request.method == 'POST':
        telefone = request.form.get('telefone')
        print(f"Consultando Telefone: {telefone}")  # Log do telefone que está sendo consultado
        
        if not telefone:
            return jsonify({'status': 'error', 'message': '🤔 Cadê o Telefone?'}), 400

        try:
            # Chamada à API externa para consultar o telefone
            response = requests.get(f'http://api2.minerdapifoda.xyz:8080/api/telefones2?telefone={telefone}')
            print(f"Resposta da API: {response.status_code} - {response.text}")  # Log da resposta da API
            
            if response.status_code != 200:
                return jsonify({'status': 'error', 'message': '❌ Não foi encontrado informações para o telefone informado.'}), 404
            
            tel_data = response.json().get('Resultado')
            print("Estrutura de tel_data:", tel_data)  # Log da estrutura para depuração

            # Acessando os dados de tel_data
            if isinstance(tel_data, dict):
                # Pegando a primeira tabela encontrada
                primeira_tabela = next(iter(tel_data.values()), None)  # Pega a primeira tabela (lista)
                
                if primeira_tabela and isinstance(primeira_tabela, list) and primeira_tabela:
                    tabela = primeira_tabela[0]  # Pega o primeiro item da lista
                    mensagem = (
                        f"<strong>Telefone Informado:</strong> {tabela['telefone']}<br><br>"
                        f"<strong>📌 Dados Encontrados 📌</strong><br>"
                        f"▸ <strong>Nome:</strong> {tabela['nome']}<br>"
                        f"▸ <strong>CPF:</strong> {tabela['cpf']}<br>"
                        f"▸ <strong>Tipo de Pessoa:</strong> {tabela['TIPO_PESSOA']}<br>"
                        f"▸ <strong>Data Instalação:</strong> {tabela['DATA_INSTALACAO']}<br>"
                        f"▸ <strong>Telefone Secundário:</strong> {tabela['telefone_sec']}<br>"
                        f"▸ <strong>Rua:</strong> {tabela['rua']}<br>"
                        f"▸ <strong>Bairro:</strong> {tabela['bairro']}<br>"
                        f"▸ <strong>Número:</strong> {tabela['num']}<br>"
                        f"▸ <strong>Complemento:</strong> {tabela['compl']}<br>"
                        f"▸ <strong>Cep:</strong> {tabela['cep']}<br>"
                        f"▸ <strong>UF:</strong> {tabela['uf']}<br><br>"
                    )
                    return jsonify({'status': 'success', 'data': mensagem}), 200

                return jsonify({'status': 'error', 'message': '❌ Nenhum dado encontrado para o telefone informado.'}), 404

            return jsonify({'status': 'error', 'message': '❌ Estrutura de dados inesperada.'}), 404

        except Exception as e:
            print(f"Erro ao consultar Telefone: {e}")  # Log do erro
            return jsonify({'status': 'error', 'message': '❌ Ocorreu um erro ao consultar o telefone.'}), 500

    return render_template('tel.html')  # Renderiza a página de consulta de telefone

# CONSULTA DE NOMES

@app.route('/consultar_nome', methods=['GET', 'POST'])
def consultar_nome():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado

    if request.method == 'POST':
        nome = request.form.get('nome')
        print(f"Consultando Nome: {nome}")

        if not nome:
            return jsonify(message="🤔 Cadê o Nome?"), 400

        try:
            cors_url = 'https://api.allorigins.win/get?url='
            api_url = f'http://api2.minerdapifoda.xyz:8080/api/nomes?nome={nome}'
            response = requests.get(cors_url + api_url)

            if response.status_code == 200:
                jsonData = response.json()
                nomeData = jsonData.get('contents')

                if nomeData:
                    return jsonify(status="success", data=nomeData)

                return jsonify(message="❌ Nome não encontrado ou inexistente!"), 404

            return jsonify(message="❌ Nome não encontrado ou inexistente!"), 404

        except Exception as e:
            print(f"Erro ao consultar Nome: {e}")
            return jsonify(message="❌ Ocorreu um erro ao consultar o nome."), 500

    # Renderiza a página de consulta de nome
    return render_template('consultar_nome.html')

@app.route('/youtube')
def consultar_youtube():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    return render_template('youtube.html')

@app.route('/youtube2')
def consul_youtube2():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    return render_template('youtube2.html')

@app.route('/main')
def main():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona se não estiver logado
    return render_template('main.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    print("Usuário deslogado.")  # Log do logout
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
