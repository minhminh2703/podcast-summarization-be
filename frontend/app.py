import os
import requests
import streamlit as st
import tempfile
from typing import Optional
import time

# Set the backend API URL
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")

# Set page configuration
st.set_page_config(
    page_title="Podcast Summarizer",
    page_icon="🎙️",
    layout="wide"
)

def upload_and_process(
    audio_file, 
    summary_type: str,
    max_length: int
) -> Optional[dict]:
    """Upload the audio file to the backend and get the summary"""
    
    if not audio_file:
        return None
    
    with st.spinner("Processing your podcast... This may take a few minutes."):
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Prepare the form data
            with open(tmp_file_path, "rb") as f:
                files = {
                    "file": (audio_file.name, f, f"audio/{os.path.splitext(audio_file.name)[1][1:]}")
                }
                data = {
                    "summarization_type": summary_type,
                    "max_summary_length": str(max_length)
                }

                response = requests.post(f"{BACKEND_API_URL}/summarize", files=files, data=data)
            
            
            # Check if the request was successful
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

def main():
    # App title and description
    st.title("🎙️ Podcast Summarizer")
    st.markdown("""
    Upload your podcast audio file and get a transcript and summary powered by AI.
    This app uses OpenAI's Whisper for transcription and GPT for summarization.
    """)
    
    # Sidebar with options
    st.sidebar.header("Settings")
    
    summary_type = st.sidebar.radio(
        "Summary Type",
        ["concise", "detailed", "bullets"],
        index=0,
        help="Choose the type of summary you want"
    )
    
    max_length = st.sidebar.slider(
        "Max Summary Length",
        min_value=100,
        max_value=1000,
        value=300,
        step=50,
        help="Maximum length of the summary in tokens"
    )
    
    # File uploader
    st.subheader("Upload Your Podcast")
    audio_file = st.file_uploader(
        "Upload an audio file (MP3, WAV, M4A)",
        type=["mp3", "wav", "m4a", "mp4"],
        help="Maximum file size: 200 MB"
    )
    
    # Check API connection
    try:
        response = requests.get(f"{BACKEND_API_URL}/")
        if response.status_code == 200:
            st.sidebar.success("✅ Connected to backend API")
        else:
            st.sidebar.error("❌ Cannot connect to backend API")
    except:
        st.sidebar.error("❌ Cannot connect to backend API")
    
    # Process button
    if audio_file:
        st.audio(audio_file, format=f"audio/{os.path.splitext(audio_file.name)[1][1:]}")
        
        if st.button("Generate Summary"):
            start_time = time.time()
            
            # Upload and process the file
            result = upload_and_process(audio_file, summary_type, max_length)
            
            if result:
                processing_time = time.time() - start_time
                st.success(f"Processing completed in {processing_time:.2f} seconds!")
                
                # Display duration of the podcast
                duration = result.get("duration", 0)
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                st.info(f"Podcast Duration: {int(hours)}h {int(minutes)}m {int(seconds)}s")
                
                # Create tabs for summary and full transcript
                tab1, tab2 = st.tabs(["Summary", "Full Transcript"])
                
                with tab1:
                    st.subheader("Podcast Summary")
                    
                    if summary_type == "bullets":
                        # If bullet points, try to split them and format
                        bullet_points = result["summary"].split("- ")
                        for point in bullet_points:
                            if point.strip():
                                st.markdown(f"- {point.strip()}")
                    else:
                        st.markdown(result["summary"])
                    
                    # Add a download button for the summary
                    st.download_button(
                        label="Download Summary",
                        data=result["summary"],
                        file_name="podcast_summary.txt",
                        mime="text/plain"
                    )
                
                with tab2:
                    st.subheader("Full Transcript")
                    st.markdown(result["transcription"])
                    
                    # Add a download button for the transcript
                    st.download_button(
                        label="Download Transcript",
                        data=result["transcription"],
                        file_name="podcast_transcript.txt",
                        mime="text/plain"
                    )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "Made with ❤️ using Streamlit, FastAPI, Whisper, and GPT"
    )

if __name__ == "__main__":
    main()