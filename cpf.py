from flask import Flask, request, render_template, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('cpf.html')

@app.route('/cpf2', methods=['POST'])
def consulta_cpf():
    cpf = request.form.get('cpf')

    if not cpf:
        return jsonify({'status': 'error', 'message': '🤔 Cadê o CPF?'}), 400

    try:
        # Chamada à API externa para consultar o CPF
        response = requests.get(f'http://api2.minerdapifoda.xyz:8080/api/cpf3?cpf={cpf}')
        
        if response.status_code != 200:
            return jsonify({'status': 'error', 'message': '❌ Não foi encontrado informações para o CPF informado.'}), 404
        
        # Captura os dados retornados
        cpf_data = response.json().get('Resultado')
        
        # Imprime a estrutura do cpf_data para depuração
        print("Dados retornados da API:", cpf_data)  # Para depuração
        
        # Usar regex para extrair as informações
        resultados = {
            'cpf': re.search(r'CPF:\s*([\d\-]+)', cpf_data).group(1),
            'nome': re.search(r'Nome:\s*(.*)', cpf_data).group(1),
            'sexo': re.search(r'Sexo:\s*(.*)', cpf_data).group(1),
            'data_nascimento': re.search(r'Data de Nascimento:\s*(.*)', cpf_data).group(1)
        }

        # Formatar a mensagem de retorno
        resultado_mensagem = (
            f"CPF: {resultados['cpf']}\n"
            f"Nome: {resultados['nome']}\n"
            f"Sexo: {resultados['sexo']}\n"
            f"Data de Nascimento: {resultados['data_nascimento']}"
        )
        
        return jsonify({'status': 'success', 'data': resultado_mensagem}), 200

    except Exception as e:
        print(f"Erro ao consultar CPF: {e}")
        return jsonify({'status': 'error', 'message': '❌ Ocorreu um erro ao consultar o CPF.'}), 500

if __name__ == '__main__':
    app.run(debug=True)