import os
import time
import threading
import random
from flask import Flask
from minecraft.networking.connection import Connection
from minecraft.exceptions import LoginDisconnect

# --- Flask Keep-Alive ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MC Bot is running with random accounts!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Minecraft Bot Setup ---
MC_HOST = "midou1555.aternos.me"
MC_PORT = 26755

def generate_username():
    return "BOT" + str(random.randint(1000, 9999))

def run_mc_bot():
    while True:
        username = generate_username()
        print(f"🚪 Connecting to {MC_HOST}:{MC_PORT} as {username}")

        try:
            connection = Connection(MC_HOST, MC_PORT, username=username)

            # توابع عند النجاح أو الطرد
            def handle_join_packet(packet):
                print(f"[+] {username} joined the server!")

            def handle_disconnect(packet):
                print(f"❌ Disconnected: {packet.json_data}")

            connection.register_packet_listener(handle_join_packet)
            connection.register_packet_listener(handle_disconnect)

            # الاتصال
            connection.connect()

            # خليه 30 ثانية متصل
            time.sleep(30)

            # اغلاق الاتصال بشكل مرتب
            print(f"🚪 {username} leaving server...")
            connection.socket.close()
            connection.running = False

        except LoginDisconnect as e:
            print(f"❌ Login rejected for {username}: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error for {username}: {e}")

        # استراحة قبل إعادة الدخول بحساب جديد
        time.sleep(2)

# --- Start Everything in Threads ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    bot_thread = threading.Thread(target=run_mc_bot, daemon=True)

    flask_thread.start()
    bot_thread.start()

    while True:
        time.sleep(60)
