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
        
        # Replace template variables
        page = page.replace('{{ page_name }}', indicator_id)
        page = page.replace('{{ map1_url }}', indicator_data.get('map1_url', ''))
        page = page.replace('{{ map2_url }}', indicator_data.get('map2_url', ''))
        
        # Create the JavaScript with proper string formatting
        indicators_js = f"""
        <script>
            // Get the current indicator data from the URL
            const pathSegments = window.location.pathname.split('/').filter(Boolean);
            const currentIndicatorId = pathSegments.length > 0 ? pathSegments[pathSegments.length - 1] : '{indicator_id}';
            const indicators = {json.dumps(config, ensure_ascii=False)};
            
            // Update the page content
            document.addEventListener('DOMContentLoaded', function() {{
                const currentIndicator = indicators[currentIndicatorId] || {{}};
                
                // Update the title, description, and icon
                const titleElement = document.getElementById('indicator-title');
                const descElement = document.getElementById('indicator-description');
                const iconElement = document.getElementById('indicator-icon');
                
                if (titleElement) titleElement.textContent = currentIndicator.title || 'Indicator';
                if (descElement) descElement.textContent = currentIndicator.description || '';
                if (iconElement) iconElement.textContent = currentIndicator.icon || '🌍';
                
                // Update the dropdown button
                const dropdownButton = document.getElementById('indicatorDropdown');
                if (dropdownButton) {{
                    dropdownButton.textContent = currentIndicator.title || 'Select Indicator';
                }}
                
                // Populate the dropdown menu
                const menu = document.getElementById('indicatorMenu');
                if (menu) {{
                    menu.innerHTML = ''; // Clear existing items
                    Object.entries(indicators).forEach(([id, data]) => {{
                        const link = document.createElement('a');
                        link.href = './' + id + '/';
                        if (id === currentIndicatorId) {{
                            link.className = 'active';
                        }}
                        link.textContent = data.title || id;
                        menu.appendChild(link);
                    }});
                }}
                
                // Initialize the toggle buttons
                const exploreBtn = document.getElementById('exploreBtn');
                const analyzeBtn = document.getElementById('analyzeBtn');
                const map1 = document.getElementById('map1');
                const map2 = document.getElementById('map2');
                
                if (exploreBtn && analyzeBtn && map1 && map2) {{
                    exploreBtn.addEventListener('click', () => {{
                        exploreBtn.classList.add('active');
                        analyzeBtn.classList.remove('active');
                        map1.classList.add('active');
                        map2.classList.remove('active');
                    }});
                    
                    analyzeBtn.addEventListener('click', () => {{
                        analyzeBtn.classList.add('active');
                        exploreBtn.classList.remove('active');
                        map2.classList.add('active');
                        map1.classList.remove('active');
                    }});
                }}
            }});
        </script>
        """
        
        # Insert the JavaScript before the closing head tag
        page = page.replace('</head>', indicators_js + '\n</head>')
        
        # Write the output file
        with open(os.path.join(indicator_dir, 'index.html'), 'w') as f:
            f.write(page)
    
    # Copy the config to the docs directory
    with open(os.path.join(output_dir, 'map_config.json'), 'w') as f:
        json.dump(config, f, indent=4)

def main():
    print("Building static files...")
    copy_static_files()
    generate_pages()
    print("Build complete! Files are in the 'docs' directory.")

if __name__ == "__main__":
    main()
