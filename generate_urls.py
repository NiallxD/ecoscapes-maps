import json

def generate_all_urls():
    # Load the config
    with open('map_config.json', 'r') as f:
        config = json.load(f)
    
    urls = []
    base_url = "https://niallxd.github.io/ecoscapes-maps/"
    
    # Generate URLs for each theme, subtheme, and indicator combination
    for theme in config.get('themes', []):
        theme_id = theme['id']
        theme_name = theme['name']
        
        for subtheme in theme.get('subthemes', []):
            subtheme_id = subtheme['id']
            subtheme_name = subtheme['name']
            
            for indicator_id in subtheme.get('indicators', []):
                # Get indicator details
                indicator_data = config.get('indicators', {}).get(indicator_id, {})
                indicator_name = indicator_data.get('title', indicator_id)
                
                # Generate URL with query parameters
                url = f"{base_url}?theme={theme_id}&subtheme={subtheme_id}&indicator={indicator_id}"
                
                urls.append({
                    'url': url,
                    'theme_name': theme_name,
                    'subtheme_name': subtheme_name,
                    'indicator_name': indicator_name,
                    'theme_id': theme_id,
                    'subtheme_id': subtheme_id,
                    'indicator_id': indicator_id
                })
    
    return urls

def save_urls_to_file(urls, filename='all_map_urls.txt'):
    with open(filename, 'w') as f:
        f.write("All Possible EcoScapes Map URLs\n")
        f.write("=" * 50 + "\n\n")
        
        for i, url_data in enumerate(urls, 1):
            f.write(f"{i}. {url_data['url']}\n")
            f.write(f"   Theme: {url_data['theme_name']} ({url_data['theme_id']})\n")
            f.write(f"   Subtheme: {url_data['subtheme_name']} ({url_data['subtheme_id']})\n")
            f.write(f"   Indicator: {url_data['indicator_name']} ({url_data['indicator_id']})\n")
            f.write("\n")
        
        f.write(f"\nTotal URLs generated: {len(urls)}\n")

if __name__ == "__main__":
    urls = generate_all_urls()
    save_urls_to_file(urls)
    print(f"Generated {len(urls)} URLs and saved to all_map_urls.txt")
