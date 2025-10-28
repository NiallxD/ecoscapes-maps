import os
import json
import shutil
from pathlib import Path

def load_config():
    with open('map_config.json', 'r') as f:
        return json.load(f)

def ensure_dir(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)

def copy_static_files():
    # Create static directory if it doesn't exist
    static_dir = 'static'
    ensure_dir(static_dir)
    
    # Copy any static files (CSS, JS, images) if needed
    # Example: shutil.copy2('path/to/your/css/style.css', os.path.join(static_dir, 'css/'))

def generate_pages():
    # Load the template
    with open('templates/mapviewer/map.html', 'r') as f:
        template = f.read()
    
    # Load the config
    config = load_config()
    
    # Create output directory
    output_dir = 'docs'
    ensure_dir(output_dir)
    
    # Create an index.html that redirects to the first indicator
    first_indicator = next(iter(config))
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0; url=./{first_indicator}/" />
            <title>Redirecting...</title>
        </head>
        <body>
            <p>Redirecting to <a href="./{first_indicator}/">./{first_indicator}/</a>...</p>
        </body>
        </html>
        ''')
    
    # Generate a page for each indicator
    for indicator_id, indicator_data in config.items():
        # Create indicator directory
        indicator_dir = os.path.join(output_dir, indicator_id)
        ensure_dir(indicator_dir)
        
        # Create a copy of the template for this indicator
        page = template
        page = page.replace('{{ page_name }}', indicator_id)
        page = page.replace('{{ map1_url }}', indicator_data.get('map1_url', ''))
        page = page.replace('{{ map2_url }}', indicator_data.get('map2_url', ''))
        
        # Add the indicators data to the page
        page = page.replace('{{ indicators|tojson }}', json.dumps(config))
        
        # Write the output file
        with open(os.path.join(indicator_dir, 'index.html'), 'w') as f:
            f.write(page)
    
{{ ... }}
    with open(os.path.join(output_dir, 'map_config.json'), 'w') as f:
        json.dump(config, f, indent=4)

def main():
    print("Building static files...")
    copy_static_files()
    generate_pages()
    print("Build complete! Files are in the 'docs' directory.")

if __name__ == "__main__":
    main()
