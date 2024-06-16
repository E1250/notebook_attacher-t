import json
import base64
import argparse

def update_images_back_to_attachments(notebook_path, output_notebook_path):
    try:
        # Step 1: Read the notebook JSON content
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
            
        # Step 2: Iterate through the notebook cells and update images back to attachments
        total_image_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            new_attachments = {}
            new_source_lines = []

            for line in cell.get('source', []):
                if line.startswith('![Image]'):
                    # Extract the image path
                    full_image_path = line.split('(')[1].split(')')[0].strip('./')
                    
                    # Read the image and encode it in base64
                    with open(full_image_path, 'rb') as img_file:
                        image_bytes = img_file.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    # Determine the MIME type from the file extension
                    image_extension = full_image_path.split('.')[-1]
                    mime_type = f"image/{image_extension}"

                    # Update attachments
                    attachment_name = f"image_{total_image_count}"
                    new_attachments[attachment_name] = {mime_type: image_base64}

                    # Update the source line to reference the attachment
                    new_source_lines.append(f"![Image](attachment:{attachment_name})\n")

                    total_image_count += 1
                else:
                    new_source_lines.append(line)
            
            # Update the cell with new attachments and source
            if new_attachments:
                cell['attachments'] = new_attachments
                cell['source'] = new_source_lines

        # Step 3: Save the updated notebook content back to the file
        with open(output_notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)

        print(f"Updated {total_image_count} images back to attachments and saved the notebook as {output_notebook_path}")

    except FileNotFoundError:
        print(f"File not found: {notebook_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {notebook_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Update images back to attachments in a Jupyter notebook")
    parser.add_argument("notebook_path", type=str, help="Path to the Jupyter notebook file")
    parser.add_argument("output_notebook_path", type=str, help="Path to save the updated notebook file", default="attached_notebook.ipynb")
    args = parser.parse_args()
    
    update_images_back_to_attachments(args.notebook_path, args.output_notebook_path)

if __name__ == '__main__':
    main()