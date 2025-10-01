#!/usr/bin/env python3
import requests
import re
from datetime import datetime, timezone, timedelta

# --- Config ---
M3U_URLS = [
    "https://raw.githubusercontent.com/Akash802980/Sl/refs/heads/main/slv.m3u",
    "https://raw.githubusercontent.com/Akash802980/nxtm3u/refs/heads/main/backend.m3u",
    "https://raw.githubusercontent.com/Akash802980/Mar-M/refs/heads/main/mr.m3u",
]

# --- Direct Token & Chat ID ---
TELEGRAM_BOT_TOKEN = "8253188928:AAGpN7UWpPdGOPLyBDaJSyRHzbMNxzjoKgE"  # Apna bot token
CHAT_ID = "5496402943"                                        # Apna numeric chat ID

def send_telegram(msg: str):
    """Send Telegram notification and log response"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        print("Telegram Response:", resp.status_code, resp.text)
    except Exception as e:
        print("Telegram Error:", e)

def unix_to_ist(unix_time: int) -> datetime:
    return datetime.fromtimestamp(unix_time, tz=timezone.utc) + timedelta(hours=5, minutes=30)

def check_expiry(m3u_url: str):
    try:
        resp = requests.get(m3u_url, timeout=15)
        resp.raise_for_status()
        data = resp.text
    except Exception as e:
        send_telegram(f"❌ Failed to fetch {m3u_url}: {e}")
        return

    matches = re.findall(r"exp=(\d+)", data)
    if not matches:
        send_telegram(f"⚠️ No exp token found in {m3u_url}")
        return

    exp_time = int(matches[0])
    exp_dt = unix_to_ist(exp_time)
    now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

    if exp_dt < now:
        diff = now - exp_dt
        minutes = diff.total_seconds() // 60
        hours = minutes // 60
        minutes = minutes % 60
        send_telegram(f"⚡ Stream expired!\nFile: {m3u_url}\nExpired at: {exp_dt.strftime('%Y-%m-%d %H:%M:%S')} IST\nNow: {now.strftime('%Y-%m-%d %H:%M:%S')} IST\nExpired {int(hours)}h {int(minutes)}m ago")
    else:
        diff = exp_dt - now
        minutes = diff.total_seconds() // 60
        hours = minutes // 60
        minutes = minutes % 60
        send_telegram(f"✅ Stream valid!\nFile: {m3u_url}\nExpires at: {exp_dt.strftime('%Y-%m-%d %H:%M:%S')} IST\nRemaining: {int(hours)}h {int(minutes)}m")
        print(f"[OK] {m3u_url} valid till {exp_dt.strftime('%Y-%m-%d %H:%M:%S')} IST")

# --- Main ---
if __name__ == "__main__":
    for url in M3U_URLS:
        check_expiry(url)
        
