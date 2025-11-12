import json
import os
from django.conf import settings
from django.http import JsonResponse, Http404
from django.shortcuts import render

def load_map_config():
    config_path = os.path.join(settings.BASE_DIR, 'map_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_flattened_indicators(config):
    """Convert the hierarchical structure to a flat dictionary for backward compatibility."""
    if 'indicators' in config:
        return config['indicators']
    return config  # For old config format

def get_flat_indicators_list(config):
    """Get a flat list of all indicators for the dropdown."""
    if 'indicators' in config:
        return config['indicators']
    return config  # For old config format

def get_indicator_details(config, indicator_id):
    """Get details for a specific indicator."""
    if 'indicators' in config and indicator_id in config['indicators']:
        return config['indicators'][indicator_id]
    return config.get(indicator_id)  # For old config format

def map_view(request, page_name='default'):
    config = load_map_config()
    
    # Get theme group from query string if provided
    theme_group_id = request.GET.get('theme_group')
    theme_ids_to_include = None
    
    # If theme group is specified, get the list of theme IDs to include
    if theme_group_id and 'themeGroups' in config:
        for group in config['themeGroups']:
            if group['id'] == theme_group_id:
                theme_ids_to_include = set(group['themeIds'])
                print(f"Theme group '{theme_group_id}' found. Including themes: {theme_ids_to_include}")
                break
        else:
            print(f"Theme group '{theme_group_id}' not found in config")
    
    # Handle both old and new config formats
    if 'themes' in config:  # New format with themes
        indicators = config.get('indicators', {})
        
        # If no specific page is requested, use the first available indicator
        if page_name == 'default' and indicators:
            first_indicator = next(iter(indicators.values()))
            page_config = first_indicator
        else:
            page_config = indicators.get(page_name)
            if not page_config:
                raise Http404("Indicator not found")
        
        # Pre-process themes to include indicator data
        themes = []
        for theme in config.get('themes', []):
            # Skip themes not in the selected theme group (if a group was specified)
            if theme_ids_to_include is not None and theme['id'] not in theme_ids_to_include:
                print(f"Skipping theme {theme['id']} as it's not in the selected group")
                continue
                
            theme_data = theme.copy()
            theme_data['subthemes'] = []
            
            for subtheme in theme.get('subthemes', []):
                subtheme_data = subtheme.copy()
                subtheme_data['indicator_items'] = []
                
                for indicator_id in subtheme.get('indicators', []):
                    if indicator_id in indicators:
                        indicator_data = indicators[indicator_id].copy()
                        indicator_data['id'] = indicator_id
                        subtheme_data['indicator_items'].append(indicator_data)
                
                theme_data['subthemes'].append(subtheme_data)
            
            themes.append(theme_data)
    else:  # Old format
        if page_name not in config:
            raise Http404("Page not found")
        page_config = config[page_name]
        themes = []
        indicators = config
    
    if not page_config:
        raise Http404("Indicator not found")
    
    # Find the current theme for the indicator
    current_theme = None
    for theme in themes:
        for subtheme in theme.get('subthemes', []):
            if page_name in subtheme.get('indicators', []):
                current_theme = theme
                break
        if current_theme:
            break
    
    # Update page config with theme info
    if current_theme:
        page_config['theme'] = current_theme['id']
    
    context = {
        'map1_url': page_config.get('map1_url', ''),
        'map2_url': page_config.get('map2_url', ''),
        'page_name': page_name,
        'themes': themes,
        'current_theme': current_theme,  # Add current theme to context
        'indicators': {
            'all': indicators,  # All indicators for the dropdown (flattened)
            'page_name': page_config  # Current page configuration
        },
        'page_config': page_config  # For backward compatibility
    }
    
    return render(request, 'mapviewer/map.html', context)
