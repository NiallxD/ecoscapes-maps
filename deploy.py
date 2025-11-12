import os
import json
import shutil
import subprocess
from pathlib import Path

def collect_static():
    """Collect static files for GitHub Pages."""
    if os.path.exists('docs'):
        shutil.rmtree('docs')
    os.makedirs('docs', exist_ok=True)
    
    # Copy template and static files
    shutil.copytree('templates', 'docs/templates', dirs_exist_ok=True)
    
    # Create a simple HTML file for GitHub Pages
    with open('docs/index.html', 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EcoScapes Maps</title>
            <meta http-equiv="refresh" content="0; url=/EcoScapes-Map-App-v2/sample/" />
        </head>
        <body>
            <p>Redirecting to map viewer...</p>
        </body>
        </html>
        """)
        
    # Load the map config to get theme groups
    with open('map_config.json') as f:
        config = json.load(f)
    
    # Create a version of the site for each theme group
    theme_groups = config.get('themeGroups', [])
    
    # Create a version for each theme group
    for group in theme_groups:
        group_dir = os.path.join('docs', group['id'])
        os.makedirs(group_dir, exist_ok=True)
        
        # Copy the template
        shutil.copy('templates/mapviewer/map.html', os.path.join(group_dir, 'index.html'))
        
        # Update the JavaScript to set the default theme group
        with open(os.path.join(group_dir, 'index.html'), 'r+') as f:
            content = f.read()
            # Add JavaScript to set the theme group
            content = content.replace("<script>", f"""
            <script>
            // Set the theme group from the URL
            if (!window.location.search.includes('theme_group=')) {{
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('theme_group', '{group["id"]}');
                window.history.replaceState({{}}, '', newUrl);
            }}
            """)
            f.seek(0)
            f.write(content)
            f.truncate()
    
    # Also create a default version with all themes
    os.makedirs('docs/all', exist_ok=True)
    shutil.copy('templates/mapviewer/map.html', 'docs/all/index.html')
    
    # Copy map config
    shutil.copy('map_config.json', 'docs/map_config.json')
    
    # Create a simple server for local testing
    with open('docs/server.py', 'w') as f:
        f.write("""
        import http.server
        import socketserver
        import json
        import os
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/map_config.json':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    with open('map_config.json', 'rb') as f:
                        self.wfile.write(f.read())
                    return
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        if __name__ == '__main__':
            PORT = 8000
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"Serving at port {PORT}")
                httpd.serve_forever()
        """)

def deploy_to_github():
    """Deploy the static site to GitHub Pages."""
    # Add all files
    subprocess.run(['git', 'add', '.'], check=True)
    
    # Commit changes
    subprocess.run(['git', 'commit', '-m', 'Deploy to GitHub Pages'], check=True)
    
    # Add remote if it doesn't exist
    try:
        subprocess.run(['git', 'remote', 'add', 'origin', 'git@github.com:NiallxD/ecoscapes-maps.git'], check=True)
    except subprocess.CalledProcessError:
        pass  # Remote already exists
    
    # Push to main branch
    subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
    
    print("\nDeployment to GitHub Pages is ready!")
    print("1. Go to your repository settings on GitHub")
    print("2. Go to Pages settings")
    print("3. Set source to 'Deploy from a branch'")
    print("4. Select 'master' branch and '/docs' folder")
    print("5. Click Save")
    print("\nYour site will be available at: https://niallxd.github.io/ecoscapes-maps/")
    print("Example map page: https://niallxd.github.io/ecoscapes-maps/sample/")

if __name__ == '__main__':
    print("Preparing files for GitHub Pages...")
    collect_static()
    
    print("\nTo test locally:")
    print("1. cd docs")
    print("2. python3 -m http.server 8000")
    print("3. Open one of these URLs in your browser:")
    print("   - http://localhost:8000/all/ (All themes)")
    for group in theme_groups:
        print(f"   - http://localhost:8000/{group['id']}/ ({group['name']} theme group)")
    print()
    
    deploy = input("Would you like to deploy to GitHub now? (y/n): ").lower()
    if deploy == 'y':
        deploy_to_github()
