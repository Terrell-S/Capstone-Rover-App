import json
from datetime import datetime

# Example dictionary
data = {"name": "Rover", "speed": 3.2, "active": True}

# Save to file
with open("data.json", "w") as f:
    json.dump(data, f)

# Read back
with open("data.json", "r") as f:
    loaded_data = json.load(f)

print(loaded_data)

print("Current Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M"))
