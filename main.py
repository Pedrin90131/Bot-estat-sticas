import telebot
import requests

# CONFIGURAÇÕES
API_KEY = '43352a0e053fdbe2358ee4a4517623a8'
TOKEN_TELEGRAM = '8693842157:AAFOBEJ-b9kuB2DJVjWejju-gYnRfLYMV08'

bot = telebot.TeleBot(TOKEN_TELEGRAM)
headers = {'x-apisports-key': API_KEY}

def calc_p90(valor, minutos):
    if not minutos or minutos == 0: return 0
    return round((valor / minutos) * 90, 2)

def get_player_full_data(player_name):
    # 1. Busca o ID do jogador
    res = requests.get(f"https://v3.football.api-sports.io/players?search={player_name}", headers=headers).json()
    if not res.get('response'): return None
    
    p_info = res['response'][0]['player']
    p_id = p_info['id']
    team_id = res['response'][0]['statistics'][0]['team']['id']
    
    # 2. Busca os últimos 5 jogos (fixtures) onde o jogador esteve relacionado
    res_fixtures = requests.get(f"https://v3.football.api-sports.io/fixtures?player={p_id}&last=5", headers=headers).json()
    
    jogos_recentes = []
    total_stats = {'min': 0, 'chu': 0, 'des': 0, 'fc': 0, 'fs': 0, 'titularidades': 0}
    
    if res_fixtures.get('response'):
        for f in res_fixtures['response']:
            f_id = f['fixture']['id']
            # Detalhe estatístico do jogador nesse jogo
            p_match = requests.get(f"https://v3.football.api-sports.io/fixtures/players?fixture={f_id}&player={p_id}", headers=headers).json()
            
            if p_match.get('response'):
                s = p_match['response'][0]['players'][0]['statistics'][0]
                equipa_adv = f['teams']['away']['name'] if f['teams']['home']['id'] == team_id else f['teams']['home']['name']
                data_jogo = f['fixture']['date'][:10]
                
                minutos = s['games']['minutes'] or 0
                chutes = s['shots']['total'] or 0
                desarmes = (s['tackles']['total'] or 0) + (s['tackles']['interceptions'] or 0)
                foi_titular = not s['games']['substitute']
                
                jogos_recentes.append({
                    'data': data_jogo,
                    'adv': equipa_adv,
                    'min': minutos,
                    'chu': chutes,
                    'des': desarmes,
                    'status': "✅ Titular" if foi_titular else "🔄 Reserva"
                })
                
                # Acumuladores
                total_stats['min'] += minutos
                total_stats['chu'] += chutes
                total_stats['des'] += desarmes
                total_stats['fc'] += s['fouls']['committed'] or 0
                total_stats['fs'] += s['fouls']['drawn'] or 0
                if foi_titular and minutos > 0: total_stats['titularidades'] += 1
                
    return {'info': p_info, 'jogos': jogos_recentes, 'total': total_stats}

@bot.message_handler(func=lambda message: True)
def dossie_minutagem(message):
    query = message.text
    bot.reply_to(message, f"🕵️‍♂️ ANALISANDO MINUTAGEM E PERFORMANCE: {query.upper()}")

    dados = get_player_full_data(query)
    if not dados:
        bot.reply_to(message, "Jogador não encontrado.")
        return

    p = dados['info']
    stats = dados['total']
    prob_titular = (stats['titularidades'] / len(dados['jogos'])) * 100 if dados['jogos'] else 0
    
    msg = f"👤 **RAIO-X: {p['name'].upper()}**\n"
    msg += f"🔥 Chance de Titularidade: {int(prob_titular)}%\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += "📅 **MINUTAGEM NOS ÚLTIMOS JOGOS:**\n"
    for j in dados['jogos']:
        msg += f"🗓 {j['data']} vs {j['adv']}\n"
        msg += f"⏱ **{j['min']} MINUTOS** ({j['status']})\n"
        msg += f"📊 🎯 {j['chu']} Chutes | 🛡 {j['des']} Desarmes\n"
        msg += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"

    msg += "\n📈 **POTENCIAL MÉDIO (P90):**\n"
    msg += f"🎯 Chutes: {calc_p90(stats['chu'], stats['min'])}\n"
    msg += f"🛡️ Desarmes: {calc_p90(stats['des'], stats['min'])}\n"
    msg += f"🦴 Faltas Cometidas: {calc_p90(stats['fc'], stats['min'])}\n"
    msg += f"🤕 Faltas Sofridas: {calc_p90(stats['fs'], stats['min'])}\n"
    
    bot.send_message(message.chat.id, msg)

bot.polling()
                
