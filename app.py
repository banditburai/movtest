import streamlit as st
import os
import subprocess

ffmpeg_path = 'ffmpeg'

# Function to save uploaded files
def save_uploaded_files(uploaded_files, directory='temp'):
    file_paths = []
    for uploaded_file in uploaded_files:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(filepath)
        except Exception as e:
            st.error(f'Failed to save file: {e}')
            return None
    return file_paths

# Function to create video from images
def create_video(image_paths, output_video_path):
    if len(image_paths) != 2:
        st.error("Please upload exactly two images.")
        return False
    
    command = [
    ffmpeg_path,
    '-y',
    '-loop', '1',
    '-i', image_paths[0],  # First image input
    '-loop', '1',
    '-i', image_paths[1],  # Second image input
    '-filter_complex', 'xfade=transition=fade:duration=1:offset=2,format=yuv420p',  # Crossfade filter
    '-t', '5',  # Total duration of the output video
    output_video_path
]


    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        st.error(f"FFmpeg Error: {process.stderr}")
        return False
    else:
        st.success("Video created successfully!")
        return True

st.title("FFmpeg Image-to-Video Creator")

# Single uploader for multiple files
uploaded_files = st.file_uploader("Upload two images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if st.button('Create Video'):
    if uploaded_files and len(uploaded_files) == 2:
        image_paths = save_uploaded_files(uploaded_files)
        if image_paths:
            output_video_path = os.path.join('temp', 'output_video.mp4')
            if create_video(image_paths, output_video_path):
                with open(output_video_path, "rb") as file:
                    st.download_button(label="Download Video", data=file, file_name="output_video.mp4", mime="video/mp4")
    else:
        st.warning("Please upload exactly two images to create a video.")
