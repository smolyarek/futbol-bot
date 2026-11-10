import os
import time
import threading
from flask import Flask
import telebot
from telebot import types
from google import genai
from google.genai import types as genai_types

# ================= SERVERİN 24/7 AÇIQ QALMASI ÜÇÜN (FLASK) =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Futbol AI Botu 24/7 aktivdir!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= AÇARLAR (Təhlükəsiz sistemdən oxunur) =================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# ================= AI ANALİZ VƏ AXTARIŞ SİSTEMİ =================
def analyze_football(query_text: str, is_scan: bool = False) -> str:
    """Canlı Google Axtarışı ilə interneti gəzən AI Agenti"""
    if is_scan:
        prompt = """
Sən peşəkar idman analitiki və böyük mərc mütəxəssisisən.
Canlı Google Axtarışından istifadə edərək bu gün (və ya qarşıdakı 24 saatda) keçiriləcək futbol oyunları arasında ən kəskin ƏMSAL DÜŞMƏSİ (Dropping Odds) olan 1-2 oyunu tap (Oddsportal, Flashscore, Betexplorer və s. saytları nəzərdən keçir).

Həmin oyunlar üçün dərhal araşdır:
1. Əmsalın düşməsinə səbəb olan real xəbərlər nədir?
2. Zədəli, cəzalı və rotasiya edilən əsas oyunçular kimlərdir?
3. Komandalarda daxili maliyyə böhranı, maaş problemi və ya məşqçi narazılığı varmı?
4. Hava şəraiti necədir?

Cavabı bu formatda Azərbaycan dilində ver:
⚽ **Matç və Əmsal Hərəkəti:**
(Komandalar və əmsalın necə dəyişməsi)

🔍 **Arxasındakı Real Səbəblər:**
(Heyət itkiləri, rotasiya, maliyyə və s.)

⚖️ **Doğruluq Qiymətləndirməsi:**
(Bu düşmə real amillərə əsaslanır, yoxsa süni/tələdir?)

🎯 **Qərar:**
[PUL QOYMAQ OLAR ✅] və ya [PUL QOYMAQ OLMAZ / RİSKLİDİR ❌] (səbəbi 1 cümlə ilə).
"""
    else:
        prompt = f"""
Sən peşəkar idman analitikisən.
İstifadəçi bu matçı araşdırmağını istəyir: {query_text}

Canlı Google Axtarışından istifadə edərək bu günə olan ən son məlumatları tap:
1. Əsas oyunçulardan kimlər zədəli və ya cəzalıdır?
2. Heyətdə rotasiya varmı (qarşıdakı oyunlar üçün əsas oyunçular dinləndirilir)?
3. Klub daxilində maliyyə problemi, maaş böhranı və ya gərginlik varmı?
4. Hava şəraiti necədir?
5. Əmsallarda hər hansı şübhəli dəyişiklik varmı?

Cavabı bu formatda Azərbaycan dilində ver:
📋 **Matç Faktları və Zədələr:**
(İnternetdə tapılan ən son rəsmi və daxili xəbərlər)

⚖️ **Vəziyyət Qiymətləndirməsi:**
(Komandaların real gücü və risklər)

🎯 **Mərc Qərarı:**
[PUL QOYMAQ OLAR ✅] və ya [PUL QOYMAQ OLMAZ / RİSKLİDİR ❌] (səbəbini qısa xülasə et).
"""

    try:
        response = ai_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
                temperature=0.3
            )
        )
        return response.text
    except Exception as e:
        return f"AI Analiz xətası baş verdi: {e}"

# ================= TELEGRAM MENYULARI VƏ CAVABLAR =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📉 Düşən Əmsalları Skan Et")
    btn2 = types.KeyboardButton("ℹ️ Kömək")
    markup.add(btn1, btn2)

    welcome_text = (
        "Salam! 👋 Mən sizin **24/7 Futbol AI Analitik Agenti** botunuzam.\n\n"
        "🌐 **Mən necə işləyirəm?**\n"
        "Mən canlı interneti axtarır, düşən əmsalların arxasındakı real səbəbləri (zədələr, rotasiya, maliyyə böhranı, hava) araşdırıram və sizə **Pul qoymaq olar/olmaz** qərarını verirəm.\n\n"
        "👇 Aşağıdakı düyməni sıxın və ya birbaşa istədiyiniz oyunu yazın (Məs: `Arsenal vs Chelsea`)."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "📉 Düşən Əmsalları Skan Et")
def handle_scan(message):
    bot.reply_to(message, "🔍 *Qlobal bazarlar skan edilir və internetdə ən kəskin düşən əmsallar araşdırılır...*\nZəhmət olmasa 15-20 saniyə gözləyin.", parse_mode="Markdown")
    report = analyze_football("", is_scan=True)
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Kömək")
def handle_help(message):
    bot.reply_to(message, "📌 *İstifadə qaydası:*\n\n1. **📉 Düşən Əmsalları Skan Et** düyməsinə basdıqda bu gün bazarda kəskin düşən oyunları tapıb analiz edirəm.\n2. İstənilən vaxt mənə oyun adı yazsanız (məs: `Qarabağ vs Neftçi`), həmin oyunun zədə və vəziyyətini dərhal internetdən tapıb təhlil edirəm.")

@bot.message_handler(func=lambda msg: True)
def handle_custom_match(message):
    bot.reply_to(message, f"🔎 *{message.text}* oyunu üzrə canlı internet araşdırması başlandı (zədələr, rotasiya, heyət xəbərləri)... Gözləyin.", parse_mode="Markdown")
    report = analyze_football(message.text, is_scan=False)
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

# ================= İŞƏ SALMA =================
if __name__ == "__main__":
    # 24/7 web serveri arxa planda başladırıq
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot 24/7 rejimdə işə düşdü...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
