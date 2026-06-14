import os
import subprocess
from telethon import TelegramClient, events

# Your Telegram API credentials
api_id = 27479878
api_hash = '05f8dc8265d4c5df6376dded1d71c0ff'
bot_token = '8778522239:AAFIq6V5IzPtjGxoJI6mzpGBudEEJurMt50'

# The target public channel
target_channel = 'https://t.me/uuuujikkmuh' 

# Initialize the client
client = TelegramClient('vps_bot_session', api_id, api_hash).start(bot_token=bot_token)

def prepare_video_note(input_file, output_file):
    """
    Uses FFmpeg to crop the center of the video into a 1:1 square.
    """
    command = [
        'ffmpeg', '-y', '-i', input_file,
        '-vf', "crop='min(iw,ih):min(iw,ih)',scale=384:384",
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '24',
        '-c:a', 'aac', '-b:a', '128k',
        output_file
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Listen for any private message sent to the bot that contains a video
@client.on(events.NewMessage(func=lambda e: e.is_private and e.video))
async def handle_video(event):
    status_msg = await event.reply("📥 Downloading video to VPS...")
    
    # 1. Download the video to the VPS
    try:
        downloaded_file = await event.download_media()
        processed_file = f"ready_{event.id}.mp4"
    except Exception as e:
        await status_msg.edit(f"❌ Download failed: {str(e)}")
        return

    # 2. Format the video using FFmpeg
    await status_msg.edit("⚙️ Processing video with FFmpeg...")
    prepare_video_note(downloaded_file, processed_file)

    # 3. Upload to the target channel
    await status_msg.edit(f"📤 Uploading to {target_channel}...")
    try:
        await client.send_file(
            target_channel, 
            processed_file, 
            video_note=True, 
            caption="Automated upload via VPS bot"
        )
        await status_msg.edit("✅ Upload successful! Check your channel.")
    except Exception as e:
        await status_msg.edit(f"❌ Upload failed: {str(e)}")

    # 4. Clean up VPS storage
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)
    if os.path.exists(processed_file):
        os.remove(processed_file)

print("Bot is running! Send a video to your bot to start.")
# This keeps the script running 24/7 on your VPS
client.run_until_disconnected()
