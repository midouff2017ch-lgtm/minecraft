import os
import time
import threading
from flask import Flask
from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound
from minecraft.exceptions import LoginDisconnect

# --- Flask Keep-Alive ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MC Bot is running and looping join/leave!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Minecraft Bot Setup ---
MC_HOST = "midou1555.aternos.me"
MC_PORT = 26755
MC_USERNAME = "MIDOUX"  # <-- الاسم

def on_join(packet):
    print(f"[+] Bot {MC_USERNAME} joined the server!")

def on_disconnect(packet):
    print(f"❌ Disconnected from server. Reason: {packet.json_data}")

def run_mc_bot():
    while True:
        try:
            print(f"🚪 Connecting to {MC_HOST}:{MC_PORT} as {MC_USERNAME}")
            connection = Connection(MC_HOST, MC_PORT, username=MC_USERNAME)

            # Events
            connection.register_packet_listener(on_join, clientbound.play.JoinGamePacket)
            connection.register_packet_listener(on_disconnect, clientbound.login.DisconnectPacket)
            connection.register_packet_listener(on_disconnect, clientbound.play.DisconnectPacket)

            connection.connect()

            # يبقى 5 ثواني داخل السيرفر
            time.sleep(5)

            # يخرج بنفسه
            print("🚪 Leaving server...")
            connection.disconnect()

            # ينتظر 5 ثواني برا
            time.sleep(5)

        except LoginDisconnect as e:
            print("❌ Login rejected by server:", e)
            time.sleep(5)

        except Exception as e:
            print("⚠️ Unexpected error:", e)
            time.sleep(5)

# --- Start Everything in Threads ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    bot_thread = threading.Thread(target=run_mc_bot, daemon=True)

    flask_thread.start()
    bot_thread.start()

    # Keep main thread alive
    while True:
        time.sleep(60)

