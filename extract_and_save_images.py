import json
import base64
import os
import argparse
import streamlit as st
from zipfile import ZipFile
from utils import platform_path, platform_relpath

def extract_and_save_images(notebook_path, output_dir, is_linux=False):
    try:
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
        
        main_output_dir = 'outputs'
        os.makedirs(main_output_dir, exist_ok=True)
        os.makedirs(platform_path(is_linux, main_output_dir, output_dir), exist_ok=True)

        total_image_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            attachments = cell.get('attachments', {})
            sources = cell.get('source', [])
            new_source_lines = {}

            # Extract every attachment
            for attachment_name, attachment_data in attachments.items():
                for image_format, image_base64 in attachment_data.items():
                    image_bytes = base64.b64decode(image_base64)
                    image_extension = image_format.split('/')[-1]
                    image_filename = f"cell_{cell_num}_image_{total_image_count}.{image_extension}"
                    image_path = platform_path(is_linux, main_output_dir, output_dir, image_filename)
                    
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                        
                    new_source_lines[attachment_name] = f"![Image]({platform_path(is_linux, output_dir, image_filename)})\n"
                    
                    total_image_count += 1
            
            # Modify the source lines  
            for line_num, source_line in enumerate(sources):
                if "](attachment:" in source_line:
                    # Cut the image name from the source line
                    image_name = source_line.split("](attachment:")[1].split(")")[0]
                    cell['source'][line_num] = new_source_lines[image_name]
            
            if total_image_count > 0:
                cell['attachments'] = {}

        output_notebook_full_path = platform_path(is_linux, main_output_dir, notebook_path.split('\\')[-1])
        with open(output_notebook_full_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)
        
        # Create a zip file with the images folder
        zip_file_path = platform_path(is_linux ,main_output_dir, f'{main_output_dir}.zip')
        with ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(output_notebook_full_path, platform_relpath(is_linux, output_notebook_full_path, main_output_dir))
            
            for root, _, files in os.walk(platform_path(is_linux, main_output_dir, output_dir)):
                for file in files:
                    file_path = platform_path(is_linux, root, file)
                    zipf.write(file_path, platform_relpath(is_linux, file_path, main_output_dir))

        st.success(f"Extracted {total_image_count} images to {output_dir} and updated the notebook. Saved as {output_notebook_full_path}")
        
        with open(zip_file_path, "rb") as f:
            st.download_button(
                label="Download Output Zip File",
                data=f,
                file_name=f"{main_output_dir}.zip",
                mime="application/zip"
            )
        
    except FileNotFoundError:
        st.error(f"File not found: {notebook_path}")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from the file: {notebook_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
     
        
        
def main():
    parser = argparse.ArgumentParser(description="Extract images from a Jupyter notebook and save them to a directory")
    parser.add_argument("notebook_path", type=str, help="Path to the Jupyter notebook file")
    parser.add_argument("output_dir", type=str, help="Directory to save the extracted images", default="extracted_images")
    parser.add_argument("is_linux", action="store_true", help="Flag to indicate if the platform is Linux")
    args = parser.parse_args()

    extract_and_save_images(args.notebook_path, args.output_dir)

if __name__ == "__main__":
    main()