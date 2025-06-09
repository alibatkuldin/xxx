import xml.etree.ElementTree as ET
import json
from datetime import datetime

def convert_duration(duration_str):
    """Convert duration from 'HH:MM:SS' format to seconds."""
    try:
        h, m, s = map(int, duration_str.split(':'))
        return h * 3600 + m * 60 + s
    except ValueError:
        return 0

def get_text(element, xpath, namespace):
    """Get text content from an XML element or return an empty string if not found."""
    found_element = element.find(xpath, namespace)
    return found_element.text if found_element is not None else ""

def parse_xml_to_json(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract namespace
    namespace = {'ns': 'http://pa.cellebrite.com/report/2.0'}

    call_history = []
    
    for call in root.findall('.//ns:model[@type="Call"]', namespace):
        # Extract fields
        direction = get_text(call, './/ns:field[@name="Direction"]/ns:value', namespace).lower()
        app = get_text(call, './/ns:field[@name="Source"]/ns:value', namespace) or "unknown"
        timestamp = get_text(call, './/ns:field[@name="TimeStamp"]/ns:value', namespace)
        duration_str = get_text(call, './/ns:field[@name="Duration"]/ns:value', namespace)
        duration = convert_duration(duration_str)
        status = get_text(call, './/ns:field[@name="Status"]/ns:value', namespace) or "unknown"
        
        # Get caller number and name
        number = get_text(call, './/ns:multiModelField[@name="Parties"]/ns:model/ns:field[@name="Identifier"]/ns:value', namespace)
        name = get_text(call, './/ns:multiModelField[@name="Parties"]/ns:model/ns:field[@name="Name"]/ns:value', namespace)

        # Construct the call entry
        call_data = {
            "type": direction,
            "app": app,
            "timestamp": timestamp,
            "duration": duration,
            "status": status,
            "number": number,
            "name": name
        }
        call_history.append(call_data)

    return {"call_history": call_history}

# File paths
xml_file = r'C:\Users\timur\OneDrive\Рабочий стол\My\AITU project\Call_history_api\Report.xml'
output_json = r'C:\Users\timur\OneDrive\Рабочий стол\My\AITU project\Call_history_api\xiaomi_test.json'

# Convert XML to JSON
json_data = parse_xml_to_json(xml_file)

# Save JSON data to file
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)

print(f"Conversion complete! JSON data saved to {output_json}")
