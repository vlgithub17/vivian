import json
import os

body = {'name': ['Viviancccccv'], 'animal': ['Dog']}
new = {'name': ['Viviancccccv'], 'animal': ['Cat']}

path = 'favorite-animal/vivian.json'

with open(path, "r") as f:
    data = json.load(f)
    
    # Append the new animal to the 'animal' list
    if isinstance(new['animal'], dict):
        data['animal'].append(new['animal'][0])
    else:
        data['animal'].append(new['animal'][0])
    
    # Print the updated data
    print(data)

# Write the updated data back to the file
with open(path, "w") as f:
    json.dump(data, f, indent=4)
 