import pandas as pd
import json
import os

# Load CSV and preserve order
csv_path = "/Users/niallbell/Desktop/EcoScapes_Indicator_Framework_CURRENT-IMPORT.csv"
df = pd.read_csv(csv_path, encoding='utf-8')

# Ensure clean column names
df.columns = [c.strip() for c in df.columns]


# Helper: slugify text into safe IDs
def slugify(text):
    if pd.isna(text):
        return ""
    return (
        str(text)
        .lower()
        .replace("'", "")  # Remove all apostrophes
        .replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "-")
        .replace(":", "")
        .replace("*", "")
        .replace(" ", "-")
        .strip()
    )


# Helper: clean text
def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).strip()


# Helper: format source URL as HTML link
def format_source(row):
    # Convert pandas Series to dict if needed
    if hasattr(row, 'to_dict'):
        row = row.to_dict()
    
    # Handle case where row is a dictionary
    if isinstance(row, dict):
        url = row.get('Source', '')
        if not url or pd.isna(url):
            return ""
        url = str(url).strip()
        if not url.startswith('http'):
            return url
        
        link_text = "Source"
        if 'LinkText' in row and pd.notna(row['LinkText']) and str(row['LinkText']).strip():
            link_text = str(row['LinkText']).strip()
        
        return f'<a target="_blank" href="{url}">{link_text}</a>'
    
    # Handle case where row is just a URL string
    if not row or pd.isna(row):
        return ""
    url = str(row).strip()
    if url.startswith('http'):
        return f'<a target="_blank" href="{url}">Source</a>'
    return url


# Initialize output structure
themes = []
indicators = {}

# Get unique themes in order of appearance
theme_order = {}
for i, theme in enumerate(df['Theme'].drop_duplicates()):
    if pd.notna(theme):
        theme_order[theme] = i + 1

