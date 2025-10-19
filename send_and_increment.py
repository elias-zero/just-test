#!/usr/bin/env python3
# send_and_increment.py
import os
import sys
import requests
import subprocess

COUNTER_FILE = os.getenv("COUNTER_FILE", "counter.txt")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("ERROR: TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID غير مضبوطين في المتغيرات البيئية.")
    sys.exit(1)

def read_counter(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                return 1
            return int(txt)
    except FileNotFoundError:
        return 1
    except Exception as e:
        print("Error reading counter:", e)
        raise

def write_counter(path, value):
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(value) + "\n")

def git_commit_and_push(file_path, message):
    try:
        # Configure committer identity
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)

        subprocess.run(["git", "add", file_path], check=True)
        # commit only if there are changes
        result = subprocess.run(["git", "diff", "--staged", "--quiet"])
        # git diff --staged --quiet returns exit code 1 if there are staged changes
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", message], check=True)
            subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
            print("Committed and pushed updated counter.")
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print("Git error:", e)
        raise

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    resp = requests.post(url, data=payload, timeout=30)
    print("Telegram API HTTP", resp.status_code)
    print("Response:", resp.text)
    resp.raise_for_status()

def main():
    try:
        current = read_counter(COUNTER_FILE)
        message = f"كوبون رقم {current}"
        print("Sending:", message)
        send_message(TOKEN, CHAT_ID, message)
        next_val = current + 1
        write_counter(COUNTER_FILE, next_val)
        print(f"Counter updated: {current} -> {next_val}")
        # Commit and push change back to repo so next run continues the sequence
        git_commit_and_push(COUNTER_FILE, f"Increment coupon counter to {next_val}")
    except Exception as e:
        print("Fatal error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
