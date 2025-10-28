import os
import shutil
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.test import Client, RequestFactory
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.http import HttpRequest, Http404
from django.views.static import serve
import json

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Export the site as static files for GitHub Pages'

    def handle(self, *args, **options):
        # Set up the output directory (docs/ for GitHub Pages)
        output_dir = Path(settings.BASE_DIR) / 'docs'
        static_dir = output_dir / 'static'
        
        # Clean and create output directories
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a request factory
        self.factory = RequestFactory()
        
        try:
            # Load the map config
            self.load_config()
            
            # Export each page from config
            for page_name in self.config.keys():
                self.export_page(page_name, output_dir, self.config)
            
            # Export the root URL (homepage)
            self.export_page('', output_dir, self.config, 'index.html')
            
            # Copy static files
            self.copy_static_files(static_dir)
            
            # Create a simple 404 page
            self.create_404_page(output_dir)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully exported site to {output_dir}'))
            
        except Exception as e:
            logger.error(f'Error during export: {str(e)}', exc_info=True)
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
            raise
    
    def load_config(self):
        """Load the map configuration."""
        config_path = Path(settings.BASE_DIR) / 'map_config.json'
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('map_config.json not found!'))
            self.config = {}
    
    def copy_static_files(self, static_dir):
        """Copy all static files to the output directory."""
        self.stdout.write('Copying static files...')
        
        # Get the parent directory of static_dir (output_dir)
        output_dir = static_dir.parent
        
        # Copy static files from each app
        for app in settings.INSTALLED_APPS:
            if app.startswith('django.'):
                continue
                
            app_static = Path(app.replace('.', '/')) / 'static'
            if app_static.exists() and app_static.is_dir():
                self.stdout.write(f'Copying static files from {app}...')
                for item in app_static.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(app_static)
                        dest_path = static_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
        
        # Copy project-wide static files
        for static_dir_path in settings.STATICFILES_DIRS:
            if isinstance(static_dir_path, (str, Path)):
                static_path = Path(static_dir_path)
                if static_path.exists() and static_path.is_dir():
                    self.stdout.write(f'Copying project static files from {static_path}...')
                    for item in static_path.rglob('*'):
                        if item.is_file():
                            rel_path = item.relative_to(static_path)
                            dest_path = static_dir / rel_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dest_path)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully copied static files to {static_dir}'))
    
    def export_page(self, page_name, output_dir, config, output_filename=None):
        """Export a single page to a static HTML file."""
        try:
            # Determine the URL and output path
            url = f'/{page_name}/' if page_name else '/'
            output_filename = output_filename or f'{page_name}/index.html' if page_name else 'index.html'
            output_path = output_dir / output_filename
            
            self.stdout.write(f'Exporting {url} to {output_path}...')
            
            # Create the output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get the page data from config
            page_data = config.get(page_name, {}) if page_name else {}
            
            # Create a request object
            request = self.factory.get(url)
            request.META.update({
                'HTTP_HOST': 'localhost',
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': '8000',
            })
            
            # Prepare the context
            context = {
                'page_name': page_name,
                'map1_url': page_data.get('map1_url', ''),
                'map2_url': page_data.get('map2_url', ''),
                'indicators': {
                    'all': config,
                    'page_name': page_data
                },
                'page_config': page_data,
                'STATIC_URL': '/static/'  # Ensure static URL is set correctly
            }
            
            # Render the template
            try:
                content = render_to_string('mapviewer/map.html', context, request=request)
                
                # Fix any remaining static file paths
                content = content.replace('/static/', 'static/')
                
                # Write the content to a file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                self.stderr.write(f'Error rendering {url}: {str(e)}')
                raise
                
        except Exception as e:
            self.stderr.write(f'Error exporting page {page_name}: {str(e)}')
            raise
    
    def create_404_page(self, output_dir):
        """Create a simple 404 page."""
        try:
            context = {
                'title': 'Page Not Found',
                'message': 'The page you are looking for does not exist.'
            }
            content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>404 - Page Not Found</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    h1 { font-size: 50px; }
                    p { font-size: 20px; }
                </style>
            </head>
            <body>
                <h1>404</h1>
                <p>Page not found</p>
                <p><a href="/">Return to Homepage</a></p>
            </body>
            </html>
            """
            
            with open(output_dir / '404.html', 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.stderr.write(f'Error creating 404 page: {str(e)}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error exporting {url}: {str(e)}'))
