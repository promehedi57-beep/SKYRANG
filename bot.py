import asyncio
import logging
from collections import deque
import time

import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ======================== কনফিগারেশন ========================
TELEGRAM_TOKEN = "8647348457:AAEi5Kre2Df4Xeig80aZzsd_7zR9MFO739Y"
TELEGRAM_CHAT_ID = "-1003800508577"  

API_URL = "https://x.mnitnetwork.com/mapi/v1/mdashboard/console/info"

# তোমার ব্রাউজার থেকে পাওয়া একদম নতুন টোকেন এবং কুকি
MAUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNX0k0VkE3RkU2UiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NzY4Mjg4NzgsImNyZWF0ZWQiOjE3NzY3NDI0NzgsIjJvbzkiOiJNc0giLCJleHAiOjE3NzY4Mjg4NzgsImlhdCI6MTc3Njc0MjQ3OCwic3ViIjoiTV9JNFZBN0ZFNlIifQ.LeXHWzXyMq0I0nNNnmdhDjk012ptMwhjvpMudjycebI"

COOKIE_DATA = "mauthtoken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNX0k0VkE3RkU2UiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NzY4Mjg4NzgsImNyZWF0ZWQiOjE3NzY3NDI0NzgsIjJvbzkiOiJNc0giLCJleHAiOjE3NzY4Mjg4NzgsImlhdCI6MTc3Njc0MjQ3OCwic3ViIjoiTV9JNFZBN0ZFNlIifQ.LeXHWzXyMq0I0nNNnmdhDjk012ptMwhjvpMudjycebI; cf_clearance=zR2O5_AmdhDIeQftiaZfNwSqFRDifr2ehHNQu6Jw8q4-1776774653-1.2.1.1-nhuG0sMStguP0dzU8D5_GYYe1lqY.uAqbc7OCQJYDpYQBkAm_pdg6E99Tuj1JYX8MNh4.9FLwm1mWHd.uwADn85mKdwImpDowYQgPcWDFLqoYd1YZL9kkxSiHltckMnJx1ePoHi0_vACV_p1bY5uRrrj6sNVVprnfRBg93s1xHKt.k305d2DUYyfMt5Yap5JZx_hYY9jj00dgffd9aVe5eRPdsCU1dHVChmRaKQ.i.Ptq2yrCLfc.R_9EQuQ32Q3qv6nZUPpgidVGXBdsjcWGafamjflt81WsTkMLdC4MuBwD3xR8FiuO1xKdAntXMwdTgT7yUFDVHIjyF29wQR7kw; TawkConnectionTime=0; twk_uuid_681787a55d55ef191a9da720=%7B%22uuid%22%3A%221.Ws5fNn3B3jtPb5VwJIV72bULtbVrmIGVECkvIdlVtObmwTts0jfxpP7wOqftlRphv8hGSHEouYvyMG8KX6vsSezC5RRocZQO3z6AWCeEWJFEAETJ73gSnDcqX%22%2C%22version%22%3A3%2C%22domain%22%3A%22mnitnetwork.com%22%2C%22ts%22%3A1776774655643%7D"

# ট্র্যাকিং 
processed_ids = deque(maxlen=10000)

FLAG_MAP = {
    "Bangladesh": "🇧🇩", "India": "🇮🇳", "Pakistan": "🇵🇰", "Sri Lanka": "🇱🇰", "Nepal": "🇳🇵",
    "United States": "🇺🇸", "UK": "🇬🇧", "United Kingdom": "🇬🇧", "Canada": "🇨🇦", "Australia": "🇦🇺",
    "Brazil": "🇧🇷", "Argentina": "🇦🇷", "Mexico": "🇲🇽", "Colombia": "🇨🇴", "Peru": "🇵🇪",
    "Russia": "🇷🇺", "Ukraine": "🇺🇦", "Germany": "🇩🇪", "France": "🇫🇷", "Italy": "🇮🇹", "Spain": "🇪🇸",
    "Indonesia": "🇮🇩", "Vietnam": "🇻🇳", "Philippines": "🇵🇭", "Thailand": "🇹🇭", "Malaysia": "🇲🇾",
    "Myanmar": "🇲🇲", "Cambodia": "🇰🇭", "Laos": "🇱🇦", "Singapore": "🇸🇬", "Japan": "🇯🇵", "South Korea": "🇰🇷",
    "China": "🇨🇳", "Taiwan": "🇹🇼", "Hong Kong": "🇭🇰",
    "Nigeria": "🇳🇬", "Egypt": "🇪🇬", "South Africa": "🇿🇦", "Kenya": "🇰🇪", "Morocco": "🇲🇦",
    "Algeria": "🇩🇿", "Ivory Coast": "🇨🇮", "Cameroon": "🇨🇲", "Ghana": "🇬🇭", "Senegal": "🇸🇳",
    "Turkey": "🇹🇷", "Saudi Arabia": "🇸🇦", "UAE": "🇦🇪", "Iran": "🇮🇷", "Iraq": "🇮🇶", "Israel": "🇮🇱",
    "Tajikistan": "🇹🇯", "Uzbekistan": "🇺🇿", "Kazakhstan": "🇰🇿", "Kyrgyzstan": "🇰🇬",
    "Cuba": "🇨🇺", "Madagascar": "🇲🇬", "Guinea Republic": "🇬🇳", "Sierra Leone": "🇸🇱",
    "Central African Republic": "🇨🇫"
}

def get_flag(country_name: str) -> str:
    for name, flag in FLAG_MAP.items():
        if name.lower() in str(country_name).lower():
            return flag
    return "🌍"

