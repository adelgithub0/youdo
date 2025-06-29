from yt_dlp import YoutubeDL

def get_streams(url):
    ydl_opts = {'quiet': True, 'extract_flat': False}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            streams = []
            for f in info.get("formats", []):
                if f.get("filesize") and f.get("itag"):
                    label = f"{f['format_note']} - {f['ext']} - {round(f['filesize']/1024/1024, 1)}MB"
                    streams.append({
                        "itag": str(f["itag"]),
                        "label": label,
                        "type": "audio" if f["vcodec"] == "none" else "video"
                    })
            return streams
    except Exception as e:
        print("Error:", e)
        return []

def download_video(url, itag):
    try:
        ydl_opts = {
            'quiet': True,
            'format': itag,
            'outtmpl': 'video.%(ext)s'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.download([url])
        return "video.mp4" if os.path.exists("video.mp4") else None
    except Exception as e:
        print("Download error:", e)
        return None

def download_audio(url, itag):
    try:
        ydl_opts = {
            'quiet': True,
            'format': itag,
            'outtmpl': 'audio.%(ext)s'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.download([url])
        return "audio.mp3" if os.path.exists("audio.mp3") else None
    except Exception as e:
        print("Download error:", e)
        return None
