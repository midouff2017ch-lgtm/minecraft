import os
import time
import threading
import random
from flask import Flask
from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound, serverbound

# --- Flask Keep-Alive ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MC Bot MIDOUXCHEAT is running and keeping Aternos awake!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Minecraft Bot Setup ---
MC_HOST = "midou1555.aternos.me"
MC_PORT = 26755
MC_USERNAME = "MIDOUXCHEAT"

def on_join(packet):
    print(f"[+] Bot {MC_USERNAME} joined the server!")

def on_disconnect(packet):
    print(f"❌ Disconnected from server. Reason: {packet.json_data}")

def run_mc_bot():
    while True:
        try:
            print(f"Connecting to {MC_HOST}:{MC_PORT} as {MC_USERNAME}")
            connection = Connection(MC_HOST, MC_PORT, username=MC_USERNAME)

            # Events
            connection.register_packet_listener(on_join, clientbound.play.JoinGamePacket)
            connection.register_packet_listener(on_disconnect, clientbound.login.DisconnectPacket)
            connection.register_packet_listener(on_disconnect, clientbound.play.DisconnectPacket)

            connection.connect()

            x, y, z = 0.0, 64.0, 0.0  # موقع افتراضي
            while True:
                # كل 30 ثانية رسالة أن البوت شغال
                print("Bot still alive...")

                # كل دقيقة يتحرك خطوة صغيرة يمين/يسار
                dx = random.choice([-0.5, 0.5])
                dz = random.choice([-0.5, 0.5])
                x += dx
                z += dz

                move = serverbound.play.PlayerPositionPacket()
                move.x, move.y, move.z = x, y, z
                move.on_ground = True
                connection.write_packet(move)

                print(f"Bot moved to ({x:.1f}, {y:.1f}, {z:.1f})")

                time.sleep(60)

        except Exception as e:
            print("⚠️ Error, retrying in 10s:", e)
            time.sleep(10)

# --- Start Everything ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    run_mc_bot()
