import os
import re
import svgwrite
from lxml import etree
import xml.etree.ElementTree as ET
from svg.path import parse_path, Path, Line, CubicBezier, QuadraticBezier, Arc
from svg.path.path import Move, Close
import numpy as np
import math
from io import StringIO
import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Processing timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# ==========================
# Parameters
# ==========================
INPUT_DIR = "/Users/niallbell/Programming/Django/EcoScapes-Map-App-v2/assets/icons"       # Folder containing your source SVG icons
OUTPUT_DIR = "/Users/niallbell/Programming/Django/EcoScapes-Map-App-v2/assets/square-icons"     # Folder to save the new icons
SQUARE_SIZE = 512              # Size of the square (width and height)
SQUARE_RADIUS = 64             # Corner radius of the square
PADDING = 64                   # Padding inside the square for the icon
# ==========================


def normalize_path_data(d):
    """Normalize path data to fix common issues."""
    if not d:
        return ""
    
    # Remove newlines and extra spaces
    d = ' '.join(d.split())
    
    # Ensure proper spacing between commands
    d = re.sub(r'([a-zA-Z])(?=[^\s,])', r'\1 ', d)
    d = re.sub(r'(?<=[0-9])(?=[-+])', ' ', d)
    d = re.sub(r'(?<=[0-9])(?=[A-Za-z])', ' ', d)
    d = re.sub(r'(?<=[A-Za-z])(?=[0-9-+])', ' ', d)  # Removed extra ', d'
    
    # Remove duplicate spaces and commas
    d = re.sub(r'\s+', ' ', d).strip()
    d = re.sub(r',+', ',', d)
    d = re.sub(r'\s*,\s*', ',', d)
    
    return d

def get_path_bounds(d):
    """Calculate the bounding box of a path."""
    try:
        # First try with svg.path for accurate bounds
        try:
            path = parse_path(d)
            if not path:
                return None
                
            # Get all points from the path
            points = []
            for segment in path:
                if hasattr(segment, 'point'):
                    points.append((segment.point(0).real, segment.point(0).imag))
                    points.append((segment.point(1).real, segment.point(1).imag))
                if hasattr(segment, 'control1'):
                    points.append((segment.control1.real, segment.control1.imag))
                if hasattr(segment, 'control2'):
                    points.append((segment.control2.real, segment.control2.imag))
                if hasattr(segment, 'end'):
                    points.append((segment.end.real, segment.end.imag))
                    
            if points:
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                return {
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                }
        except:
            pass
            
        # Fallback: Parse numbers and find min/max
        try:
            # Extract all numbers from the path data
            import re
            numbers = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d)]
            
            if len(numbers) >= 4:  # Need at least 2 points (x1,y1,x2,y2)
                x_coords = numbers[::2]  # All even indices
                y_coords = numbers[1::2]  # All odd indices
                
                return {
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                }
        except:
            pass
            
        return None
    except Exception as e:
        print(f"  Warning: Could not calculate bounds: {str(e)}")
        return None

def clean_path_data(d):
    """Clean and normalize path data."""
    if not d:
        return ""
    
    # Remove newlines and extra spaces
    d = ' '.join(d.split())
    
    # Ensure proper spacing between commands
    d = re.sub(r'([a-zA-Z])(?=[^\s,])', r'\1 ', d)  # Add space after command letters
    d = re.sub(r'(?<=[0-9])(?=[-+])', ' ', d)  # Add space before - or + after numbers
    d = re.sub(r'(?<=[0-9])(?=[A-Za-z])', ' ', d)  # Add space between number and letter
    d = re.sub(r'(?<=[A-Za-z])(?=[0-9-+])', ' ', d)  # Add space between letter and number
    
    # Remove duplicate spaces and commas
    d = re.sub(r'\s+', ' ', d).strip()
    d = re.sub(r',+', ',', d)
    d = re.sub(r'\s*,\s*', ',', d)
    
    # Ensure path starts with a command
    if d and d[0] not in 'MmLlHhVvCcSsQqTtAaZz':
        d = 'M ' + d
    
    return d

