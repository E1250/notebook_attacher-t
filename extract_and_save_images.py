import json
import base64
import os
import argparse

def extract_and_update_images(notebook_path, output_dir, output_notebook_path):
    try:
        # Step 1: Read the notebook JSON content
        with open(notebook_path, 'r') as f:
            notebook_content = json.load(f)
        
        # Step 2: Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Step 3: Iterate through the notebook cells and extract images
        total_image_count = 0
        for cell_num, cell in enumerate(notebook_content.get('cells', [])):
            attachments = cell.get('attachments', {})
            cell_image_count = 0
            new_source_lines = []

            for attachment_name, attachment_data in attachments.items():
                for image_format, image_base64 in attachment_data.items():
                    image_bytes = base64.b64decode(image_base64)
                    image_extension = image_format.split('/')[-1]
                    image_filename = f"cell_{cell_num}_image_{cell_image_count}.{image_extension}"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    # Save the image to the specified path
                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                    
                    # Add the image path to the cell's source
                    new_source_lines.append(f"![Image](./{image_path})\n")
                    
                    cell_image_count += 1
                    total_image_count += 1

            # Update the cell: clear attachments and update the source
            if cell_image_count > 0:
                cell['attachments'] = {}
                cell['source'] = new_source_lines


        # Step 4: Save the updated notebook content back to the file
        with open(output_notebook_path, 'w') as f:
            json.dump(notebook_content, f, indent=4)

        print(f"Extracted {total_image_count} images to {output_dir} and updated the notebook. Saved as {output_notebook_path}")

    except FileNotFoundError:
        print(f"File not found: {notebook_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {notebook_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract images from a Jupyter notebook and save them to a directory")
    parser.add_argument("notebook_path", type=str, help="Path to the Jupyter notebook file")
    parser.add_argument("output_dir", type=str, help="Directory to save the extracted images", default="extracted_images")
    parser.add_argument("output_notebook_path", type=str, help="Path to save the updated notebook with image paths", default="updated_notebook.ipynb")
    args = parser.parse_args()

    extract_and_update_images(args.notebook_path, args.output_dir, args.output_notebook_path)

if __name__ == "__main__":
    main()
        

