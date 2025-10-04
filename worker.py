#!/usr/bin/env python3
import requests
import re
from datetime import datetime, timezone, timedelta

# --- Config ---
M3U_URLS = [
    "https://raw.githubusercontent.com/Akash802980/Sl/refs/heads/main/slv.m3u",
    "https://raw.githubusercontent.com/Akash802980/nxtm3u/refs/heads/main/backend.m3u",
    "https://raw.githubusercontent.com/Akash802980/Mar-M/refs/heads/main/mr.m3u",
    "https://zee-worker.1akiytb4.workers.dev/",
]
# --- Direct Token & Chat ID ---
TELEGRAM_BOT_TOKEN = "8253188928:AAGpN7UWpPdGOPLyBDaJSyRHzbMNxzjoKgE"  # Apna bot token
CHAT_ID = "5496402943"                                        # Apna numeric chat ID

def send_telegram(msg: str):
    """Send Telegram notification"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)

def unix_to_ist(unix_time: int) -> datetime:
    return datetime.fromtimestamp(unix_time, tz=timezone.utc) + timedelta(hours=5, minutes=30)

def check_expiry(m3u_url: str) -> str:
    """Return single line status for this playlist"""
    try:
        resp = requests.get(m3u_url, timeout=15)
        resp.raise_for_status()
        data = resp.text.splitlines()[:50]  # **first 50 lines**
    except Exception:
        return f"❌ {m3u_url.split('/')[-1]}: Failed to fetch"

    exp_time = None
    for line in data:
        match = re.search(r"exp=(\d+)", line)
        if match:
            exp_time = int(match.group(1))
            break

    m3u_name = m3u_url.split("/")[-1]

    if not exp_time:
        return f"⚠️ {m3u_name}: No exp token found"

    exp_dt = unix_to_ist(exp_time)
    now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

    if exp_dt < now:
        diff = now - exp_dt
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        return f"⚡ {m3u_name} expired | Expired {hours}h {minutes}m ago"
    else:
        diff = exp_dt - now
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        return f"✅ {m3u_name} valid | Expires in {hours}h {minutes}m"

# --- Main ---
if __name__ == "__main__":
    message_lines = []
    for url in M3U_URLS:
        line = check_expiry(url)
        message_lines.append(line)
    final_msg = "\n".join(message_lines)
    send_telegram(final_msg)
