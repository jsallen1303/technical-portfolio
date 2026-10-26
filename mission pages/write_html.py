from flask import Flask, render_template
import json
import os
from pathlib import Path

# Tell Flask to look for templates in the current directory (.)
app = Flask(__name__, template_folder='.')
# Strip leading whitespace from blocks and trailing newlines from block tags
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

def generate_static_files():
    # Create default missions.json if it doesn't exist
    missions_file = Path('missions.json')
    if not missions_file.exists():
        print("⚠ missions.json not found, creating empty default...")
        default_missions = []
        with open('missions.json', 'w') as f:
            json.dump(default_missions, f, indent=2)
    
    # Load your main missions.json
    with open('missions.json', 'r') as f:
        missions_data = json.load(f)
        
    # Create output directory
    output_dir = Path('static_output')
    output_dir.mkdir(exist_ok=True)
    
    # Load individual JSON files from input_json/
    json_dir = Path('input_json')
    
    for json_file in json_dir.glob('*.json'):
        print(f"Processing {json_file.name}...")
        try:
            with open(json_file, 'r') as f:
                page_data = json.load(f)
            
            # Pass the JSON data as 'mission' to match your template
            template_data = {
                'mission': page_data,
                'missions': missions_data  # In case you need the full list
            }
            
            # Render template
            with app.app_context():
                html_content = render_template('mission_template.html', **template_data)
            
            # Write to static file
            output_file = output_dir / f"{json_file.stem}.html"
            with open(output_file, 'w') as f:
                f.write(html_content)
            
            print(f"✓ Generated: {output_file}")
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON Error in {json_file}: {e}")
            print(f"  Error at line {e.lineno}, column {e.colno}")
            continue
            
        except Exception as e:
            print(f"✗ Error processing {json_file}: {e}")
            continue

if __name__ == '__main__':
    generate_static_files()
