import os
import json
from pathlib import Path

def ensure_dir(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)

def load_config():
    with open('map_config.json', 'r') as f:
        return json.load(f)

def create_indicator_page(indicator_id, indicator_data, output_dir):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{indicator_data.get('title', 'Indicator')} - EcoScapes Map Viewer</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f8f9fa;
            padding: 10px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .toolbar h1 {{
            margin: 0;
            font-size: 1.2em;
            color: #2c3e50;
        }}
        .toggle-container {{
            display: flex;
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: hidden;
        }}
        .toggle-option {{
            padding: 8px 16px;
            cursor: pointer;
            background-color: white;
            transition: background-color 0.3s;
        }}
        .toggle-option.active {{
            background-color: #3498db;
            color: white;
        }}
        .toggle-option:not(.active):hover {{
            background-color: #f0f0f0;
        }}
        .map-container {{
            display: flex;
            height: calc(100vh - 60px);
        }}
        .map-iframe {{
            width: 100%;
            height: 100%;
            border: none;
            display: none;
        }}
        .map-iframe.active {{
            display: block;
        }}
        .back-link {{
            color: #3498db;
            text-decoration: none;
            margin-right: 20px;
        }}
        .content-area {{
            padding: 15px 20px;
        }}
        .indicator-icon {{
            font-size: 2em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="toolbar">
        <div>
            <a href="../" class="back-link">← Back to Indicators</a>
            <h1>{indicator_data.get('title', 'Indicator')}</h1>
        </div>
        <div class="toggle-container">
            <div id="exploreBtn" class="toggle-option active">Explore</div>
            <div id="analyzeBtn" class="toggle-option">Analyze</div>
        </div>
    </div>
    
    <div class="content-area">
        <p>{indicator_data.get('description', '')}</p>
        <div class="indicator-icon">{indicator_data.get('icon', '🌍')}</div>
    </div>
    
    <div class="map-container">
        <iframe id="map1" class="map-iframe active" 
            src="{indicator_data.get('map1_url', '')}">
        </iframe>
        <iframe id="map2" class="map-iframe" 
            src="{indicator_data.get('map2_url', '')}">
        </iframe>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const exploreBtn = document.getElementById('exploreBtn');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const map1 = document.getElementById('map1');
            const map2 = document.getElementById('map2');
            
            exploreBtn.addEventListener('click', function() {{
                exploreBtn.classList.add('active');
                analyzeBtn.classList.remove('active');
                map1.classList.add('active');
                map2.classList.remove('active');
            }});
            
            analyzeBtn.addEventListener('click', function() {{
                analyzeBtn.classList.add('active');
                exploreBtn.classList.remove('active');
                map2.classList.add('active');
                map1.classList.remove('active');
            }});
        }});
    </script>
</body>
</html>"""
    
    output_file = os.path.join(output_dir, indicator_id, 'index.html')
    with open(output_file, 'w') as f:
        f.write(page)

def create_index_page(config, output_dir):
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoScapes Map Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
        }
        .indicator-list {
            list-style: none;
            padding: 0;
        }
        .indicator-item {
            margin-bottom: 15px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        .indicator-item a {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #3498db;
            font-weight: bold;
            font-size: 1.2em;
        }
        .indicator-icon {
            font-size: 1.5em;
            margin-right: 10px;
        }
        .indicator-item p {
            margin: 5px 0 0 30px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <h1>EcoScapes Map Viewer</h1>
    <p>Select an indicator to view:</p>
    <ul class="indicator-list">
"""

    for indicator_id, indicator_data in config.items():
        index_html += f"""
        <li class="indicator-item">
            <a href="{indicator_id}/">
                <span class="indicator-icon">{indicator_data.get('icon', '🌍')}</span>
                {indicator_data.get('title', indicator_id).replace('-', ' ').title()}
            </a>
            <p>{indicator_data.get('description', '')}</p>
        </li>
        """

    index_html += """
    </ul>
</body>
</html>
"""

    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(index_html)

def main():
    # Load the configuration
    config = load_config()
    
    # Set up output directory
    output_dir = 'docs'
    ensure_dir(output_dir)
    
    # Create the index page
    create_index_page(config, output_dir)
    
    # Create a page for each indicator
    for indicator_id, indicator_data in config.items():
        indicator_dir = os.path.join(output_dir, indicator_id)
        ensure_dir(indicator_dir)
        create_indicator_page(indicator_id, indicator_data, output_dir)
    
    # Create a .nojekyll file to ensure all files are included
    with open(os.path.join(output_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    print(f"Generated {len(config)} indicator pages in {output_dir}/")

if __name__ == "__main__":
    main()
