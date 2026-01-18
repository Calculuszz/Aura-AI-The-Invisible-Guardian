import logging
import threading
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
from config import Config
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Notifier")

class Notifier:
    def __init__(self):
        self.last_alert_time = 0
        self.alert_cooldown = 10  # Seconds between alerts
        
        # Google Sheets Setup
        self.sheet = None
        self.setup_sheets()

    def setup_sheets(self):
        try:
            if os.path.exists(Config.GOOGLE_SHEETS_CREDENTIALS_FILE):
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_SHEETS_CREDENTIALS_FILE, scope)
                client = gspread.authorize(creds)
                
                # Open or Create Sheet
                try:
                    self.sheet = client.open(Config.GOOGLE_SHEET_NAME).sheet1
                except gspread.SpreadsheetNotFound:
                    logger.info("Sheet not found, creating new one...")
                    sh = client.create(Config.GOOGLE_SHEET_NAME)
                    sh.share(client.auth.service_account_email, perm_type='user', role='owner')
                    self.sheet = sh.sheet1
                    # Add Header
                    self.sheet.append_row(["Timestamp", "Event", "Location", "Details"])
                
                logger.info("Google Sheets connected successfully.")
            else:
                logger.warning(f"Google Sheets credentials not found at {Config.GOOGLE_SHEETS_CREDENTIALS_FILE}. Logging will be local only.")
        except Exception as e:
            logger.error(f"Failed to setup Google Sheets: {e}")

    def alert(self, event_type, location="Unknown"):
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Cooldown check for notifications (not logs)
        if (current_time.timestamp() - self.last_alert_time) < self.alert_cooldown:
            return

        self.last_alert_time = current_time.timestamp()
        
        message = f"ALARM: {event_type} detected at {location} on {timestamp}"
        logger.info(message)
        
        # Run in separate thread to not block video
        threading.Thread(target=self._send_async, args=(message, timestamp, event_type, location)).start()

    def _send_async(self, message, timestamp, event_type, location):
        # 1. Google Sheets
        if self.sheet:
            try:
                self.sheet.append_row([timestamp, event_type, location, message])
            except Exception as e:
                logger.error(f"Failed to log to Sheet: {e}")

        # 2. Telegram
        if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID:
            try:
                url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": message}
                requests.post(url, data=data)
            except Exception as e:
                logger.error(f"Failed to send Telegram: {e}")

        # 3. Webhook (Generic)
        if Config.WEBHOOK_URL:
             try:
                payload = {"text": message, "timestamp": timestamp}
                requests.post(Config.WEBHOOK_URL, json=payload)
             except Exception as e:
                logger.error(f"Failed to send Webhook: {e}")
