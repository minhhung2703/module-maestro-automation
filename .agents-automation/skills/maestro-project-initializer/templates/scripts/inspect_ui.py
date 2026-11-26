import xml.etree.ElementTree as ET
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'ui-dumps/current_ui.xml'

content = ""
for enc in ['utf-16', 'utf-16-le', 'utf-8']:
    try:
        with open(filename, 'r', encoding=enc) as f:
            content = f.read()
        if content.strip().startswith('<?xml') or '<hierarchy' in content:
            break
    except Exception:
        pass

if not content:
    print("Cannot read file")
    sys.exit(1)

start_idx = content.find("<hierarchy")
end_idx = content.find("</hierarchy>")
if start_idx != -1 and end_idx != -1:
    xml_str = content[start_idx:end_idx + len("</hierarchy>")]
    root = ET.fromstring(xml_str)
else:
    root = ET.fromstring(content)

print(f"=== UI Elements from {filename} ===")
for node in root.iter():
    t = node.attrib.get('text', '')
    res_id = node.attrib.get('resource-id', '')
    bounds = node.attrib.get('bounds', '')
    cls = node.attrib.get('class', '').split('.')[-1]
    if t or (res_id and ('btn' in res_id or 'item' in res_id or 'tv' in res_id or 'layout' in res_id or 'Menu' in res_id or 'edt' in res_id or 'edit' in res_id)):
        safe_t = t.encode('ascii', errors='replace').decode('ascii')
        print(f"{cls:15} | id={res_id:35} | text={safe_t:25} | bounds={bounds}")
