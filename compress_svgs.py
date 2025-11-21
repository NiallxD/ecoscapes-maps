#!/usr/bin/env python3
import os
import sys
import glob
from svgpathtools import svg2paths, wsvg
import shutil

def compress_svg(input_path, output_path):
    """Compress an SVG file and save it to the output path."""
    try:
        # Read the original file to get its size
        original_size = os.path.getsize(input_path)
        
        # Parse the SVG file
        paths, attributes = svg2paths(input_path)
        
        # If no paths found, copy the file as is
        if not paths:
            shutil.copy2(input_path, output_path)
            return original_size, os.path.getsize(output_path)
        
        # Create a new SVG with just the paths
        wsvg(paths=paths, filename=output_path, attributes=attributes, 
             svg_attributes={'viewBox': '0 0 1024 1024'})  # Default viewBox, adjust as needed
        
        compressed_size = os.path.getsize(output_path)
        return original_size, compressed_size
        
    except Exception as e:
        print(f"Error processing {os.path.basename(input_path)}: {str(e)}")
        return None, None

def process_directory(input_dir, output_dir):
    """Process all SVG files in the input directory and save to output directory."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all SVG files in the input directory
    svg_files = glob.glob(os.path.join(input_dir, '*.svg'))
    
    if not svg_files:
        print(f"No SVG files found in {input_dir}")
        return
    
    print(f"Found {len(svg_files)} SVG files to process...\n")
    
    total_original = 0
    total_compressed = 0
    processed_count = 0
    
    for svg_file in svg_files:
        filename = os.path.basename(svg_file)
        output_path = os.path.join(output_dir, filename)
        
        print(f"Processing {filename}...")
        original_size, compressed_size = compress_svg(svg_file, output_path)
        
        if original_size and compressed_size:
            saved = ((original_size - compressed_size) / original_size) * 100
            print(f"  Original: {original_size/1024:.2f}KB  "
                  f"Compressed: {compressed_size/1024:.2f}KB  "
                  f"Saved: {saved:.2f}%")
            
            total_original += original_size
            total_compressed += compressed_size
            processed_count += 1
    
    # Print summary
    if processed_count > 0:
        print("\n--- Compression Summary ---")
        print(f"Processed: {processed_count} files")
        print(f"Original size: {total_original/1024:.2f}KB")
        print(f"Compressed size: {total_compressed/1024:.2f}KB")
        print(f"Total saved: {((total_original - total_compressed) / total_original * 100):.2f}%")
        print(f"\nCompressed SVGs saved to: {os.path.abspath(output_dir)}")
    else:
        print("No files were processed successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress_svgs.py <input_directory> [output_directory]")
        print("If output_directory is not provided, files will be saved to 'compressed' folder")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'compressed'
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)
    
    process_directory(input_dir, output_dir)
