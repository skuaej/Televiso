import os
from telethon import TelegramClient, events

# Your Telegram API credentials
api_id = 27479878
api_hash = '05f8dc8265d4c5df6376dded1d71c0ff'
bot_token = '8778522239:AAFIq6V5IzPtjGxoJI6mzpGBudEEJurMt50'

# The target public channel
target_channel = 'https://t.me/uuuujikkmuh' 

# Initialize the client
client = TelegramClient('vps_bot_session', api_id, api_hash).start(bot_token=bot_token)

# Listen for private messages containing a video
@client.on(events.NewMessage(func=lambda e: e.is_private and e.video))
async def handle_video(event):
    status_msg = await event.reply("📥 Downloading horizontal video...")
    
    # 1. Download the raw video
    try:
        downloaded_file = await event.download_media()
    except Exception as e:
        await status_msg.edit(f"❌ Download failed: {str(e)}")
        return

    # 2. Upload directly to the target channel (No FFmpeg formatting needed)
    await status_msg.edit(f"📤 Uploading as standard video...")
    try:
        uploaded_msg = await client.send_file(
            target_channel, 
            downloaded_file, 
            # NOTICE: video_note=True has been removed completely!
            supports_streaming=True, # Allows the video to be streamed smoothly
            caption="Standard Widescreen Upload"
        )
        
        # Construct the standard Telegram Embed Link
        embed_link = f"https://t.me/uuuujikkmuh/{uploaded_msg.id}?embed=1"
        
        await status_msg.edit(f"✅ Upload successful!\n🔗 Your Player Link: {embed_link}")
    except Exception as e:
        await status_msg.edit(f"❌ Upload failed: {str(e)}")

    # 3. Clean up storage
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)

print("Bot is running! Send a video to your bot to start.")
client.run_until_disconnected()
