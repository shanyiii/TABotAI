import discord
from qdrant_langchain import qdrant_retrieval
from config import DISCORD_TOKEN

# client 是跟 discord 連接，intents 是要求機器人的權限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

# 調用event函式庫
@client.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份：{client.user}")

@client.event
# 當頻道有新訊息
async def on_message(message):
    # 排除機器人本身的訊息，避免無限循環
    if message.author == client.user:
        return
    
    print("Message received: ", message.content)
    response_text = await qdrant_retrieval(message.content)
    await message.channel.send(response_text)

client.run(DISCORD_TOKEN)
