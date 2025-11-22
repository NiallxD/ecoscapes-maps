import json
import csv
import os

def clean_html_tags(text):
    """Remove HTML tags from text if present"""
    if not text:
        return ""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def main():
    # Define file paths
    input_file = 'ecoscapes_framework.json'
    output_file = 'ecoscapes_framework_export.csv'
    
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV file and write header
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'theme_id', 'theme_name', 'theme_description', 'theme_icon',
            'subtheme_id', 'subtheme_name', 'subtheme_description', 'subtheme_icon',
            'indicator_id', 'indicator_title', 'indicator_description', 
            'indicator_source', 'indicator_unit', 'indicator_icon',
            'indicator_map1_url', 'indicator_map2_url'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each theme
        for theme in data.get('themes', []):
            theme_row = {
                'theme_id': theme.get('id', ''),
                'theme_name': theme.get('name', ''),
                'theme_description': clean_html_tags(theme.get('description', '')),
                'theme_icon': theme.get('icon', '')
            }
            
            # Process each subtheme in the theme
            for subtheme in theme.get('subthemes', []):
                subtheme_row = {
                    **theme_row,
                    'subtheme_id': subtheme.get('id', ''),
                    'subtheme_name': subtheme.get('name', ''),
                    'subtheme_description': clean_html_tags(subtheme.get('description', '')),
                    'subtheme_icon': subtheme.get('icon', '')
                }
                
                # Process each indicator in the subtheme
                for indicator_id in subtheme.get('indicators', []):
                    indicator = data.get('indicators', {}).get(indicator_id, {})
                    if indicator:
                        writer.writerow({
                            **subtheme_row,
                            'indicator_id': indicator_id,
                            'indicator_title': indicator.get('title', ''),
                            'indicator_description': clean_html_tags(indicator.get('description', '')),
                            'indicator_source': clean_html_tags(indicator.get('source', '')),
                            'indicator_unit': indicator.get('unit_of_measure', ''),
                            'indicator_icon': indicator.get('icon', ''),
                            'indicator_map1_url': indicator.get('map1_url', ''),
                            'indicator_map2_url': indicator.get('map2_url', '')
                        })
    
    print(f"✅ Conversion complete: {os.path.abspath(output_file)} created.")

if __name__ == "__main__":
    main()
