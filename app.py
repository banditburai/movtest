import streamlit as st
from PIL import Image
import subprocess
import tempfile
import shutil
import os

# Function to process and display uploaded images
def process_images(uploaded_files):
    image_assignments = {}
    cols = st.columns(4)  # Create four columns for the grid layout
    col_index = 0
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as f:
            shutil.copyfileobj(uploaded_file, f)
            temp_file_path = f.name

        # Display thumbnail in the respective column
        with cols[col_index]:
            st.image(uploaded_file, use_column_width='always')
            
            # User input for quadrant and position, default 'NOT ASSIGNED'
            quadrant = st.selectbox("Select quadrant", ['NOT ASSIGNED', 1, 2, 3, 4], key=f'quadrant_{uploaded_file.name}')
            position = st.selectbox("Select position", ['NOT ASSIGNED', 'Before', 'After'], key=f'position_{uploaded_file.name}')

            if quadrant != 'NOT ASSIGNED' and position != 'NOT ASSIGNED':
                image_assignments[(quadrant, position)] = temp_file_path

        col_index = (col_index + 1) % 4  # Move to the next column

    return image_assignments

# Main app
def main():
    
    st.title("Image Crossfade App")
    
    uploaded_files = st.file_uploader("Upload images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    output_file_name = st.text_input("Enter the name for the output file (without extension)", "output")
    output_file_name = output_file_name if output_file_name else "output"

    if uploaded_files:
        image_assignments = process_images(uploaded_files)
        
        hold_duration = st.slider("Hold duration on each image (seconds)", 0.5, 5.0, 2.0, 0.1)
        crossfade_duration = st.slider("Crossfade duration (seconds)", 0.5, 5.0, 1.0, 0.1)
        total_length = 4 * (hold_duration + crossfade_duration) 

        if len(image_assignments) == 8:

            # Constructing FFmpeg command
            ffmpeg_command = ['ffmpeg', '-y']
            sorted_assignments = sorted(image_assignments.items(), key=lambda x: (x[0][0], x[0][1] == 'After'))
            for _, path in sorted_assignments:
                ffmpeg_command.extend(['-loop', '1', '-t', str(hold_duration + crossfade_duration), '-i', path])
            
            filter_complex = ""
            for i in range(4):  # 4 pairs
                filter_complex += f"[{2*i}:v][{2*i+1}:v]xfade=transition=fade:duration={crossfade_duration}:offset={hold_duration}[pair{i}];"
            filter_complex += "[pair0][pair1]hstack[top];[pair2][pair3]hstack[bottom];[top][bottom]vstack,format=yuv420p[v]"
            ffmpeg_command.extend(['-filter_complex', filter_complex, '-map', '[v]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', f'{output_file_name}.mp4', '-t', str(total_length)])

            # Run FFmpeg command
            process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE)
            stderr = process.communicate()[1]

            if process.returncode == 0:
                st.success("Video created successfully!")
                with open(f'{output_file_name}.mp4', 'rb') as file:
                    st.download_button(label='Download Video', data=file, file_name=f'{output_file_name}.mp4', mime='video/mp4')
                st.video(f'{output_file_name}.mp4')
            else:
                st.error(f"Error in video creation: {stderr.decode()}")

if __name__ == "__main__":
    main()
