# 🚀 Gupy Job Tracker: Automação de Vagas no Telegram

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Gupy API](https://img.shields.io/badge/Source-Gupy%20API-orange)](https://portal.gupy.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Sobre o Projeto

Buscar vagas de emprego diariamente é um processo exaustivo e repetitivo. Para resolver esse problema e otimizar meu tempo (e o de centenas de profissionais), desenvolvi este **rpa** em Python. 

O robô atua como um "radar" silencioso: ele monitora a plataforma Gupy 24 horas por dia, captura novas oportunidades de trabalho no Estado do Rio de Janeiro e dispara alertas formatados em tempo real diretamente em um canal do Telegram. Assim, as vagas chegam mastigadas até os candidatos, contendo todas as informações essenciais (Modelo de trabalho, tipo de contrato e acessibilidade para PCD).

---

## 🎯 Veja rodando na prática

Quer ver o robô trabalhando ao vivo? Entre no grupo aberto do Telegram que é alimentado 100% por esta automação:
👉 **[Entrar no Grupo: Vagas Gupy | Rio de Janeiro](https://t.me/+20ZgzGruRzJlYjVh)**

---

## 📸 Demonstração do Bot

<img width="911" height="914" alt="image" src="https://github.com/user-attachments/assets/b72a9a11-6467-45e4-a9b9-b6bf26d0791d" />


*Acima: Interface do bot entregando vagas no grupo com formatação amigável.*

---

## 💡 Diferenciais Técnicos (Por que não usei Selenium?)

A maioria das automações de Web Scraping utiliza ferramentas que simulam um navegador aberto (como Selenium), o que consome muita memória RAM e deixa o processo lento. Este projeto resolve o problema usando uma **abordagem API-First**:

1. **Performance Extrema:** O script intercepta a API oculta que a própria Gupy usa para renderizar as vagas. Ele consome pacotes JSON puros, sendo incrivelmente mais rápido e leve.
2. **Tratamento de Dados:** A API retorna datas no fuso horário global (UTC) e termos técnicos em inglês. O código faz o *parse* automático, traduzindo para o horário de Brasília e para o português.
3. **Trava Anti-Spam (SQLite):** Utiliza um banco de dados relacional leve (`vagas_gupy.db`) para memorizar o ID de cada vaga processada. Isso garante que o bot nunca envie a mesma vaga duplicada para o grupo, mesmo que o script seja reiniciado.

---

## ⚙️ Como Adaptar para o SEU Estado

O código foi criado focado no Rio de Janeiro, mas você pode mudar para qualquer estado do Brasil em segundos.

Abra o arquivo `main.py`, vá até a função `buscar_vagas_gupy_rj()` e localize o dicionário de parâmetros:

```python
# Altere 'Rio de Janeiro' para o seu estado (ex: 'São Paulo', 'Minas Gerais')
params = {
    'state': 'Rio de Janeiro', 
    'limit': 10,
    'offset': offset
}
```

---

## 🚀 Instalação e Uso Local

### 1. Pré-requisitos
* Python 3.8+ instalado.
* Um Bot criado no Telegram via [@BotFather](https://t.me/botfather).

### 2. Clonando o Repositório
Abra o terminal e rode os comandos:
```bash
git clone [https://github.com/lucasnunestrabalho99-sudo/telegram-vagas-gupy-bot.git](https://github.com/lucasnunestrabalho99-sudo/telegram-vagas-gupy-bot.git)
cd telegram-vagas-gupy-bot
```

### 3. Configurando o Ambiente
Crie um ambiente virtual e instale as bibliotecas necessárias:
```bash
python -m venv venv

# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Variáveis de Ambiente
Crie um arquivo chamado **exatamente** `.env` na raiz do projeto e insira as credenciais do seu robô e do seu grupo:
```env
TELEGRAM_TOKEN=cole_seu_token_aqui
CHAT_ID_GRUPO=cole_o_id_do_seu_grupo_aqui
```

### 5. Executando o Motor
```bash
python main.py
```

---

## 📅 Agendamento Automático (Windows)
Se você utiliza Windows, o repositório inclui um arquivo `rodar_gupy.bat`. Você pode usar o **Agendador de Tarefas do Windows** para rodar esse arquivo de hora em hora. O `.bat` já está configurado para forçar o encoding UTF-8 (evitando crash com emojis) e gerar um arquivo `erro_log.txt` para monitoramento.

---
**Desenvolvido com ☕ por Lucas Nunes** | [LinkedIn](linkedin.com/in/lucas-nunes-da-silva-574604216)
