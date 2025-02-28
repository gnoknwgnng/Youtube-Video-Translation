import streamlit as st
import yt_dlp
import os
import subprocess
from googletrans import Translator
from google.cloud import speech
import coqui_tts
import ffmpeg

def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_audio.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return "downloaded_audio.wav"

def transcribe_audio(audio_file):
    client = speech.SpeechClient()
    with open(audio_file, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )
    response = client.recognize(config=config, audio=audio)
    return " ".join([result.alternatives[0].transcript for result in response.results])

def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text

def generate_voice(translated_text, output_file):
    tts = coqui_tts.TTS("tts_models/en/ljspeech/tacotron2-DDC")
    tts.tts_to_file(translated_text, file_path=output_file)

def sync_video_with_audio(video_file, audio_file, output_file):
    command = [
        "python", "Wav2Lip/inference.py", 
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip.pth", 
        "--face", video_file, 
        "--audio", audio_file
    ]
    subprocess.run(command)
    os.rename("results/result_voice.mp4", output_file)

def main():
    st.title("YouTube Video Translator")
    video_url = st.text_input("Enter YouTube Video URL")
    target_language = st.selectbox("Select Target Language", ["te", "hi", "fr", "es"])
    if st.button("Translate Video"):
        st.write("Downloading audio...")
        audio_file = download_audio(video_url)
        
        st.write("Transcribing speech...")
        text = transcribe_audio(audio_file)
        
        st.write("Translating text...")
        translated_text = translate_text(text, target_language)
        
        st.write("Generating voice...")
        generated_audio = "translated_audio.wav"
        generate_voice(translated_text, generated_audio)
        
        st.write("Syncing video...")
        output_video = "translated_video.mp4"
        sync_video_with_audio("downloaded_video.mp4", generated_audio, output_video)
        
        st.video(output_video)
        st.success("Translation completed!")

if __name__ == "__main__":
    main()
