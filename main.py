import os
import time
import sqlite3
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES E CAMINHOS ---
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(DIRETORIO_ATUAL, '.env'))
CAMINHO_BANCO = os.path.join(DIRETORIO_ATUAL, 'vagas_gupy.db')

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID_GRUPO")

# Dicionários de Tradução para deixar a mensagem amigável
TRADUCAO_MODELO = {
    "on-site": "Presencial",
    "hybrid": "Híbrido",
    "remote": "Remoto"
}

TRADUCAO_TIPO_VAGA = {
    "vacancy_type_effective": "Efetivo",
    "vacancy_type_apprentice": "Jovem Aprendiz",
    "vacancy_type_internship": "Estágio",
    "vacancy_type_temporary": "Temporário",
    "vacancy_type_freelancer": "Freelancer"
}

# --- 2. BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vagas_enviadas (
            link TEXT PRIMARY KEY,
            data_publicacao TEXT,
            titulo TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

# --- 3. DISPARO PARA O TELEGRAM ---
def enviar_alerta_telegram(titulo, empresa, local, modelo, tipo, pcd, link, data, hora):
    if not TOKEN or not CHAT_ID:
        print("❌ ERRO: Token ou Chat ID não encontrados!")
        return False

    mensagem = f"🎯 <b>VAGA GUPY - RIO DE JANEIRO!</b>\n\n" \
               f"💼 <b>Vaga:</b> {titulo}\n" \
               f"🏢 <b>Empresa:</b> {empresa}\n" \
               f"📍 <b>Local:</b> {local}\n" \
               f"💻 <b>Modelo:</b> {modelo}\n" \
               f"📄 <b>Tipo:</b> {tipo}\n" \
               f"♿ <b>PCD:</b> {pcd}\n" \
               f"📅 <b>Data:</b> {data} às {hora}\n\n" \
               f"🔗 <a href='{link}'>Clique aqui para aplicar na Gupy</a>"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML", "disable_web_page_preview": True}
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"✅ Enviada: {titulo[:40]}...")
            return True
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# --- 4. MOTOR DE BUSCA DA GUPY ---
def buscar_vagas_gupy_rj():
    print("🚀 Iniciando varredura detalhada na API da Gupy...")
    conn, cursor = iniciar_banco()
    
    # Máscara completa de navegador para passar pela proteção
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://portal.gupy.io/job-search/sortBy=publishedDate&state=Rio%20de%20Janeiro',
        'Origin': 'https://portal.gupy.io'
    }
    
    offset = 0
    vagas_velhas = 0
    LIMITE_VELHAS = 20
    url_api = "https://employability-portal.gupy.io/api/v1/jobs"
    
    while vagas_velhas < LIMITE_VELHAS:
        params = {'state': 'Rio de Janeiro', 'limit': 10, 'offset': offset}
        
        try:
            resposta = requests.get(url_api, headers=headers, params=params, timeout=15)
            
            if resposta.status_code != 200: 
                print(f"🛑 Erro de conexão. Código HTTP: {resposta.status_code}")
                break
            
            # Tenta decodificar o JSON. Se falhar, mostra o que a Gupy enviou de verdade.
            try:
                dados_json = resposta.json()
            except Exception:
                print(f"🛑 Fomos bloqueados! O servidor não enviou os dados JSON. Resposta do site:\n{resposta.text[:300]}")
                break

            lista_vagas = dados_json.get('data', [])
            if not lista_vagas: break

            for vaga in lista_vagas:
                link_vaga = vaga.get('jobUrl', '')
                if not link_vaga: continue
                
                titulo = vaga.get('name', 'Título Indisponível')
                empresa = vaga.get('careerPageName', 'Empresa não informada')
                local = f"{vaga.get('city', 'RJ')} - {vaga.get('state', 'RJ')}"
                
                # Tradução de Modelo e Tipo
                modelo = TRADUCAO_MODELO.get(vaga.get('workplaceType', ''), "Não informado")
                tipo = TRADUCAO_TIPO_VAGA.get(vaga.get('type', ''), "Outros")
                
                # Verificação de PCD
                pcd = "Sim" if vaga.get('disabilities') else "Não informado"

                # Tratamento de Data e Hora (Convertendo de UTC para Brasília/RJ)
                data_iso = vaga.get('publishedDate', '')
                try:
                    # Limpa os milissegundos e o "Z" do final (ex: "2026-04-27T23:39:00.000Z" -> "2026-04-27T23:39:00")
                    data_limpa = data_iso.split('.')[0] 
                    
                    # Converte o texto da Gupy em um objeto de "Tempo" do Python
                    data_utc = datetime.strptime(data_limpa, "%Y-%m-%dT%H:%M:%S")
                    
                    # Subtrai 3 horas (Fuso do Rio de Janeiro)
                    data_brt = data_utc - timedelta(hours=3)
                    
                    # Formata de volta para texto bonitinho pro Telegram
                    data_f = data_brt.strftime("%d/%m/%Y")
                    hora_f = data_brt.strftime("%H:%M")
                except Exception:
                    data_f, hora_f = "Sem data", "--:--"

                cursor.execute('SELECT 1 FROM vagas_enviadas WHERE link = ?', (link_vaga,))
                if cursor.fetchone():
                    vagas_velhas += 1
                    if vagas_velhas >= LIMITE_VELHAS: break
                else:
                    vagas_velhas = 0 
                    cursor.execute('INSERT INTO vagas_enviadas VALUES (?, ?, ?)', (link_vaga, data_f, titulo))
                    conn.commit()
                    
                    enviar_alerta_telegram(titulo, empresa, local, modelo, tipo, pcd, link_vaga, data_f, hora_f)
                    time.sleep(2)
            
            offset += 10 
        except Exception as e:
            print(f"⚠️ Erro de execução: {e}")
            break

    conn.close()
    print("✅ Varredura finalizada!")

if __name__ == '__main__':
    buscar_vagas_gupy_rj()