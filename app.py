import streamlit as st
import os
import re
import shutil
from pathlib import Path

# =====================================================
# STREAMLIT UI CONFIGURATION
# =====================================================
st.set_page_config(page_title="Chapter Renamer & Sequencer", page_icon="📁", layout="centered")

st.title("📁 Chapter File Renamer & Sequencer")
st.write("Upload your chapter `.txt` files. The app will naturally sort them, renumber the chapters sequentially starting from 1 while preserving the rest of the filename, and let you download the results as a ZIP archive.")

# =====================================================
# FILE UPLOADERS
# =====================================================
st.subheader("Upload Chapter Text Files")
uploaded_files = st.file_uploader("Upload `.txt` chapter files", type=["txt"], accept_multiple_files=True)

# =====================================================
# PROCESSING LOGIC
# =====================================================
def natural_sort_key(path):
    filename = path.stem
    numbers = [int(num) for num in re.findall(r"\d+", filename)]
    return numbers

def process_renaming(files):
    input_dir = Path("temp_input")
    output_dir = Path("temp_output")
    
    # Clean/create directories
    if input_dir.exists():
        shutil.rmtree(input_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
        
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Save uploaded files locally
    for file in files:
        with open(input_dir / file.name, "wb") as f:
            f.write(file.getbuffer())
            
    # Find all .txt files and sort them naturally
    txt_files = sorted(input_dir.glob("*.txt"), key=natural_sort_key)
    
    counter = 1
    processed_count = 0
    skipped_files = []
    
    for file_path in txt_files:
        filename = file_path.stem
        match = re.match(r"^Глава\s+\d+\.\s*(.+)", filename)
        
        if match:
            rest_of_name = match.group(1)
            new_filename = f"Глава {counter}. {rest_of_name}.txt"
            
            src_path = file_path
            dst_path = output_dir / new_filename
            
            shutil.copy2(src_path, dst_path)
            counter += 1
            processed_count += 1
        else:
            skipped_files.append(filename + ".txt")
            
    # Create ZIP archive of results
    shutil.make_archive("renamed_chapters_archive", "zip", output_dir)
    return "renamed_chapters_archive.zip", processed_count, skipped_files

# =====================================================
# MAIN ACTION BUTTON
# =====================================================
if st.button("Rename and Process Files"):
    if not uploaded_files:
        st.error("Please upload at least one `.txt` file.")
    else:
        with st.spinner("Processing and renaming files..."):
            try:
                zip_path, count, skipped = process_renaming(uploaded_files)
                st.success(f"Successfully processed and renamed {count} files!")
                
                if skipped:
                    st.warning(f"Skipped {len(skipped)} files due to pattern mismatch (expected format: 'Глава X. ...'):")
                    for s in skipped:
                        st.write(f"- {s}")
                
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label="📦 Download Renamed Files (ZIP)",
                        data=fp,
                        file_name="renamed_chapters.zip",
                        mime="application/zip"
                    )
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")