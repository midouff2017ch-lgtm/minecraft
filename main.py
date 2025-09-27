import os
import time
import threading
import random
from flask import Flask
from minecraft.networking.connection import Connection
from minecraft.networking.packets import serverbound, clientbound
from minecraft.exceptions import LoginDisconnect

# --- Flask Keep-Alive ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MC Bot is running and keeping alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Minecraft Bot Setup ---
MC_HOST = "midou1555.aternos.me"
MC_PORT = 26755
MC_USERNAME = "MIDOUXBOT"  # <-- هنا الاسم الجديد

should_reconnect = False

def on_join(packet):
    print(f"[+] Bot {MC_USERNAME} joined the server!")

def on_disconnect(packet):
    global should_reconnect
    print(f"❌ Disconnected from server. Reason: {packet.json_data}")
    should_reconnect = True

def run_mc_bot():
    global should_reconnect
    while True:
        should_reconnect = False
        try:
            print(f"Connecting to {MC_HOST}:{MC_PORT} as {MC_USERNAME}")
            connection = Connection(MC_HOST, MC_PORT, username=MC_USERNAME)

            # Events
            connection.register_packet_listener(on_join, clientbound.play.JoinGamePacket)
            connection.register_packet_listener(on_disconnect, clientbound.login.DisconnectPacket)
            connection.register_packet_listener(on_disconnect, clientbound.play.DisconnectPacket)

            connection.connect()

            x, y, z = 0.0, 64.0, 0.0
            while connection.connected:
                # حركة عشوائية بسيطة كل 60 ثانية
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

        except (ConnectionResetError, EOFError) as e:
            print("⚠️ Connection error, retrying in 10s:", e)
            should_reconnect = True

        except LoginDisconnect as e:
            print("❌ Login rejected by server:", e)
            should_reconnect = False

        except Exception as e:
            print("⚠️ Unexpected error:", e)
            should_reconnect = True

        if should_reconnect:
            print("🔄 Reconnecting in 10 seconds...")
            time.sleep(10)
        else:
            print("🛑 Bot stopped (no reconnect).")
            break

# --- Start Everything in Threads ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    bot_thread = threading.Thread(target=run_mc_bot, daemon=True)

    flask_thread.start()
    bot_thread.start()

    # Keep main thread alive
    while True:
        time.sleep(60)

