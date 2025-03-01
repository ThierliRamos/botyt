from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta'  # Necessário para gerenciar sessões

def verificar_credenciais(usuario, senha):
    # Lê o arquivo de usuários
    with open('usuarios.txt', 'r') as f:
        for linha in f:
            login, senha_arquivo = linha.strip().split('|')
            if login == usuario and senha_arquivo == senha:
                return True
    return False

@app.route('/')
def home():
    return render_template('index.html')  # Serve o index.html ao acessar a raiz

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')  # Usar get() para evitar KeyError
    senha = request.form.get('senha')      # Usar get() para evitar KeyError
    if verificar_credenciais(usuario, senha):
        session['logged_in'] = True  # Marca como logado
        return redirect(url_for('main'))
    else:
        return "Usuário ou senha inválidos!"

@app.route('/check_bin', methods=['POST'])
def check_bin():
    # Lógica para verificar BIN
    ...

@app.route('/bin')
def check_bin():    
    return render_template('bin.html')  # Retorna a página bin.html

@app.route('/ip')
def consultar_ip():    
    return render_template('ip.html')  # Retorna a página bin.html

@app.route('/youtube')
def consultar_youtube():    
    return render_template('youtube.html')  # Retorna a página bin.html



@app.route('/main')
def main():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redireciona para login se não estiver logado
    return render_template('main.html')  # Serve o main.html após login

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove a sessão
    return redirect(url_for('home'))  # Redireciona para a página de login

if __name__ == '__main__':    
    port = int(os.environ.get("PORT", 5000))  # Usa a variável de ambiente PORT ou 5000 como padrão    
    app.run(host='0.0.0.0', port=port)  # Escuta em 0.0.0.0 na porta especificada
