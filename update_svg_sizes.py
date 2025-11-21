import os
import re
from pathlib import Path

def update_svg_sizes(directory):
    # Get all SVG files in the directory
    svg_files = list(Path(directory).glob('*.svg'))
    
    if not svg_files:
        print(f"No SVG files found in {directory}")
        return
    
    updated_count = 0
    
    for svg_file in svg_files:
        try:
            # Read the SVG file
            with open(svg_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # First, normalize any malformed attributes
            content = re.sub(r'"\s*"(width|height)=', r' \1=', content)  # Fix "" before width/height
            content = re.sub(r'=\s*"\s*"', '=""', content)  # Fix empty quotes
            
            # Remove any existing width and height attributes completely
            content = re.sub(r'\s+width\s*=\s*["\'][^"\']*["\']', '', content)
            content = re.sub(r'\s+height\s*=\s*["\'][^"\']*["\']', '', content)
            
            # Add new width and height attributes with proper spacing
            new_content = re.sub(r'(<svg[^>]*)', r'\1 width="150pt" height="150pt"', content, count=1)
            
            # Write the changes back to the file
            with open(svg_file, 'w', encoding='utf-8') as file:
                file.write(new_content)
            updated_count += 1
            print(f"Updated: {svg_file.name}")
                
        except Exception as e:
            print(f"Error processing {svg_file.name}: {str(e)}")
    
    print(f"\nProcessing complete. Updated {updated_count} out of {len(svg_files)} SVG files.")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the assets/icons directory
    icons_dir = os.path.join(script_dir, 'assets', 'icons')
    
    if os.path.exists(icons_dir):
        update_svg_sizes(icons_dir)
    else:
        print(f"Icons directory not found at: {icons_dir}")
        print("Please make sure the script is in the project root directory.")
