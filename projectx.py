import streamlit as st
import whisper
import ffmpeg
import subprocess
import os

# Load Whisper model (use "base" for faster results, "medium" or "large" for better accuracy)
model = whisper.load_model("base")

def generate_captions(video_path):
    """Generate captions from video using Whisper model."""
    # Extract audio from the video file using ffmpeg
    audio_path = "temp_audio.wav"
    ffmpeg.input(video_path).output(audio_path, ac=1, ar="16000").run(overwrite_output=True)

    # Transcribe the audio with forced language "en" (English)
    result = model.transcribe(audio_path, language="en")

    return result["segments"]

def format_time(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,MS)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

def create_caption_file(captions):
    """Create a subtitle file (.srt) from Whisper output."""
    srt_filename = "captions.srt"
    with open(srt_filename, "w", encoding="utf-8") as file:
        for idx, caption in enumerate(captions):
            start_time = caption['start']
            end_time = caption['end']
            text = caption['text']

            start_time_str = format_time(start_time)
            end_time_str = format_time(end_time)

            file.write(f"{idx + 1}\n")
            file.write(f"{start_time_str} --> {end_time_str}\n")
            file.write(f"{text}\n\n")
    
    return srt_filename

def add_subtitles_to_video(video_path, srt_file, output_path):
    """Overlay subtitles on the video using ffmpeg."""
    ffmpeg.input(video_path).output(output_path, vf=f"subtitles={srt_file}:force_style='Fontsize=24,PrimaryColour=&HFFFFFF&'").run(overwrite_output=True)

def main():
    st.title("Video Caption Generator")
    st.write("Upload a video, and we will generate captions for you.")

    # Upload video file
    video_file = st.file_uploader("Choose a video file", type=["mp4", "mkv", "avi", "mov"])

    if video_file is not None:
        # Save the uploaded video to a temporary file
        temp_video_path = "temp_video" + os.path.splitext(video_file.name)[1]
        with open(temp_video_path, "wb") as f:
            f.write(video_file.getbuffer())

        # Generate captions
        st.write("Generating captions...")
        captions = generate_captions(temp_video_path)

        # Create caption file (SRT)
        srt_file = create_caption_file(captions)

        # Generate video with subtitles
        output_file = "output_with_captions.mp4"
        add_subtitles_to_video(temp_video_path, srt_file, output_file)

        # Provide download link for the video with captions
        st.write("Captions generated! You can download the video with captions below.")
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download captioned video",
                data=f,
                file_name=output_file,
                mime="video/mp4"
            )

        # Clean up temporary files
        os.remove(temp_video_path)
        os.remove(srt_file)
        os.remove(output_file)

if __name__ == "__main__":
    main()
