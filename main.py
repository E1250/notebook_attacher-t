import argparse
import streamlit as st
from zipfile import ZipFile
from attach_images_to_notebook import attach_images_back_to_notebook
from extract_and_save_images import extract_and_save_images
import shutil
import os

def main():
    parser = argparse.ArgumentParser(description='Extract and update images in Jupyter Notebook or revert images back to attachments.')
    subparsers = parser.add_subparsers(dest='command')

    extract_parser = subparsers.add_parser('extract', help='Extract images and update notebook')
    extract_parser.add_argument('notebook_path', help='Path to the Jupyter Notebook file.')
    extract_parser.add_argument('output_dir', help='Directory to save extracted images.')
    extract_parser.add_argument('is_unix', action='store_true', help='Flag to indicate if the platform is Linux.')

    revert_parser = subparsers.add_parser('revert', help='Update images back to attachments')
    revert_parser.add_argument('notebook_path', help='Path to the updated Jupyter Notebook file.')

    args = parser.parse_args()

    if args.command == 'extract':
        extract_and_save_images(args.notebook_path, args.output_dir, args.is_linux)
    elif args.command == 'revert':
        attach_images_back_to_notebook(args.notebook_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
    
    main_upload_folder = 'uploads'
    os.makedirs(main_upload_folder, exist_ok=True)

    # Streamlit UI
    st.title('Jupyter Notebook Image Tool')

    command = st.sidebar.selectbox('Select Command', ['extract', 'revert'])

    if command == 'extract':
        st.text('Extract images attached in a Jupyter Notebook and update the notebook with image paths.')
        notebook = st.file_uploader('Upload Jupyter Notebook', type=['ipynb'])
        output_dir = st.text_input('Enter Images Directory Name:', value='notebook_images')
        is_linux = st.checkbox('Is Linux?', help='Check this if you are running on a Linux platform to use the correct path separator.')
        
        # Show text
        st.text('For faster unzip, run the following code in a cell in the Jupyter Notebook:')            
        st.code(f'''
            import os
            import zipfile
            with zipfile.ZipFile('{output_dir}.zip', 'r') as zip_ref:
                zip_ref.extractall()
            os.remove('{output_dir}.zip')
            ''')
        
        if st.button('Extract Images and Update Notebook'):
            if notebook is not None:
                notebook_path = os.path.join(main_upload_folder, notebook.name)
                with open(notebook_path, 'wb') as f:
                    f.write(notebook.getvalue())
                if os.path.exists('outputs'): shutil.rmtree('outputs')
                extract_and_save_images(notebook_path, output_dir, is_linux=is_linux)

    elif command == 'revert':
        st.text('Attach images back to a Jupyter Notebook from a folder of images.')
        notebook = st.file_uploader('Upload Notebook', type=['ipynb'])
        images_folder = st.file_uploader('Upload Images Folder as Zip', type=['zip'])
        
        if st.button('Attach Images Back to Notebook'):
            if notebook is not None and images_folder is not None:
                notebook_path = os.path.join(main_upload_folder, notebook.name)
                # Extracting notebook
                with open(notebook_path, 'wb') as f:
                    f.write(notebook.getvalue())
                # Extracting images
                with ZipFile(images_folder) as z:
                    z.extractall(path='uploads')
                if os.path.exists('outputs'): shutil.rmtree('outputs')
                attach_images_back_to_notebook(notebook_path)
                
    # Removing uploads folder
    shutil.rmtree('uploads')