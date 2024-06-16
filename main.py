import argparse
import streamlit as st
from zipfile import ZipFile
from attach_images_to_notebook import attach_images_back_to_notebook
from extract_and_save_images import extract_and_save_images

def main():
    parser = argparse.ArgumentParser(description='Extract and update images in Jupyter Notebook or revert images back to attachments.')
    subparsers = parser.add_subparsers(dest='command')

    extract_parser = subparsers.add_parser('extract', help='Extract images and update notebook')
    extract_parser.add_argument('notebook_path', help='Path to the Jupyter Notebook file.')
    extract_parser.add_argument('output_dir', help='Directory to save extracted images.')
    extract_parser.add_argument('output_notebook_path', help='Path to save the updated notebook file.')

    revert_parser = subparsers.add_parser('revert', help='Update images back to attachments')
    revert_parser.add_argument('notebook_path', help='Path to the updated Jupyter Notebook file.')
    revert_parser.add_argument('images_folder', help='Path to the folder containing images.')
    revert_parser.add_argument('output_notebook_path', help='Path to save the restored notebook file.')

    args = parser.parse_args()

    if args.command == 'extract':
        extract_and_save_images(args.notebook_path, args.output_dir, args.output_notebook_path)
    elif args.command == 'revert':
        attach_images_back_to_notebook(args.notebook_path, args.images_folder, args.output_notebook_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

    # Streamlit UI
    st.title('Jupyter Notebook Image Tool')

    command = st.sidebar.selectbox('Select Command', ['extract', 'revert'])

    if command == 'extract':
        notebook_path = st.file_uploader('Upload Jupyter Notebook', type=['ipynb'])
        output_dir = st.text_input('Enter Output Directory Path:')
        output_notebook_path = st.text_input('Enter Output Notebook Path:')
        
        if st.button('Extract Images and Update Notebook'):
            if notebook_path is not None:
                with open(notebook_path.name, 'wb') as f:
                    f.write(notebook_path.getvalue())
                extract_and_save_images(notebook_path.name, output_dir, output_notebook_path)

    elif command == 'revert':
        notebook_path = st.file_uploader('Upload Updated Notebook', type=['ipynb'])
        images_folder = st.file_uploader('Upload Images Folder as Zip', type=['zip'])
        output_notebook_path = st.text_input('Enter Output Notebook Path:')
        
        if st.button('Update Images Back to Attachments'):
            if notebook_path is not None and images_folder is not None:
                with open(notebook_path.name, 'wb') as f:
                    f.write(notebook_path.getvalue())
                with ZipFile(images_folder) as z:
                    z.extractall(path='images_folder_extracted')
                attach_images_back_to_notebook(notebook_path.name, 'images_folder_extracted', output_notebook_path)
