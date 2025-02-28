import os
import streamlit as st
from pytube import YouTube
import whisper
from googletrans import Translator
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip

# Step 1: Download YouTube video
def download_youtube_video(url, output_path="video.mp4"):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(filename=output_path)
    return output_path

# Step 2: Transcribe audio using Whisper
def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # Use "small", "medium", or "large" for better accuracy
    result = model.transcribe(audio_path)
    return result["text"]

# Step 3: Translate text using Google Translate
def translate_text(text, target_language="te"):  # Default to Telugu ("te")
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Step 4: Generate translated audio using gTTS
def generate_translated_audio(text, output_path="translated_audio.mp3", language="te"):
    tts = gTTS(text=text, lang=language)
    tts.save(output_path)
    return output_path

# Step 5: Replace original audio with translated audio
def replace_audio_in_video(video_path, audio_path, output_path="output_video.mp4"):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec="libx264")
    return output_path

# Streamlit App
def main():
    st.title("YouTube Video Translator and Dubbing")
    st.write("Upload a YouTube video URL, select a target language, and get a translated and dubbed video!")

    # Input: YouTube URL
    youtube_url = st.text_input("Enter YouTube Video URL:")

    # Input: Target Language
    target_language = st.selectbox(
        "Select Target Language",
        options=["te", "hi", "en", "es", "fr"],  # Add more languages as needed
        format_func=lambda x: {"te": "Telugu", "hi": "Hindi", "en": "English", "es": "Spanish", "fr": "French"}[x]
    )

    if st.button("Translate and Dub Video"):
        if youtube_url:
            with st.spinner("Processing..."):
                try:
                    # Step 1: Download video
                    st.write("Downloading video...")
                    video_path = download_youtube_video(youtube_url)

                    # Step 2: Transcribe audio
                    st.write("Transcribing audio...")
                    transcribed_text = transcribe_audio(video_path)
                    st.write("Transcribed Text:", transcribed_text)

                    # Step 3: Translate text
                    st.write("Translating text...")
                    translated_text = translate_text(transcribed_text, target_language)
                    st.write("Translated Text:", translated_text)

                    # Step 4: Generate translated audio
                    st.write("Generating translated audio...")
                    translated_audio_path = generate_translated_audio(translated_text, language=target_language)

                    # Step 5: Replace audio in video
                    st.write("Replacing audio in video...")
                    output_video_path = replace_audio_in_video(video_path, translated_audio_path)

                    # Display the output video
                    st.write("Done! Here's your translated and dubbed video:")
                    st.video(output_video_path)

                    # Provide a download link
                    with open(output_video_path, "rb") as file:
                        btn = st.download_button(
                            label="Download Video",
                            data=file,
                            file_name="translated_video.mp4",
                            mime="video/mp4"
                        )
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a valid YouTube URL.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
