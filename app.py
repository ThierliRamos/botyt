from flask import Flask, render_template, request, redirect, url_for, session
import os
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

@app.route('/')
def cpf():
    return render_template('cpf.html')  # Certifique-se de que este é o seu arquivo de entrada

@app.route('/consultar_cpf')
def consultar_cpf_page():
    return render_template('cpf.html')  # Renderiza a página de consulta de CPF

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
