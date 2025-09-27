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

            # --- Events ---
            def handle_join(packet):
                print(f"[+] {username} joined the server!")

            def handle_disconnect(packet):
                print(f"❌ {username} disconnected: {packet.json_data}")

            connection.register_packet_listener(handle_join)
            connection.register_packet_listener(handle_disconnect)

            # --- Connect ---
            connection.connect()

            # --- Stay connected for 30s ---
            start_time = time.time()
            while connection.connected and (time.time() - start_time < 30):
                time.sleep(1)

            # --- Disconnect cleanly ---
            if connection.connected:
                print(f"🚪 {username} leaving server...")
                connection.disconnect()
                time.sleep(2)  # مهلة بسيطة للتأكد

        except LoginDisconnect as e:
            print(f"❌ Login rejected for {username}: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error for {username}: {e}")

        # --- Wait a bit before new account ---
        time.sleep(3)

# --- Start Everything ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    bot_thread = threading.Thread(target=run_mc_bot, daemon=True)

    flask_thread.start()
    bot_thread.start()

    while True:
        time.sleep(60)
