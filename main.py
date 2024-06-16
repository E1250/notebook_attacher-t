import json
import base64
import os
import argparse
import streamlit as st

def extract_and_update_images(notebook_path, output_dir, output_notebook_path):
    try:
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
        
        os.makedirs(output_dir, exist_ok=True)

        total_image_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            attachments = cell.get('attachments', {})
            new_source_lines = []

            for attachment_name, attachment_data in attachments.items():
                for image_format, image_base64 in attachment_data.items():
                    image_bytes = base64.b64decode(image_base64)
                    image_extension = image_format.split('/')[-1]
                    image_filename = f"cell_{cell_num}_image_{total_image_count}.{image_extension}"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                    
                    new_source_lines.append(f"![Image](./{image_path})\n")
                    
                    total_image_count += 1

            if total_image_count > 0:
                cell['attachments'] = {}
                cell['source'] = new_source_lines

        with open(output_notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)

        st.success(f"Extracted {total_image_count} images to {output_dir} and updated the notebook. Saved as {output_notebook_path}")

    except FileNotFoundError:
        st.error(f"File not found: {notebook_path}")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from the file: {notebook_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def update_images_back_to_attachments(notebook_path, output_notebook_path):
    try:
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
            
        total_image_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            new_attachments = {}
            new_source_lines = []

            for line in cell.get('source', []):
                if line.startswith('![Image]'):
                    full_image_path = line.split('(')[1].split(')')[0].strip('./')
                    
                    with open(full_image_path, 'rb') as img_file:
                        image_bytes = img_file.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    image_extension = full_image_path.split('.')[-1]
                    mime_type = f"image/{image_extension}"

                    attachment_name = f"image_{total_image_count}"
                    new_attachments[attachment_name] = {mime_type: image_base64}

                    new_source_lines.append(f"![Image](attachment:{attachment_name})\n")

                    total_image_count += 1
                else:
                    new_source_lines.append(line)
            
            if new_attachments:
                cell['attachments'] = new_attachments
                cell['source'] = new_source_lines

        with open(output_notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)

        st.success(f"Updated {total_image_count} images back to attachments and saved the notebook as {output_notebook_path}")

    except FileNotFoundError:
        st.error(f"File not found: {notebook_path}")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from the file: {notebook_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract and update images in Jupyter Notebook or revert images back to attachments.')
    subparsers = parser.add_subparsers(dest='command')

    extract_parser = subparsers.add_parser('extract', help='Extract images and update notebook')
    extract_parser.add_argument('notebook_path', help='Path to the Jupyter Notebook file.')
    extract_parser.add_argument('output_dir', help='Directory to save extracted images.')
    extract_parser.add_argument('output_notebook_path', help='Path to save the updated notebook file.')

    revert_parser = subparsers.add_parser('revert', help='Update images back to attachments')
    revert_parser.add_argument('notebook_path', help='Path to the updated Jupyter Notebook file.')
    revert_parser.add_argument('output_notebook_path', help='Path to save the restored notebook file.')

    args = parser.parse_args()

    if args.command == 'extract':
        extract_and_update_images(args.notebook_path, args.output_dir, args.output_notebook_path)
    elif args.command == 'revert':
        update_images_back_to_attachments(args.notebook_path, args.output_notebook_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

    # Streamlit UI
    st.title('Jupyter Notebook Image Tool')

    command = st.sidebar.selectbox('Select Command', ['extract', 'revert'])

    if command == 'extract':
        notebook_path = st.text_input('Enter Notebook Path:')
        output_dir = st.text_input('Enter Output Directory Path:')
        output_notebook_path = st.text_input('Enter Output Notebook Path:')
        
        if st.button('Extract Images and Update Notebook'):
            extract_and_update_images(notebook_path, output_dir, output_notebook_path)

    elif command == 'revert':
        notebook_path = st.text_input('Enter Updated Notebook Path:')
        output_notebook_path = st.text_input('Enter Output Notebook Path:')
        
        if st.button('Update Images Back to Attachments'):
            update_images_back_to_attachments(notebook_path, output_notebook_path)
