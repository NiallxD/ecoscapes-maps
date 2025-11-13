import json
import csv
from collections import OrderedDict

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def extract_indicators(config):
    rows = []
    
    # Create a mapping of theme IDs to their display names (without numbers)
    theme_id_to_name = {}
    for theme in config['themes']:
        # Extract theme name without the number prefix
        theme_name = ' '.join(theme['name'].split(' ')[1:])
        theme_id_to_name[theme['id']] = theme_name
    
    # Create a mapping of indicator IDs to their full data
    indicator_data = {}
    for indicator_id, data in config['indicators'].items():
        # Use the indicator ID as the name to preserve -core and -linkage suffixes
        # Convert the ID to a more readable format (replace hyphens with spaces and capitalize words)
        indicator_name = ' '.join(word.capitalize() for word in indicator_id.split('-'))
        indicator_data[indicator_id] = {
            'id': indicator_id,  # Store the original ID
            'name': indicator_name,
            'description': data.get('description', ''),
            'icon': data.get('icon', 'fa-leaf'),
            'posts': data.get('posts', indicator_id),
            'map1': data.get('map1_url', ''),
            'map2': data.get('map2_url', '')
        }
    
    # Now go through themes and subthemes to build the CSV
    for theme in config['themes']:
        theme_name = ' '.join(theme['name'].split(' ')[1:])
        
        for subtheme in theme.get('subthemes', []):
            subtheme_name = ' '.join(subtheme['name'].split(' ')[1:])
            
            for indicator_id in subtheme.get('indicators', []):
                if indicator_id in indicator_data:
                    data = indicator_data[indicator_id]
                    rows.append({
                        'Theme': theme_name,
                        'Subtheme': subtheme_name,
                        'Indicator': data['id'],  # Use the original ID to preserve -core and -linkage
                        'posttag': data['posts'],
                        'description': data['description'],
                        'icon': data['icon'],
                        'map1': data['map1'],
                        'map2': data['map2']
                    })
    
    return rows

def write_to_csv(rows, output_file):
    if not rows:
        return
        
    fieldnames = ['Theme', 'Subtheme', 'Indicator', 'posttag', 'description', 'icon', 'map1', 'map2']
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    config = load_config('map_config.json')
    rows = extract_indicators(config)
    write_to_csv(rows, 'ecoscapes-export.csv')
    print("CSV file has been created: ecoscapes-export.csv")

if __name__ == "__main__":
    main()
