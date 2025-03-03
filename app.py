from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    if verificar_credenciais(usuario, senha):
        session['logged_in'] = True
        print(f"Usuário {usuario} logado com sucesso.")  # Log do login
        return redirect(url_for('main'))
    else:
        return "Usuário ou senha inválidos!"

@app.route('/bin')
def bin_page():
    return render_template('bin.html', message=None)

@app.route('/check_bin', methods=['POST'])
def check_bin():
    bin_number = request.form['bin']
    return verificar_bin(bin_number)

@app.route('/ip')
def ip_page():
    return render_template('ip.html', message=None)

@app.route('/check_ip', methods=['POST'])
def check_ip():
    ip_address = request.form.get('ip')
    resultado = buscar_informacoes_ip(ip_address, is_dono=False, is_vip=True)
    return render_template('ip.html', message=resultado)

# CONSULTA CPF

@app.route('/consultar_cpf', methods=['GET', 'POST'])
def consultar_cpf():
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
            resultados = {
                'cpf': re.search(r'CPF:\s*([\d\-]+)', cpf_data).group(1),
                'nome': re.search(r'Nome:\s*(.*)', cpf_data).group(1),
                'sexo': re.search(r'Sexo:\s*(.*)', cpf_data).group(1),
                'data_nascimento': re.search(r'Data de Nascimento:\s*(.*)', cpf_data).group(1)
            }
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

# CONSULTA NOME

# CONSULTA DE NOME

@app.route('/consultar_nome', methods=['GET', 'POST'])
def consultar_nome():
    if request.method == 'POST':
        nome = request.form.get('nome')
        print(f"Consultando Nome: {nome}")

        if not nome:
            return jsonify(message="🤔 Cadê o Nome?"), 400

        try:
            response = requests.get(f'http://api2.minerdapifoda.xyz:8080/api/nomes?nome={nome}')
            print(f"Resposta da API: {response.status_code} - {response.text}")

            if response.status_code != 200:
                return jsonify(message="❌ Nome não encontrado ou inexistente!"), 404

            nomeData = response.json().get('Resultado')
            if "Nome não encontrado" in nomeData:
                return jsonify(message="❌ Nome não encontrado ou inexistente!"), 404

            print(f"Dado retornado: {nomeData}")
            return jsonify(status="success", data=nomeData)

        except Exception as e:
            print(f"Erro ao consultar Nome: {e}")
            return jsonify(message="❌ Ocorreu um erro ao consultar o nome."), 500

    return render_template('consultar_nome.html')  # Renderiza a página de consulta de nome

@app.route('/download/<string:nome>', methods=['GET'])
def download_nome(nome):
    try:
        response = requests.get(f'http://api2.minerdapifoda.xyz:8080/api/nomes?nome={nome}')
        
        if response.status_code != 200:
            return jsonify(message="❌ Nome não encontrado ou inexistente!"), 404

        nomeData = response.json().get('Resultado')

        if "Nome não encontrado" in nomeData:
            return jsonify(message="❌ Nome não encontrado ou inexistente!"), 404

        output = io.BytesIO(nomeData.encode('utf-8'))

        # Mudar o download_name para incluir o nome do usuário
        return send_file(
            output,
            as_attachment=True,
            download_name=f'{nome}_consulta.txt',  # Nome do arquivo personalizado
            mimetype='text/plain'
        )
    except Exception as e:
        print(f"Erro ao fazer download do nome: {e}")
        return jsonify(message="❌ Ocorreu um erro ao fazer o download."), 500

@app.route('/youtube')
def consultar_youtube():
    return render_template('youtube.html')

@app.route('/youtube2')
def consul_youtube2():
    return render_template('youtube2.html')

@app.route('/main')
def main():
    try:
        print(f"Usuário está logado: {session.get('logged_in')}")  # Log do status da sessão
        if not session.get('logged_in'):
            return redirect(url_for('home'))
        return render_template('main.html')
    except Exception as e:
        print(f"Erro ao acessar a página principal: {e}")  # Log do erro
        return "Erro ao acessar a página principal.", 500

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    print("Usuário deslogado.")  # Log do logout
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
