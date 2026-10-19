import yt_dlp

def baixar_audio_wav(url, pasta_destino='./audios'):
    ydl_opts = {
        
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': f'{pasta_destino}/%(title)s.%(ext)s',
        'ignoreerrors': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    baixar_audio_wav("https://www.youtube.com/watch?v=9vMh9f41pqE&list=RD9vMh9f41pqE&start_radio=1")

