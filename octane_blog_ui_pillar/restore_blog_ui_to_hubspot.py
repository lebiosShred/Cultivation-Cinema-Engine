import urllib.request
import json
import os

token = os.environ.get('HUBSPOT_ACCESS_TOKEN', '')
if not token:
    print("Error: HUBSPOT_ACCESS_TOKEN environment variable is not set.")
    exit(1)
layout_id = '65127478077'
url = f'https://api.hubapi.com/content/api/v2/layouts/{layout_id}'

script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'widget_blog_post_source.html'), 'r', encoding='utf-8') as f:
    clean_post_source = f.read()

req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as resp:
    layout = json.loads(resp.read().decode('utf-8'))

def update_module(node):
    if isinstance(node, dict):
        if node.get('name') == 'module_151388194052436':
            node['params']['blog_post_source'] = clean_post_source
            return True
        for v in node.values():
            if update_module(v): return True
    elif isinstance(node, list):
        for i in node:
            if update_module(i): return True
    return False

update_module(layout['layout_data'])

stylesheet_injection = '''<link rel="stylesheet" href="https://blog.octanesolutions.com.au/hubfs/hub_generated/template_assets/1/64565249625/1741527457237/template_Octane_2022_Stylesheet.min.css">
<link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;0,900;1,400&display=swap" rel="stylesheet">'''

layout['custom_head'] = stylesheet_injection

put_req = urllib.request.Request(
    url,
    data=json.dumps(layout).encode('utf-8'),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    method='PUT'
)

with urllib.request.urlopen(put_req) as resp:
    print(f'Successfully restored layout {layout_id}! HTTP Status: {resp.getcode()}')
