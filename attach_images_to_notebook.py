import json
import base64
import argparse
import streamlit as st
import os
import re

def attach_images_back_to_notebook(notebook_path, outputs_dir='outputs'):
    # try:
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)

        os.makedirs(outputs_dir, exist_ok=True)
        
        total_image_count = 0
        cell_img_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            new_attachments = {}
            new_source_lines = []

            for line in cell.get('source', []):
                if line.startswith('![Image'):
                    full_image_path = line.split('(')[1].split(')')[0].strip('./')
                    
                    with open(os.path.join('uploads', full_image_path), 'rb') as img_file:
                        image_bytes = img_file.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    image_extension = full_image_path.split('.')[-1]
                    mime_type = f"image/{image_extension}"

                    attachment_name = f"image-{cell_img_count}"
                    new_attachments[attachment_name] = {mime_type: image_base64}

                    new_source_lines.append(f"![Image](attachment:{attachment_name})\n")

                    total_image_count += 1
                    cell_img_count += 1
                else:
                    new_source_lines.append(line)
            
            if new_attachments:
                cell['attachments'] = new_attachments
                cell['source'] = new_source_lines
            
            cell_img_count = 0
                
        output_notebook_name = re.split(r'[\\/]', notebook_path)[-1]
        output_notebook_path = os.path.join(outputs_dir, output_notebook_name)
        with open(output_notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)

        st.success(f"Updated {total_image_count} images back to attachments and saved the notebook as {output_notebook_name}")

        # Provide the notebook as a downloadable file
        with open(output_notebook_path, 'rb') as f:
            st.download_button(
                label="Download updated notebook",
                data=f,
                file_name=output_notebook_name,
                mime="application/json"
            )
    
    # except FileNotFoundError:
    #     st.error(f"File not found: {notebook_path}")
    # except json.JSONDecodeError:
    #     st.error(f"Error decoding JSON from the file: {notebook_path}")
    # except Exception as e:
    #     st.error(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Update images back to attachments in a Jupyter notebook")
    parser.add_argument("notebook_path", type=str, help="Path to the Jupyter notebook file")
    parser.add_argument("--outputs_dir", type=str, help="Directory to save the output files", default="outputs")
    args = parser.parse_args()
    
    attach_images_back_to_notebook(args.notebook_path, args.outputs_dir)

if __name__ == '__main__':
    main()