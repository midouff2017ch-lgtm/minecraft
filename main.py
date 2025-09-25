import os
import time
import threading
from flask import Flask
from minecraft.networking.connection import Connection
from minecraft.networking.packets import serverbound, clientbound

# --- Flask Keep-Alive ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MC Bot is running and keeping Aternos awake!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Minecraft Bot Setup ---
MC_HOST = "midou1555.aternos.me"
MC_PORT = 26755
MC_USERNAME = "KeepAliveBot"
MC_PROTOCOL = 754  # بروتوكول 1.16.5

def on_join(packet):
    print(f"[+] Bot {MC_USERNAME} joined the server!")

def run_mc_bot():
    while True:
        try:
            print(f"Connecting to {MC_HOST}:{MC_PORT} as {MC_USERNAME}")

            # هنا بدون LoginInfo
            connection = Connection(MC_HOST, MC_PORT, username=MC_USERNAME, allowed_versions=[MC_PROTOCOL])

            connection.register_packet_listener(on_join, clientbound.play.JoinGamePacket)
            connection.connect()

            tick = 0
            while True:
                pkt = serverbound.play.PlayerPositionAndLookPacket()
                pkt.x, pkt.y, pkt.z = 0.0, 64.0, 0.0
                pkt.yaw, pkt.pitch = 0.0, 0.0
                pkt.on_ground = True
                connection.write_packet(pkt)

                tick += 1
                if tick % 10 == 0:
                    print(f"Bot still alive... {tick*30} seconds")

                time.sleep(30)

        except Exception as e:
            print("⚠️ Error, retrying in 10s:", e)
            time.sleep(10)

# --- Start Everything ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    run_mc_bot()
