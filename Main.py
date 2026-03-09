import os
import telebot
from flask import Flask
from threading import Thread

TOKEN = '8693842157:AAGQGuDLQ1Q4jxGI6mlzqbfcIObz1zLxqqA'
bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Robô de Estatísticas de Elite Rodando!"

def run():
    app.run(host='0.0.0.0', port=8080)

@bot.message_handler(commands=['start', 'stats'])
def start_stats(message):
    instrucao = (
        "📊 **Mande os 16 dados (espaço):**\n\n"
        "1. Chutes | 2. Minutos | 3. Cartões | 4. Km Viagem | 5. Descanso\n"
        "6. Faltas Com. | 7. Desarmes | 8. Juiz | 9. Marcador (1-10)\n"
        "10. Goleiro (1-10) | 11. Ref. Única (1/0) | 12. Dia Especial (1/0)\n"
        "13. Mordedor (1/0) | 14. Driblador (1/0)\n"
        "15. Time em Crise (1-Sim, 0-Não) | 16. Histórico Freguês (1-Sim, 0-Não)"
    )
    msg = bot.reply_to(message, instrucao)
    bot.register_next_step_handler(msg, analise_final)

def analise_final(message):
    try:
        d = message.text.split()
        (chutes, min_j, cart, km, desc, f_com, des, juiz, marc, gol, 
         ref, esp, mord, drib, crise, fregues) = map(float, d)
        
        # P90 BASE
        p90 = (chutes / min_j) * 90
        
        # AJUSTES PSICOLÓGICOS E TÁTICOS
        peso = 1.0
        if ref == 1: peso += 0.20      # Referência aumenta volume
        if esp == 1: peso += 0.15      # Aniversário/Estreia aumenta fome
        if crise == 1: peso -= 0.15    # Time em crise trava o jogo
        if fregues == 1: peso += 0.25  # Lei do ex ou freguesia histórica
        
        # DUELO INDIVIDUAL
        penalidade_defesa = (1 - (marc / 30)) * (1 - (gol / 35))
        if mord == 1 and drib == 1: penalidade_defesa *= 0.85 # Caça ao driblador
        
        # EXPECTATIVA FINAL
        exp = round(p90 * peso * penalidade_defesa, 2)
        
        # FADIGA
        fadiga = round((km / 100) / (desc / 24), 2)
        
        relatorio = (
            f"🏆 **ANÁLISE DE ELITE CONCLUÍDA**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚽ **P90 Bruto:** {round(p90, 2)} | **POTENCIAL REAL:** {exp}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **AMBIENTE:**\n"
            f"• Crise no Clube: {'Sim (-15%)' if crise == 1 else 'Não'}\n"
            f"• Lei do Ex/Freguês: {'Sim (+25%)' if fregues == 1 else 'Não'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚔️ **DUELO:**\n"
            f"• Marcador Mordedor: {'SIM' if mord == 1 else 'Não'}\n"
            f"• Risco Cartão: {'ALTO 🔥' if juiz > 5.5 or f_com > 15 else 'NORMAL'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✈️ **Fadiga:** {fadiga}% | **Goleiro:** {int(gol)}/10\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Com {exp} de projeção, procure linhas de 0.5 ou 1.5 chutes.*"
        )
        bot.reply_to(message, relatorio, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Erro! Mande os 16 números.")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
