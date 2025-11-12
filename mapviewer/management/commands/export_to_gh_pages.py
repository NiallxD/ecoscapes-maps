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
        
        # Clean up previous build files (except .nojekyll and .gitkeep)
        self.stdout.write('Cleaning up previous build...')
        for item in output_dir.glob('*'):
            if item.is_file() and item.name not in ['.nojekyll', 'CNAME']:
                item.unlink()
            elif item.is_dir() and item.name != 'static':
                shutil.rmtree(item, ignore_errors=True)
        
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
            
            # Export the root URL (homepage) first
            self.export_page('', output_dir, self.config, 'index.html')
            
            # Export each page from config
            for page_name in self.config.keys():
                if page_name not in ['themes', 'indicators']:  # Skip special keys
                    continue
                self.export_page(page_name, output_dir, self.config)
            
            # Export themes page
            self.export_page('themes', output_dir, self.config, 'themes.html')
            
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
        
        # Ensure the static directory exists
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy static files from each app
        for app in settings.INSTALLED_APPS:
            if app.startswith('django.'):
                continue
                
            try:
                # Try to find the app's static directory
                app_path = Path(app.replace('.', '/'))
                app_static = app_path / 'static'
                
                # Handle case where app is in a different location (like site-packages)
                if not app_static.exists():
                    try:
                        import importlib
                        module = importlib.import_module(app)
                        if hasattr(module, '__file__'):
                            app_root = Path(module.__file__).parent
                            app_static = app_root / 'static'
                    except (ImportError, AttributeError):
                        continue
                
                if app_static.exists() and app_static.is_dir():
                    self.stdout.write(f'Copying static files from {app}...')
                    for item in app_static.rglob('*'):
                        try:
                            if item.is_file() and not any(part.startswith(('.', '_')) for part in item.parts):
                                rel_path = item.relative_to(app_static)
                                dest_path = static_dir / rel_path
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(item, dest_path)
                        except Exception as e:
                            self.stderr.write(f'Error copying {item}: {str(e)}')
                            
            except Exception as e:
                self.stderr.write(f'Error processing app {app}: {str(e)}')
        
        # Copy project-wide static files
        for static_dir_path in settings.STATICFILES_DIRS:
            if not static_dir_path:
                continue
                
            try:
                static_path = Path(static_dir_path)
                if static_path.exists() and static_path.is_dir():
                    self.stdout.write(f'Copying project static files from {static_path}...')
                    for item in static_path.rglob('*'):
                        try:
                            if item.is_file() and not any(part.startswith(('.', '_')) for part in item.parts):
                                rel_path = item.relative_to(static_path)
                                dest_path = static_dir / rel_path
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(item, dest_path)
                        except Exception as e:
                            self.stderr.write(f'Error copying {item}: {str(e)}')
            except Exception as e:
                self.stderr.write(f'Error processing static directory {static_dir_path}: {str(e)}')
        
        # Copy admin static files
        try:
            from django.contrib import admin
            admin_static = Path(admin.__file__).parent / 'static' / 'admin'
            if admin_static.exists():
                self.stdout.write('Copying admin static files...')
                dest_admin = static_dir / 'admin'
                if dest_admin.exists():
                    shutil.rmtree(dest_admin)
                shutil.copytree(admin_static, dest_admin)
        except Exception as e:
            self.stderr.write(f'Error copying admin static files: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully copied static files to {static_dir}'))
    
    def export_page(self, page_name, output_dir, config, output_filename=None):
        """Export a single page to a static HTML file."""
        try:
            # Determine the URL and output path
            url = f'/{page_name}/' if page_name else '/'
            
            # Always create .html files in the root directory for GitHub Pages
            if page_name and not output_filename:
                output_filename = f'{page_name}.html'
            else:
                output_filename = output_filename or 'index.html'
                
            # Ensure we're always writing to the root of output_dir
            output_path = output_dir / output_filename
            
            self.stdout.write(f'Exporting {url} to {output_path}...')
            
            # Create the output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get the page data from config
            page_data = config.get(page_name, {}) if (page_name and page_name in config) else {}
            
            # Prepare the context with themes and indicators
            context = {
                'page_name': page_name or 'Home',
                'themes': config.get('themes', []),  # Always include themes in context
                'indicators': {
                    'all': config.get('indicators', {}),
                    'page_name': page_data if isinstance(page_data, dict) else {}
                },
                'page_config': page_data if isinstance(page_data, dict) else {},
                'STATIC_URL': './static/'  # Relative path for static files
            }
            
            # Add map URLs if they exist
            if isinstance(page_data, dict):
                context.update({
                    'map1_url': page_data.get('map1_url', ''),
                    'map2_url': page_data.get('map2_url', '')
                })
            
            # Render the template
            try:
                content = render_to_string('mapviewer/map.html', context)
                
                # Fix any remaining static file paths to be relative to the base URL
                content = content.replace('href="/static/', 'href="static/')
                content = content.replace('src="/static/', 'src="static/')
                
                # Ensure all static file paths are relative to the base URL
                content = content.replace('href="static/', 'href="./static/')
                content = content.replace('src="static/', 'src="./static/')
                
                # Fix any remaining absolute paths that might cause issues
                content = content.replace('href="/', 'href="./')
                
                # For GitHub Pages, we need to set the base URL correctly
                # Since we're using .html files in the root, we can use './' as the base
                base_path = './'
                
                # Add base tag to fix relative paths
                head_end = content.find('</head>')
                if head_end > 0:
                    base_tag = f'<base href="{base_path}">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n</head>'
                    content = content[:head_end] + base_tag + content[head_end + 7:]
                
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
