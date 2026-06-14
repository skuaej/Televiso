import re
from aiohttp import web
from telethon import TelegramClient

# Your Telegram API credentials
api_id = 27479878
api_hash = '05f8dc8265d4c5df6376dded1d71c0ff'
bot_token = '8778522239:AAFIq6V5IzPtjGxoJI6mzpGBudEEJurMt50'

# The database channel where the videos are stored
channel_username = 'uuuujikkmuh'

# Initialize the client
client = TelegramClient('streamer_session', api_id, api_hash)

async def stream_video(request):
    """
    Handles the incoming request from your frontend video player,
    processes the seek bar (Range headers), and streams the file.
    """
    try:
        message_id = int(request.match_info['message_id'])
    except ValueError:
        return web.Response(status=400, text="Invalid message ID")
    
    # 1. Fetch the message containing the video from Telegram
    message = await client.get_messages(channel_username, ids=message_id)
    if not message or not message.video:
        return web.Response(status=404, text="Video not found in channel")

    file_size = message.video.size
    
    # 2. Handle 'Range' requests (This is the magic that makes the seek bar work)
    range_header = request.headers.get('Range', 'bytes=0-')
    match = re.match(r'bytes=(\d+)-(.*)', range_header)
    
    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else file_size - 1
    else:
        start = 0
        end = file_size - 1

    length = end - start + 1

    # 3. Build the HTTP 206 Partial Content headers
    headers = {
        'Content-Type': 'video/mp4',
        'Accept-Ranges': 'bytes',
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Content-Length': str(length),
        'Access-Control-Allow-Origin': '*' # Allows your web/Android player to access the stream
    }

    response = web.StreamResponse(status=206, headers=headers)
    await response.prepare(request)

    # 4. Stream the chunks from Telegram directly to the frontend player
    try:
        async for chunk in client.iter_download(
            message.media, 
            offset=start, 
            request_size=1024 * 1024, # Download in 1MB chunks
            limit=length
        ):
            await response.write(chunk)
    except Exception as e:
        print(f"Streaming interrupted: {e}")

    return response

async def main():
    # Start the Telethon client
    await client.start(bot_token=bot_token)
    
    # Set up the web server routes
    app = web.Application()
    
    # The endpoint will be: http://YOUR_VPS_IP:8080/stream/{message_id}
    app.router.add_get('/stream/{message_id}', stream_video)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Run the server on port 8080
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    print("Ummo TV Streaming Backend is live on port 8080...")
    await site.start()
    
    # Keep the server running continuously
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
    
