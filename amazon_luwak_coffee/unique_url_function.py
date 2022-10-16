import json

# Load the JSON file
f = open("pdp_urls.json")
json_file = json.load(f)
f.close()

# Print out the URLs from the list of dicts
for i in json_file:
    print(i["url"] + '\n')

# Enumerate over the list of dicts and check if there are any duplicates. Print the length of the list after eliminating duplicates
print(len([i for idx, value in enumerate(json_file) if value not in json_file[idx + 1:]]))