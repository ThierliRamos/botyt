from flask import render_template
import requests
import time

def buscar_informacoes_ip(ip_address, is_dono, is_vip):
    try:
        # Determina se o usuário pode usar o comando
        pode_usar = is_dono or is_vip
        if not pode_usar:
            return "🔐 Apenas pessoas autorizadas podem usar!"
        
        time.sleep(1)  # Espera 1 segundo

        url = f"https://ip-geo-location.p.rapidapi.com/ip/check?format=json&language=pt&filter={ip_address}"
        headers = {
            "x-rapidapi-key": "99bb57d209mshb6ca809dc147a3ep1a51e7jsnf829ae92aef6",
            "x-rapidapi-host": "ip-geo-location.p.rapidapi.com",
        }

        print(f"Consultando: {url}")

        response = requests.get(url, headers=headers)
        data = response.json()

        if data:
            return (f"<div><strong>IP Identificado:</strong> {data['ip']}</div>"
                    f"<div><strong>Organização:</strong> {data['asn']['organisation']}</div>"
                    f"<div><strong>País:</strong> {data['country']['name']}</div>"
                    f"<div><strong>Região:</strong> {data['region']['name']}</div>"
                    f"<div><strong>Cidade:</strong> {data['city']['name']}</div>"
                    f"<div><strong>População:</strong> {data['country']['population']}</div>"
                    f"<div><strong>Latitude:</strong> {data['location']['latitude']}</div>"
                    f"<div><strong>Longitude:</strong> {data['location']['longitude']}</div>"
                    f"<div><strong>Fuso Horário:</strong> {data['time']['timezone']}</div>")
    except Exception as error:
        print(error)
        return "Erro ao buscar informações!"
