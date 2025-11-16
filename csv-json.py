import pandas as pd
import json

# Load CSV and preserve order
df = pd.read_csv("/Users/niallbell/Desktop/EcoScapes Indicator Framework_Nov16_2025.csv")

# Ensure clean column names
df.columns = [c.strip() for c in df.columns]

# Add an order column to maintain original row order
df['__order'] = range(len(df))

# Helper: slugify text into safe IDs
def slugify(text):
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

# Helper: clean text by removing apostrophes
def clean_text(text):
    return str(text).replace("'", "") if pd.notna(text) else ""

themes = []
indicators = {}
theme_counter = 1

# First, create a mapping of themes to their order in the CSV
unique_themes = []
for theme in df['Theme'].unique():
    if theme not in unique_themes and pd.notna(theme):
        unique_themes.append(theme)

theme_order = {theme: i+1 for i, theme in enumerate(unique_themes)}

# Process themes in the order they first appear in the CSV
themes = []
for theme_name in unique_themes:
    theme_group = df[df['Theme'] == theme_name]
    theme_id = slugify(theme_name)
    
    # Get theme info from the first row of the theme group
    theme_info = theme_group['ThemeInfo'].iloc[0] if 'ThemeInfo' in theme_group and pd.notna(theme_group['ThemeInfo'].iloc[0]) else f"Description for {theme_name}"
    
    # Get theme icon from the first row of the theme group
    theme_icon = theme_group['SubthemeIcon'].iloc[0] if 'SubthemeIcon' in theme_group and pd.notna(theme_group['SubthemeIcon'].iloc[0]) else "fa-seedling"
    
    theme_obj = {
        "id": theme_id,
        "name": f"{theme_order[theme_name]}.0 {theme_name}",
        "description": theme_info,
        "icon": theme_icon,
        "subthemes": []
    }

    # Get unique subthemes in the order they first appear
    unique_subthemes = []
    for subtheme in theme_group['Subtheme'].unique():
        if subtheme not in unique_subthemes and pd.notna(subtheme):
            unique_subthemes.append(subtheme)
    
    subtheme_order = {sub: i+1 for i, sub in enumerate(unique_subthemes)}
    
    # Process subthemes in order
    for subtheme_name in unique_subthemes:
        subtheme_group = theme_group[theme_group['Subtheme'] == subtheme_name]
        subtheme_id = slugify(subtheme_name)
        
        # Get subtheme info and icon from the first row of the group
        subtheme_info = subtheme_group['SubthemeInfo'].iloc[0] if 'SubthemeInfo' in subtheme_group and pd.notna(subtheme_group['SubthemeInfo'].iloc[0]) else f"Description for {subtheme_name}"
        subtheme_icon = subtheme_group['SubthemeIcon'].iloc[0] if 'SubthemeIcon' in subtheme_group and pd.notna(subtheme_group['SubthemeIcon'].iloc[0]) else "fa-leaf"
        
        subtheme_obj = {
            "id": subtheme_id,
            "name": f"{theme_order[theme_name]}.{subtheme_order[subtheme_name]} {subtheme_name}",
            "description": subtheme_info,
            "icon": subtheme_icon,
            "indicators": []
        }

        # Get indicators in their original order
        indicator_order = {}
        for i, row in enumerate(subtheme_group.itertuples(index=False), start=1):
            indicator_name = str(row.Indicator).strip()
            if indicator_name and indicator_name.lower() != 'nan':
                indicator_order[indicator_name] = i

        # Process indicators in order
        for _, row in subtheme_group.iterrows():
            raw_indicator = str(row["Indicator"]).strip()
            if not raw_indicator or raw_indicator.lower() == "nan":
                continue
                
            indicator_name = raw_indicator.replace("*", "").strip()
            indicator_id = str(row.get("id", "")).strip()
            if not indicator_id or indicator_id.lower() == "nan":
                indicator_id = slugify(indicator_name)
            else:
                indicator_id = indicator_id.lower()
            
            # Get the correct counter from our order tracking
            indicator_counter = indicator_order.get(indicator_name, 1)

            # Add to subtheme list if not already present
            if indicator_id not in [i for i in subtheme_obj["indicators"]]:
                subtheme_obj["indicators"].append(indicator_id)

            # Add to global indicators dictionary if not already present
            if indicator_id not in indicators:
                # Clean text fields
                clean_indicator_name = clean_text(indicator_name)
                clean_posts = clean_text(row.get("posttag", indicator_id))
                clean_description = clean_text(row.get("IndicatorInfo", ""))
                clean_source = clean_text(row.get("Source", ""))
                clean_unit = clean_text(row.get("UnitOfMeasure", ""))
                
                indicators[indicator_id] = {
                    "title": f"{theme_order[theme_name]}.{subtheme_order[subtheme_name]}.{indicator_counter} {clean_indicator_name}",
                    "description": clean_description if pd.notna(row.get("IndicatorInfo")) else "",
                    "source": clean_source if pd.notna(row.get("Source")) else "",
                    "unit_of_measure": clean_unit if pd.notna(row.get("UnitOfMeasure")) else "",
                    "posts": clean_posts if pd.notna(row.get("posttag")) else indicator_id,
                    "icon": row.get("IndicatorIcon", "fa-leaf") if pd.notna(row.get("IndicatorIcon")) else "fa-leaf",
                    "map1_url": "https://felt.com/embed/map/S2S-ConnectivityModel-v0p1-copy-mr4RufF9AQM9B5KvTx1IczZC?loc=50.1164%2C-123.0674%2C8.51z&legend=1&cooperativeGestures=1&link=1&geolocation=0&zoomControls=1&scaleBar=1",
                    "map2_url": "https://cascadia.staging.dashboard.terradapt.org/?zoom=10.57924853633501&lng=-123.16974611514613&lat=49.724616106137404&opacity=0.75&layerTheme=%22landcover%22&layerScope=%22monitor%22&layerVisualisation=%22pixel%22&minTimestamp=%221984-07-01T00%3A00%3A00%22&maxTimestamp=%222024-07-01T00%3A00%3A00%22&selectedLayer=%22landcover_class%22&layerView=%22status%22&layerStart=%221984-07-01T00%3A00%3A00%22&layerEnd=%222024-07-01T00%3A00%3A00%22&currentTimestamp=%222024-07-01T00%3A00%3A00%22&pitch=45.997005671225544&bearing=11.999218870754135"
                }

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
