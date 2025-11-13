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

## Icon Font System

This project uses a custom icon font system for better performance and customization. The system is built using `fantasticon`.

### Adding New Icons

1. **Add SVG Icons**:
   - Place your SVG icons in the `assets/icons` directory
   - Each SVG file should be named with the icon name you want to use (e.g., `home.svg`, `settings.svg`)
   - Icons should be square and ideally 24x24 or 32x32 pixels

2. **Generate the Icon Font**:
   ```bash
   npm run build:icons
   ```
   This will:
   - Create font files in `static/fonts/`
   - Generate CSS and SCSS files with the icon classes
   - Create a preview HTML file

3. **Using Icons in HTML**:
   ```html
   <i class="icon icon-home"></i>
   <i class="icon icon-settings"></i>
   ```

4. **Using Icons in CSS/SCSS**:
   ```scss
   .my-element::before {
     @extend %icon-home; // Using the icon as a mixin
   }
   ```

5. **Include the CSS**:
   Add this to your base template:
   ```html
   <link rel="stylesheet" href="{% static 'fonts/custom-icons.css' %}">
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
