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

def map_view(request, page_name):
    config = load_map_config()
    
    # Handle both old and new config formats
    if 'themes' in config:  # New format with themes
        indicators = config.get('indicators', {})
        page_config = indicators.get(page_name)
        
        # Pre-process themes to include indicator data
        themes = []
        for theme in config.get('themes', []):
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
