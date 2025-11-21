#!/usr/bin/env python3
"""
SVG to Circular Icons Converter

This script takes SVG files and converts them into circular icons with the original
SVG centered inside a colored circle. The original SVG will be made white.
"""
import os
import glob
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_circular_icon(svg_path, output_dir, circle_color='#4CAF50', size=100):
    """
    Convert an SVG to a circular icon with the original SVG in white.
    
    Args:
        svg_path (str): Path to the input SVG file
        output_dir (str): Directory to save the output SVG
        circle_color (str): Color of the circular background (hex code)
        size (int): Width and height of the output icon in pixels
    """
    # Parse the input SVG
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {svg_path}: {e}")
        return
    
    # Get the original dimensions or use the specified size
    def get_dimension(dim, default):
        if dim is None:
            return default
        # Extract numeric value from strings like '150pt' or '150'
        import re
        num = re.search(r'([0-9.]+)', str(dim))
        return float(num.group(1)) if num else default
    
    width = get_dimension(root.get('width'), size)
    height = get_dimension(root.get('height'), size)
    view_box = root.get('viewBox', f"0 0 {width} {height}")
    
    # Create a new SVG root
    new_root = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': str(size),
        'height': str(size),
        'viewBox': f'0 0 {size} {size}',
        'version': '1.1'
    })
    
    # Add a circular background
    circle = ET.SubElement(new_root, 'circle', {
        'cx': str(size // 2),
        'cy': str(size // 2),
        'r': str(size // 2),
        'fill': circle_color
    })
    
    # Calculate scale to fit the icon nicely in the circle
    scale = size * 0.7 / max(width, height) if max(width, height) > 0 else 1
    translate = (size - (max(width, height) * scale)) / 2
    
    # Create a group for the original icon with white fill
    group = ET.SubElement(new_root, 'g', {
        'fill': '#FFFFFF',
        'transform': f'translate({translate}, {translate}) scale({scale})',
        'fill-rule': 'evenodd'
    })
    
    # Add all elements from the original SVG to the group
    for elem in root:
        # Create a deep copy of each element
        new_elem = ET.fromstring(ET.tostring(elem, encoding='unicode'))
        # Remove any existing fill attributes to ensure white color
        if 'fill' in new_elem.attrib:
            del new_elem.attrib['fill']
        group.append(new_elem)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the new SVG
    output_path = os.path.join(output_dir, os.path.basename(svg_path))
    # Pretty print the XML
    rough_string = ET.tostring(new_root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    with open(output_path, 'w') as f:
        f.write(pretty_xml)
    
    print(f"Created: {output_path}")

def process_directory(input_dir, output_dir, file_pattern='*.svg'):
    """
    Process all SVG files in a directory.
    
    Args:
        input_dir (str): Directory containing input SVG files
        output_dir (str): Directory to save output SVG files
        file_pattern (str): Pattern to match SVG files (default: '*.svg')
    """
    svg_files = glob.glob(os.path.join(input_dir, file_pattern))
    
    if not svg_files:
        print(f"No SVG files found in {input_dir} with pattern {file_pattern}")
        return
    
    print(f"Found {len(svg_files)} SVG files to process...")
    
    for svg_file in svg_files:
        create_circular_icon(svg_file, output_dir)

if __name__ == "__main__":
    # Example usage
    input_directory = 'assets/icons'  # Directory containing original SVGs
    output_directory = 'assets/icons/circular'  # Directory to save circular icons
    
    process_directory(input_directory, output_directory)
    print("\nAll icons have been converted to circular format!")
