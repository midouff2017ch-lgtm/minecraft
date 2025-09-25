import os
import time
import threading
import asyncio
import aiohttp
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
            connection.register_packet_listener(on_join, clientbound.play.JoinGamePacket)
            connection.register_packet_listener(on_disconnect, clientbound.login.DisconnectPacket)
            connection.register_packet_listener(on_disconnect, clientbound.play.DisconnectPacket)
            connection.connect()

            tick = 0
            while connection.connected:
                pkt = serverbound.play.ClientStatusPacket()
                pkt.action_id = 0
                connection.write_packet(pkt)

                tick += 1
                if tick % 10 == 0:
                    print(f"Bot still alive... {tick*30} seconds")

                time.sleep(30)

            print("⚠️ Lost connection, retrying in 10s...")
            time.sleep(10)

        except Exception as e:
            print("⚠️ Error in bot, retrying in 10s:", e)
            time.sleep(10)

# --- Async Keep-Alive Ping ---
async def keep_alive_task():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                url = "https://check-ban-e7pa.onrender.com"
                async with session.get(url) as response:
                    print(f"💡 Keep-Alive ping status: {response.status}")
            except Exception as e:
                print(f"⚠️ Keep-Alive error: {e}")
            await asyncio.sleep(60)  # كل دقيقة

# --- Main ---
if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🚀 Flask server started in background")

    # بدء حلقة asyncio للـ Keep-Alive
    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive_task())

    # تشغيل بوت الماينكرافت (الوظيفة الرئيسية) في نفس Thread الرئيسي
    run_mc_bot()
