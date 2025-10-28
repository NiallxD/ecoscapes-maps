import os
import json
import shutil

def generate_pages():
    # Create the base directory if it doesn't exist
    os.makedirs('pages', exist_ok=True)
    
    # Read the map configuration
    with open('map_config.json', 'r') as f:
        config_data = json.load(f)
    
    # Copy the config file to the pages directory
    shutil.copy2('map_config.json', 'pages/map_config.json')
    
    # Read the template
    with open('templates/mapviewer/map.html', 'r') as f:
        template = f.read()
    
    # Generate the main page
    with open('pages/index.html', 'w') as f:
        f.write(template)
    print("Generated main page")
    
    # Generate a page for each indicator
    if 'indicators' in config_data:
        for indicator_id, indicator in config_data['indicators'].items():
            # Create the page directory
            page_dir = os.path.join('pages', indicator_id)
            os.makedirs(page_dir, exist_ok=True)
            
            # Write the page
            with open(os.path.join(page_dir, 'index.html'), 'w') as f:
                f.write(template)
            
            print(f"Generated page for indicator: {indicator_id}")

if __name__ == '__main__':
    generate_pages()
