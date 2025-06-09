import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

url = "https://www.gov.kz/memleket/entities/kyzylorda-karmakshy/press/article/details/7613"

response = requests.get(url)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.content, "html.parser")

# Find the table
table = soup.find("table")

if not table:
    print("Table not found!")
    exit()

# Extract headers
rows = table.find_all("tr")
headers = [header.text.strip() for header in rows[0].find_all("th")]
print("Headers:", headers)

# Extract data
data = []
for row in rows[1:]:
    cells = row.find_all("td")
    if cells:
        data.append([cell.text.strip() for cell in cells])

print("Data:", data)  # Print first 5 rows for verification

# Your parsed data

# Create a dictionary with cleaned values
result = {
    city: (re.sub(r'\D', '', prefix)[1:] if re.sub(r'\D', '', prefix).startswith('8') else re.sub(r'\D', '', prefix))
    for city, prefix in data
}
# Convert dictionary to JSON
json_result = json.dumps(result, ensure_ascii=False, indent=4)
with open("city_codes.json", "w", encoding='utf-8') as file:
    file.write(json_result)

# Print the JSON result
print(json_result)