def format_to_range(log_range: str) -> str:
    val = str(log_range).strip()
    if not val:
        return ""
    if 'X' in val.upper():
        return val.upper()
    else:
        return val + "XXX"

def create_range_message(app_name: str, number_range: str, country: str, carrier: str, sms_text: str) -> str:
    flag = get_flag(country)
    app_display = app_name.title() if app_name else "Facebook"
    if "TWILIO" in app_display.upper(): app_display = "WhatsApp/Twilio"

    carrier_display = carrier.title() if carrier else "Unknown"
    
    # SMS টেক্সট সুন্দর করে সাজানো (যদি অনেক বড় হয়, তাহলে একটু কেটে দেওয়া হবে যাতে মেসেজ হাবিজাবি না লাগে)
    clean_sms = str(sms_text).strip() if sms_text else "No SMS data available"
    if len(clean_sms) > 80:
        clean_sms = clean_sms[:77] + "..."

    # একদম ফ্রেশ এবং প্রফেশনাল ভিআইপি ডিজাইন
    text = (
        f"✅ **New Active Range** ✅\n\n"
        f"🌍 **Country:** {flag} {country}\n"
        f"📶 **Range:** `{number_range}`\n"
        f"🏢 **Carrier:** {carrier_display}\n"
        f"🔵 **Service:** {app_display}\n"
        f"💬 **SMS:** `{clean_sms}`\n\n"
        f"💎 **Powered By [SKY](https://t.me/SKYSMSOWNER)**"
    )
    return text

async def send_range_to_telegram(session: aiohttp.ClientSession, app_name: str, number_range: str, country: str, carrier: str, sms_text: str):
    text = create_range_message(app_name, number_range, country, carrier, sms_text)
    
    # বোতামগুলো সুন্দর করে দেওয়া হলো
    reply_markup = {
        "inline_keyboard": [
            [{"text": "🚀 Get Number Now 🚀", "url": "https://t.me/SKYSMSPRO_BOT"}],
            [{"text": "📞 Join Our Channel", "url": "https://t.me/SKYOFFICIALCHANNEL1"}]
        ]
    }

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
        "reply_markup": reply_markup
    }

    while True:
        try:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    logger.info(f"✅ লাইভ রেঞ্জ পাঠানো হয়েছে: {app_name} | {country} | {number_range}")
                    break  
                elif resp.status == 429:
                    data = await resp.json()
                    retry_after = data.get("parameters", {}).get("retry_after", 30)
                    logger.warning(f"⚠️ Telegram Limit! {retry_after} সেকেন্ড অপেক্ষা...")
                    await asyncio.sleep(retry_after + 1) 
                else:
                    logger.error(f"❌ টেলিগ্রাম এরর: {await resp.text()}")
                    break
        except Exception as e:
            logger.error(f"❌ টেলিগ্রামে পাঠাতে ব্যর্থ: {e}")
            await asyncio.sleep(3)
            break

async def fetch_console_logs(session: aiohttp.ClientSession, url: str) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Mauthtoken": MAUTH_TOKEN,
        "Cookie": COOKIE_DATA,
        "Referer": "https://x.mnitnetwork.com/mdashboard/console"
    }
    try:
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                try:
                    data = await resp.json()
                except Exception:
                    data = {}

                if isinstance(data, dict):
                    inner_data = data.get("data", {})
                    if isinstance(inner_data, dict) and "logs" in inner_data:
                        return inner_data.get("logs", [])
                        
                return []
            elif resp.status == 401:
                logger.error("❌ 401 Unauthorized: টোকেনের মেয়াদ শেষ। ব্রাউজার থেকে নতুন টোকেন এনে বসান।")
            elif resp.status == 403:
                logger.error("❌ 403 Forbidden: Cloudflare ব্লক করেছে, কুকি আপডেট করুন।")
            else:
                logger.error(f"⚠️ API থেকে রেসপন্স: {resp.status}")
    except Exception as e:
        logger.error(f"API ফেচ এরর: {e}")
    return []

async def monitor_loop():
    logger.info("🚀 SKY Live Range Broadcaster Started (VIP Design Mode)")
    
    last_heartbeat = time.time()
    
    async with aiohttp.ClientSession() as session:
        while True:
            all_logs = await fetch_console_logs(session, API_URL)
            new_data_found = False
            
            if all_logs:
                for log in reversed(all_logs):
                    msg_id = log.get("id")
                    
                    if msg_id and msg_id not in processed_ids:
                        app_name = log.get("app_name", "Unknown")
                        carrier = log.get("carrier", "Unknown")
                        sms_text = log.get("sms", "") # সার্ভার থেকে SMS ডেটা নেওয়া হচ্ছে
                        
                        raw_range = log.get("range") or log.get("number", "")
                        number_range = format_to_range(raw_range) 
                        
                        country = log.get("country", "Global")
                        
                        if number_range:
                            await send_range_to_telegram(session, app_name, number_range, country, carrier, sms_text)
                            processed_ids.append(msg_id)
                            new_data_found = True
                            
                            await asyncio.sleep(3.1)
            
            if not new_data_found:
                if time.time() - last_heartbeat > 30:
                    logger.info("⏳ নতুন কোনো রেঞ্জ আসেনি, প্যানেলে চেক করা হচ্ছে...")
                    last_heartbeat = time.time()
            
            await asyncio.sleep(3)

async def main():
    print("="*50)
    print("☁️ SKY Live Range Broadcaster Running...")
    print("="*50)
    await monitor_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 ব্রডকাস্টার বন্ধ করা হয়েছে।")
