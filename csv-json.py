import pandas as pd
import json

# Load CSV
df = pd.read_csv("/Users/niallbell/Desktop/ecoscapes-csv.csv")

# Ensure clean column names
df.columns = [c.strip() for c in df.columns]

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

# Group by Theme
for theme_name, theme_group in df.groupby("Theme"):
    theme_id = slugify(theme_name)
    theme_obj = {
        "id": theme_id,
        "name": f"{theme_counter}.0 {theme_name}",
        "description": f"Description for {theme_name}.",
        "icon": "fa-seedling",  # default, can be customized
        "subthemes": []
    }

    subtheme_counter = 1
    # Group by Subtheme
    for subtheme_name, subtheme_group in theme_group.groupby("Subtheme"):
        subtheme_id = slugify(subtheme_name)
        subtheme_obj = {
            "id": subtheme_id,
            "name": f"{theme_counter}.0.{subtheme_counter} {subtheme_name}",
            "indicators": []
        }

        indicator_counter = 1
        # Iterate indicators
        for _, row in subtheme_group.iterrows():
            raw_indicator = str(row["Indicator"]).strip()
            if not raw_indicator or raw_indicator.lower() == "nan":
                continue
            indicator_name = raw_indicator.replace("*", "").strip()
            indicator_id = slugify(indicator_name)

            # Add to subtheme list
            if indicator_id not in subtheme_obj["indicators"]:
                subtheme_obj["indicators"].append(indicator_id)

            # Add to global indicators dictionary
            if indicator_id not in indicators:
                indicators[indicator_id] = {
                    "title": f"{theme_counter}.0.{subtheme_counter}.{indicator_counter} {indicator_name}",
                    "posts": row.get("posttag", indicator_id) if pd.notna(row.get("posttag")) else indicator_id,
                    "description": row.get("description", "Placeholder description.") if pd.notna(row.get("description")) else "Placeholder description.",
                    "icon": row.get("icon", "fa-leaf") if pd.notna(row.get("icon")) else "fa-leaf",
                    "map1_url": row.get("map1", "") if pd.notna(row.get("map1")) else "",
                    "map2_url": row.get("map2", "") if pd.notna(row.get("map2")) else ""
                }
            indicator_counter += 1

        theme_obj["subthemes"].append(subtheme_obj)
        subtheme_counter += 1

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