# Process themes in order of appearance
themes = []
for theme_name, theme_group in df.groupby('Theme', sort=False):
    if pd.isna(theme_name):
        continue

    theme_id = slugify(theme_name)
    theme_info = clean_text(
        theme_group['ThemeInfo'].iloc[0]) if 'ThemeInfo' in theme_group.columns else f"Description for {theme_name}"
    theme_icon = clean_text(theme_group['Theme Icon'].iloc[0]) if 'Theme Icon' in theme_group.columns else "fa-seedling"

    theme_obj = {
        "id": f"{theme_order[theme_name]:02d}-{theme_id}",
        "name": f"{theme_order[theme_name]}.0 {theme_name}",
        "description": theme_info,
        "icon": theme_icon,
        "subthemes": []
    }

    # Process subthemes in order of appearance
    subtheme_counter = 1
    for (subtheme_name, subtheme_group) in theme_group.groupby('Subtheme', sort=False):
        if pd.isna(subtheme_name):
            continue

        subtheme_id = slugify(subtheme_name)
        subtheme_info = clean_text(subtheme_group['SubthemeInfo'].iloc[
                                       0]) if 'SubthemeInfo' in subtheme_group.columns else f"Description for {subtheme_name}"
        subtheme_icon = clean_text(
            subtheme_group['SubThemeIcon'].iloc[0]) if 'SubThemeIcon' in subtheme_group.columns else "fa-leaf"

        subtheme_obj = {
            "id": f"{theme_order[theme_name]:02d}-{subtheme_counter:02d}-{subtheme_id}",
            "name": f"{theme_order[theme_name]}.{subtheme_counter} {subtheme_name}",
            "description": subtheme_info,
            "icon": subtheme_icon,
            "indicators": []
        }

        # Process indicators in order of appearance
        indicator_counter = 1
        for _, row in subtheme_group.iterrows():
            indicator_name = clean_text(row.get('Indicator', ''))
            if not indicator_name or indicator_name.lower() == 'nan':
                continue

            # Generate the base indicator ID with full index path
            indicator_base_id = slugify(indicator_name)
            indicator_id = f"{theme_order[theme_name]:02d}-{subtheme_counter:02d}-{indicator_counter:02d}-{indicator_base_id}"
            
            # Keep the original ID for reference in the title
            original_id = indicator_base_id
            subtheme_lower = subtheme_name.lower()
            if 'linkage' in subtheme_lower:
                original_id = f"linkage-{original_id}"
            elif 'habitat' in subtheme_lower and 'core' in subtheme_lower:
                original_id = f"habitat-{original_id}"
                
            clean_description = clean_text(row.get("IndicatorInfo", ""))
            clean_source = clean_text(row.get("Source", ""))
            clean_unit = clean_text(row.get("UnitOfMeasure", ""))
            clean_posts = clean_text(row.get("posttag", ""))

            # Add indicator to subtheme's indicators list
            subtheme_obj["indicators"].append(indicator_id)

            # Add indicator details to indicators dictionary
            indicators[indicator_id] = {
                "title": f"{theme_order[theme_name]}.{subtheme_counter}.{indicator_counter} {indicator_name}",
                "description": clean_description,
                "source": format_source(row),
                "unit_of_measure": clean_unit,
                "icon": clean_text(row.get("IndicatorIcon", "")) or "fa-leaf"
            }

            # Set default map URLs
            default_map1 = "https://felt.com/embed/map/S2S-ConnectivityModel-v0p1-copy-mr4RufF9AQM9B5KvTx1IczZC?loc=50.1164%2C-123.0674%2C8.51z&legend=1&cooperativeGestures=1&link=1&geolocation=0&zoomControls=1&scaleBar=1"
            default_map2 = "https://cascadia.staging.dashboard.terradapt.org/?zoom=10.57924853633501&lng=-123.16974611514613&lat=49.724616106137404&opacity=0.75&layerTheme=%22landcover%22&layerScope=%22monitor%22&layerVisualisation=%22pixel%22&minTimestamp=%221984-07-01T00%3A00%3A00%22&maxTimestamp=%222024-07-01T00%3A00%3A00%22&selectedLayer=%22landcover_class%22&layerView=%22status%22&layerStart=%221984-07-01T00%3A00%3A00%22&layerEnd=%222024-07-01T00%3A00%3A00%22&currentTimestamp=%222024-07-01T00%3A00%3A00%22&pitch=45.997005671225544&bearing=11.999218870754135"
            
            # Use map URLs from CSV if they exist, otherwise use defaults
            indicators[indicator_id]["map1_url"] = clean_text(row.get("map1_url", default_map1)) or default_map1
            indicators[indicator_id]["map2_url"] = clean_text(row.get("map2_url", default_map2)) or default_map2

            indicator_counter += 1

        subtheme_counter += 1
        theme_obj["subthemes"].append(subtheme_obj)

    themes.append(theme_obj)

# Final JSON structure
final_json = {
    "themes": themes,
    "indicators": indicators,
    "map1_url": "https://felt.com/embed/map/S2S-ConnectivityModel-v0p1-copy-mr4RufF9AQM9B5KvTx1IczZC?loc=50.1164%2C-123.0674%2C8.51z&legend=1&cooperativeGestures=1&link=1&geolocation=0&zoomControls=1&scaleBar=1",
    "map2_url": "https://cascadia.staging.dashboard.terradapt.org/?zoom=10.57924853633501&lng=-123.16974611514613&lat=49.724616106137404&opacity=0.75&layerTheme=%22landcover%22&layerScope=%22monitor%22&layerVisualisation=%22pixel%22&minTimestamp=%221984-07-01T00%3A00%3A00%22&maxTimestamp=%222024-07-01T00%3A00%3A00%22&selectedLayer=%22landcover_class%22&layerView=%22status%22&layerStart=%221984-07-01T00%3A00%3A00%22&layerEnd=%222024-07-01T00%3A00%3A00%22&currentTimestamp=%222024-07-01T00%3A00%3A00%22&pitch=45.997005671225544&bearing=11.999218870754135"
}


# Helper function to replace straight single quotes with curly apostrophes
def fix_quotes(obj):
    if isinstance(obj, str):
        # Replace straight single quotes with curly apostrophes
        return obj.replace("'", "'").replace("''", "'")
    elif isinstance(obj, dict):
        return {k: fix_quotes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_quotes(item) for item in obj]
    return obj


# Save to file with fixed quotes
with open("ecoscapes_framework.json", "w") as f:
    json.dump(fix_quotes(final_json), f, indent=2, ensure_ascii=False)

print("✅ Conversion complete: ecoscapes_framework.json created.")
