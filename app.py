from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import requests  # Importa a biblioteca requests
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
    
@app.route('/youtube')
def consultar_youtube():
    return render_template('youtube.html')

@app.route('/youtube2')
def consul_youtube2():
    return render_template('youtube2.html')

@app.route('/main')
def main():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    return render_template('main.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
