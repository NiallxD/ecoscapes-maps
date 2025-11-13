import pandas as pd
import json

# Load CSV and preserve order
df = pd.read_csv("/Users/niallbell/Desktop/ecoscapes-csv-in.csv")

# Ensure clean column names
df.columns = [c.strip() for c in df.columns]

# Add an order column to maintain original row order
df['__order'] = range(len(df))

# Helper: slugify text into safe IDs
def slugify(text):
    return (
        str(text)
        .lower()
        .replace("’", "")
        .replace("'", "")
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

themes = []
indicators = {}
theme_counter = 1

# First, create a mapping of themes to their order in the CSV
unique_themes = []
for theme in df['Theme'].unique():
    if theme not in unique_themes:
        unique_themes.append(theme)

theme_order = {theme: i+1 for i, theme in enumerate(unique_themes)}

# Process themes in the order they first appear in the CSV
themes = []
for theme_name in unique_themes:
    theme_group = df[df['Theme'] == theme_name]
    theme_id = slugify(theme_name)
    theme_obj = {
        "id": theme_id,
        "name": f"{theme_order[theme_name]}.0 {theme_name}",
        "description": f"Description for {theme_name}.",
        "icon": "fa-seedling",  # default, can be customized
        "subthemes": []
    }

    # Get unique subthemes in the order they first appear
    unique_subthemes = []
    for subtheme in theme_group['Subtheme'].unique():
        if subtheme not in unique_subthemes:
            unique_subthemes.append(subtheme)
    
    subtheme_order = {sub: i+1 for i, sub in enumerate(unique_subthemes)}
    
    # Process subthemes in order
    for subtheme_name in unique_subthemes:
        subtheme_group = theme_group[theme_group['Subtheme'] == subtheme_name]
        subtheme_id = slugify(subtheme_name)
        subtheme_obj = {
            "id": subtheme_id,
            "name": f"{theme_order[theme_name]}.{subtheme_order[subtheme_name]} {subtheme_name}",
            "indicators": []
        }

        indicator_order = {}
        for i, row in enumerate(subtheme_group.itertuples(index=False), start=1):
            indicator_order[row.Indicator] = i

        indicator_counter = 1
        # Iterate indicators in original order
        for _, row in subtheme_group.iterrows():
            raw_indicator = str(row["Indicator"]).strip()
            if not raw_indicator or raw_indicator.lower() == "nan":
                continue
                
            indicator_name = raw_indicator.replace("*", "").strip()
            # Use the 'id' column if it exists, otherwise use slugified indicator name
            indicator_id = str(row.get("id", "")).strip()
            if not indicator_id or indicator_id.lower() == "nan":
                indicator_id = slugify(indicator_name)
            else:
                indicator_id = indicator_id.lower()  # Ensure consistent case
            
            # Get the correct counter from our order tracking
            indicator_counter = indicator_order.get(indicator_name, 1)

            # Add to subtheme list if not already present
            if indicator_id not in subtheme_obj["indicators"]:
                subtheme_obj["indicators"].append(indicator_id)

            # Add to global indicators dictionary if not already present
            if indicator_id not in indicators:
                indicators[indicator_id] = {
                    "title": f"{theme_order[theme_name]}.{subtheme_order[subtheme_name]}.{indicator_counter} {indicator_name}",
                    "description": row.get("description", "Placeholder description.") if pd.notna(row.get("description")) else "Placeholder description.",
                    "posts": indicator_id,  # Use the ID for posts to ensure consistency
                    "icon": row.get("icon", "fa-leaf") if pd.notna(row.get("icon")) else "fa-leaf",
                    "map1_url": row.get("map1", "") if pd.notna(row.get("map1")) else "",
                    "map2_url": row.get("map2", "") if pd.notna(row.get("map2")) else ""
                }
            indicator_counter += 1

        theme_obj["subthemes"].append(subtheme_obj)

    themes.append(theme_obj)
    theme_counter += 1

# Final JSON structure
final_json = {
    "themes": themes,
    "indicators": indicators
}

# Save to file
with open("ecoscapes_framework.json", "w") as f:
    json.dump(final_json, f, indent=2)

print("✅ Conversion complete: ecoscapes_framework.json created.")
