import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.test import Client, RequestFactory
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpRequest
import json

class Command(BaseCommand):
    help = 'Export the site as static files for GitHub Pages'

    def handle(self, *args, **options):
        # Set up the output directory (docs/ for GitHub Pages)
        output_dir = Path(settings.BASE_DIR) / 'docs'
        static_dir = output_dir / 'static'
        
        # Create output directories if they don't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Load the map config to get all pages
        config_path = Path(settings.BASE_DIR) / 'map_config.json'
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create a request factory
        factory = RequestFactory()
        
        # Export each page
        for page_name in config.keys():
            self.export_page(page_name, output_dir, config)
        
        # Export the root URL (homepage)
        self.export_page('', output_dir, config, 'index.html')
        
        # Copy static files
        self.stdout.write('Copying static files...')
        static_src = Path(settings.STATIC_ROOT)
        if static_src.exists():
            # First, collect static files
            self.stdout.write('Collecting static files...')
            os.system('python manage.py collectstatic --noinput')
            
            # Then copy them to the output directory
            for item in static_src.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(static_src)
                    dest_path = static_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully exported site to {output_dir}'))
    
    def export_page(self, page_name, output_dir, config, output_filename=None):
        """Export a single page to a static HTML file."""
        # Determine the URL and output path
        url = f'/{page_name}/' if page_name else '/'
        output_filename = output_filename or f'{page_name}/index.html' if page_name else 'index.html'
        output_path = output_dir / output_filename
        
        self.stdout.write(f'Exporting {url} to {output_path}...')
        
        # Create the output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get the page data from config
            page_data = config.get(page_name, {}) if page_name else {}
            
            # Create a request object
            request = HttpRequest()
            request.method = 'GET'
            request.path = url
            request.META = {
                'HTTP_HOST': 'localhost',
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': '8000',
            }
            
            # Prepare the context
            context = {
                'page_name': page_name,
                'map1_url': page_data.get('map1_url', ''),
                'map2_url': page_data.get('map2_url', ''),
                'indicators': {
                    'all': config,
                    'page_name': page_data
                },
                'page_config': page_data
            }
            
            # Render the template
            content = render_to_string('mapviewer/map.html', context, request=request)
            
            # Write the content to a file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error exporting {url}: {str(e)}'))
