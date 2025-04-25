import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TABLE_NAME = os.getenv("TABLE_NAME")
TABLE_URL = os.getenv("TABLE_URL")

bot = Bot(token=BOT_TOKEN)
last_round = None

def extract_latest_round():
    try:
        response = requests.get(TABLE_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        result_elem = soup.find("div", class_="roadMap")
        round_info = soup.find("span", class_="roadIndex")
        if not round_info:
            return None, None
        round_number = int(round_info.text.replace("#", "").strip())
        last_three = ''.join([x.text.strip() for x in result_elem.select("div span")][-3:])
        return round_number, last_three
    except Exception as e:
        print("❌ ERROR:", e)
        return None, None

def analyze_pattern(data):
    if len(data) < 3:
        return "รอผลวิเคราะห์", 0
    if data[-1] == data[-2] == 'P':
        return "แทง: P", 88
    elif data[-1] == data[-2] == 'B':
        return "แทง: B", 88
    else:
        return "รอผลวิเคราะห์", 63

while True:
    round_number, last_three = extract_latest_round()
    if round_number and round_number != last_round:
        last_round = round_number
        prediction, confidence = analyze_pattern(last_three)
        message = (
            f"🎯 โต๊ะ: {TABLE_NAME} | ไม้ที่ {round_number}\n"
            f"{prediction}\n"
            f"📊 ความมั่นใจ: {confidence}%\n"
            f"🧠 ระบบ: B-SAFE++ RealStat Ultra Pro Engine"
        )
        print("📤 ส่งข้อความ:", message)
        bot.send_message(chat_id=CHAT_ID, text=message)
    time.sleep(5)
