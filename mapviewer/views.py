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

def map_view(request, page_name):
    config = load_map_config()
    
    if page_name not in config:
        raise Http404("Page not found")
    
    page_config = config[page_name]
    context = {
        'map1_url': page_config.get('map1_url', ''),
        'map2_url': page_config.get('map2_url', ''),
        'page_name': page_name,
        'indicators': {
            'all': config,  # All indicators for the dropdown
            'page_name': page_config  # Current page configuration
        },
        'page_config': page_config  # For backward compatibility
    }
    
    return render(request, 'mapviewer/map.html', context)