def normalize_svg(svg_content):
    """Normalize SVG to be square based on path extents with proper centering."""
    try:
        # Parse SVG
        parser = etree.XMLParser(recover=True, remove_blank_text=True)
        root = etree.fromstring(svg_content.encode('utf-8'), parser=parser)
        
        # Find all paths and other graphical elements
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        elements = []
        
        # Look for all possible SVG elements that might contain visual content
        for element_type in ['path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'g']:
            elements.extend(root.findall(f'.//svg:{element_type}', namespaces) or 
                          root.findall(f'.//{{http://www.w3.org/2000/svg}}{element_type}'))
        
        if not elements:
            return svg_content  # Return original if no graphical elements found
            
        # Clean path data for path elements
        for element in elements:
            if element.tag.endswith('path'):
                d = element.get('d', '')
                if d:
                    element.set('d', clean_path_data(d))
        
        # Calculate combined bounds of all elements
        bounds = None
        for element in elements:
            if element.tag.endswith('path'):
                d = element.get('d', '')
                if not d:
                    continue
                element_bounds = get_path_bounds(d)
            # Add support for other element types if needed
            # elif element.tag.endswith('rect'):
            #     element_bounds = {
            #         'x': float(element.get('x', 0)),
            #         'y': float(element.get('y', 0)),
            #         'width': float(element.get('width', 0)),
            #         'height': float(element.get('height', 0))
            #     }
            else:
                continue
                
            if element_bounds and element_bounds.get('width', 0) > 0 and element_bounds.get('height', 0) > 0:
                if bounds is None:
                    bounds = element_bounds.copy()
                else:
                    # Expand bounds to include this element
                    right = max(bounds['x'] + bounds['width'], 
                              element_bounds['x'] + element_bounds['width'])
                    bottom = max(bounds['y'] + bounds['height'],
                               element_bounds['y'] + element_bounds['height'])
                    bounds['x'] = min(bounds['x'], element_bounds['x'])
                    bounds['y'] = min(bounds['y'], element_bounds['y'])
                    bounds['width'] = right - bounds['x']
                    bounds['height'] = bottom - bounds['y']
        
        if not bounds or bounds.get('width', 0) == 0 or bounds.get('height', 0) == 0:
            # If we couldn't calculate bounds, use a default size
            bounds = {'x': 0, 'y': 0, 'width': 100, 'height': 100}
        
        # Calculate the center of the content
        center_x = bounds['x'] + bounds['width'] / 2
        center_y = bounds['y'] + bounds['height'] / 2
        
        # Calculate the size of the square that will contain the content
        size = max(bounds['width'], bounds['height']) * 1.2  # 20% padding
        
        # Calculate the new viewBox to center the content
        viewbox_x = center_x - size / 2
        viewbox_y = center_y - size / 2
        
        # Create new SVG with square viewBox
        new_svg = etree.Element('svg', 
                              xmlns="http://www.w3.org/2000/svg",
                              viewBox=f"{viewbox_x} {viewbox_y} {size} {size}",
                              width=str(size),
                              height=str(size))
        
        # Add a group to contain the original content
        g = etree.SubElement(new_svg, 'g')
        
        # Add all elements to the group
        for element in elements:
            # Create a copy of the element with all attributes
            new_element = etree.SubElement(g, element.tag)
            for attr, value in element.attrib.items():
                if attr != 'transform':  # We'll handle transform separately
                    new_element.set(attr, value)
        
        return etree.tostring(new_svg, encoding='unicode', pretty_print=True)
        
    except Exception as e:
        print(f"Error normalizing SVG: {str(e)}")
        return svg_content

def get_viewbox(root):
    """Extract viewBox or calculate from width/height."""
    vb = root.get('viewBox')
    if vb:
        try:
            parts = list(map(float, vb.split()))
            if len(parts) == 4:
                return parts[2] - parts[0], parts[3] - parts[1]
        except (ValueError, AttributeError):
            pass
    
    try:
        w = float(root.get('width', SQUARE_SIZE))
        h = float(root.get('height', SQUARE_SIZE))
        return w, h
    except (ValueError, TypeError):
        return SQUARE_SIZE, SQUARE_SIZE

def process_svg(input_file, output_file, timeout_seconds=5):
    try:
        print(f"\nProcessing: {os.path.basename(input_file)}")
        
        def _process():
            # Read the SVG content
            with open(input_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # First, get the bounds of the SVG content
            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            root = etree.fromstring(svg_content.encode('utf-8'), parser=parser)
            
            # Find all paths and calculate bounds
            namespaces = {'svg': 'http://www.w3.org/2000/svg'}
            paths = root.findall('.//svg:path', namespaces) or root.findall('.//{http://www.w3.org/2000/svg}path')
            
            # Calculate the bounds of all paths
            bounds = None
            for path in paths:
                d = path.get('d', '').strip()
                if d:
                    path_bounds = get_path_bounds(d)
                    if path_bounds:
                        if bounds is None:
                            bounds = path_bounds.copy()
                        else:
                            right = max(bounds['x'] + bounds['width'], 
                                      path_bounds['x'] + path_bounds['width'])
                            bottom = max(bounds['y'] + bounds['height'],
                                       path_bounds['y'] + path_bounds['height'])
                            bounds['x'] = min(bounds['x'], path_bounds['x'])
                            bounds['y'] = min(bounds['y'], path_bounds['y'])
                            bounds['width'] = right - bounds['x']
                            bounds['height'] = bottom - bounds['y']
            
            if not bounds:
                bounds = {'x': 0, 'y': 0, 'width': 100, 'height': 100}
            
            # Create a new SVG with just the cropped content
            cropped_svg = f'''
            <svg xmlns="http://www.w3.org/2000/svg" 
                 viewBox="{bounds['x']} {bounds['y']} {bounds['width']} {bounds['height']}"
                 width="{bounds['width']}" 
                 height="{bounds['height']}">
                {svg_content}
            </svg>
            '''
            
            # Now process the cropped SVG
            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            root = etree.fromstring(cropped_svg.encode('utf-8'), parser=parser)
            
            # Get dimensions from viewBox
            viewbox = root.get('viewBox', '0 0 100 100')
            _, _, w, h = map(float, viewbox.split())
            
            # Create new SVG
            dwg = svgwrite.Drawing(output_file, size=(SQUARE_SIZE, SQUARE_SIZE))
            
            # Define mask: square minus icon
            mask = dwg.mask(id="iconmask")
            
            # Add white square (visible area)
            mask.add(dwg.rect(
                insert=(0, 0),
                size=(SQUARE_SIZE, SQUARE_SIZE),
                rx=SQUARE_RADIUS,
                ry=SQUARE_RADIUS,
                fill="white"
            ))

            # Calculate scaling and translation
            # Scale to fit within padding, maintaining aspect ratio
            scale = min(
                (SQUARE_SIZE - 2 * PADDING) / max(w, 0.01),  # Avoid division by zero
                (SQUARE_SIZE - 2 * PADDING) / max(h, 0.01)
            )
            
            # Calculate center position
            tx = (SQUARE_SIZE - w * scale) / 2
            ty = (SQUARE_SIZE - h * scale) / 2
            transform = f"translate({tx},{ty}) scale({scale})"

            # Add paths to mask
            namespaces = {'svg': 'http://www.w3.org/2000/svg'}
            paths = root.findall('.//svg:path', namespaces) or root.findall('.//{http://www.w3.org/2000/svg}path')
            
            for path in paths:
                d = path.get('d', '').strip()
                if d:
                    try:
                        mask.add(dwg.path(
                            d=d,
                            fill="black",
                            transform=transform
                        ))
                    except Exception as e:
                        print(f"  Warning: Could not add path: {str(e)}")
                        continue

            # Add the mask to the drawing
            dwg.defs.add(mask)

            # Create the final square with the mask
            dwg.add(dwg.rect(
                insert=(0, 0),
                size=(SQUARE_SIZE, SQUARE_SIZE),
                rx=SQUARE_RADIUS,
                ry=SQUARE_RADIUS,
                fill="black",
                mask="url(#iconmask)"
            ))

            # Save the result
            dwg.save(pretty=True)
            return True
        
        # Run the entire processing with timeout
        with time_limit(timeout_seconds):
            result = _process()
            
        print(f"  ✓ Successfully processed")
        return True
        
    except TimeoutException as e:
        print(f"  ⏱️  Error: Processing timed out after {timeout_seconds} seconds")
        return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_svg_files(directory):
    """Get all SVG files in the directory and its subdirectories."""
    svg_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.svg'):
                svg_files.append(os.path.join(root, file))
    return svg_files

def main():
    print("=" * 70)
    print("SVG Formatter - Converting icons to square format")
    print("=" * 70)
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found: {INPUT_DIR}")
        return
    
    # Create output directory if it doesn't exist
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory: {str(e)}")
        return
    
    # Get all SVG files (including subdirectories)
    svg_files = get_svg_files(INPUT_DIR)
    
    if not svg_files:
        print(f"No SVG files found in {INPUT_DIR}")
        return
    
    print(f"\nFound {len(svg_files)} SVG files to process")
    print(f"Input directory: {os.path.abspath(INPUT_DIR)}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("-" * 70)
    
    success_count = 0
    failed_files = []
    
    # Process each file
    for i, input_file in enumerate(svg_files, 1):
        # Create relative path for output to maintain directory structure
        rel_path = os.path.relpath(input_file, INPUT_DIR)
        output_file = os.path.join(OUTPUT_DIR, rel_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"\n[{i}/{len(svg_files)}] Processing: {rel_path}")
        
        try:
            if process_svg(input_file, output_file):
                success_count += 1
                print(f"✓ Success")
            else:
                print(f"✗ Failed (see error above)")
                failed_files.append(rel_path)
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed_files.append(rel_path)
    
    # Print summary
    print("\n" + "=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(svg_files)}")
    print(f"Successfully processed: {success_count}")
    
    if failed_files:
        print(f"Failed to process: {len(failed_files)} files")
        print("\nFailed files:")
        for i, file in enumerate(failed_files, 1):
            print(f"  {i}. {file}")
    
    print(f"\nOutput directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 70)


if __name__ == "__main__":
    import time
    start_time = time.time()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        elapsed = time.time() - start_time
        print(f"\nTotal time: {elapsed:.2f} seconds")
