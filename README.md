# EcoScapes Map Viewer

A simple web application for toggling between two map views with a clean, modern interface.

## Features

- Toggle between two map views with a single click
- Responsive design that works on all devices
- Easy configuration via JSON
- Deployable to GitHub Pages

## Local Development

1. Clone the repository:
   ```bash
   git clone git@github.com:NiallxD/ecoscapes-maps.git
   cd ecoscapes-maps
   ```

2. Run the local server:
   ```bash
   python -m http.server 8000
   ```

3. Open in your browser:
   ```
   http://localhost:8000/sample/
   ```

## Configuration

Edit `map_config.json` to add or modify map views. Each entry should have:

```json
{
    "page_name": {
        "map1_url": "https://example.com/map1",
        "map2_url": "https://example.com/map2"
    }
}
```

## Deployment to GitHub Pages

1. Run the deployment script:
   ```bash
   python deploy.py
   ```
   
2. Follow the on-screen instructions to complete the GitHub Pages setup.

3. Your site will be available at:
   ```
   https://niallxd.github.io/ecoscapes-maps/sample/
   ```

## Adding New Pages

1. Add a new entry to `map_config.json`
2. Access it at: `https://niallxd.github.io/ecoscapes-maps/your-page-name/`

## License

MIT
