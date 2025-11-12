import json

# Load the config file
with open('map_config.json', 'r') as f:
    config = json.load(f)

# Update descriptions for all indicators
for indicator_id, indicator_data in config['indicators'].items():
    if not indicator_data.get('description'):
        indicator_data['description'] = "This indicator provides important ecological information about the area. Further details and analysis are available in the full report."

# Save the updated config
with open('map_config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("Descriptions have been updated for all indicators.")
