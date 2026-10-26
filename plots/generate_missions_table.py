#!/usr/bin/env python3
"""
Generate interactive HTML mission table from JSON data using Jinja2
"""

import json
import math
import argparse
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

def load_mission_data(json_file):
    """Load mission data from JSON file"""
    with open(json_file, 'r') as f:
        data = json.load(f)
        # Add defaults settings for any unspecified fields
        for mission in data['missions']:
            mission.setdefault('planned_end_date', None)
            mission.setdefault('extended_end_date', None)
            mission.setdefault('multiple_flights', False)
            mission.setdefault('flight_count', None)
            mission.setdefault('date_range_note', None)
            mission.setdefault('low_energy_uncertain', False)
            mission.setdefault('high_energy_uncertain', False)
            mission.setdefault('heasarc', False)
    return data['missions']

def format_date(date_str):
    """Format date to display format, handling various precisions"""
    if not date_str:
        return ''
    
    date_str = str(date_str).strip()
    
    # Year only: YYYY
    if len(date_str) == 4 and date_str.isdigit():
        return date_str
    
    # Year-Month: YYYY-MM
    elif len(date_str) == 7 and '-' in date_str:
        return date_str.replace('-', '/')
    
    # Full date: YYYY-MM-DD
    elif len(date_str) == 10 and date_str.count('-') == 2:
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%Y/%m/%d')
        except:
            return date_str.replace('-', '/')
    
    # Unknown format, return as-is
    else:
        return date_str

def format_energy(value):
    """Format energy in keV for display.
    
    Values < 1,000,000:  displayed with commas (e.g., 50,000)
    Values >= 1,000,000: scientific notation with HTML superscript
                         (e.g., 3.0 × 10<sup>8</sup>)
    
    Returns Markup so Jinja2 does not escape the <sup> tag.
    """
    if value is None or value == '':
        return ''
    
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    # Below threshold: comma-formatted integer or decimal
    if abs(num) < 1e6:
        if num == int(num):
            return f"{int(num):,}"
        else:
            return f"{num:,.2f}"
    
    # At or above threshold: scientific notation
    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10 ** exponent)
    
    # Round mantissa to 1 decimal place, then format
    mantissa = round(mantissa, 1)
    
    # Handle rounding edge case: 9.96 rounds to 10.0
    if mantissa >= 10.0:
        mantissa = mantissa / 10.0
        exponent += 1
    
    # Format mantissa: always show one decimal place
    if mantissa == int(mantissa):
        mantissa_str = f"{int(mantissa)}.0"
    else:
        mantissa_str = f"{mantissa:.1f}"
    
    # Return as Markup so Jinja2 won't escape <sup>
    return Markup(f'{mantissa_str} &times; 10<sup>{exponent}</sup>')\
        

def get_decade_from_date(date_str):
    """Extract decade from date string"""
    if not date_str:
        return None
    try:
        year = int(date_str[:4])
        return str((year // 10) * 10)
    except:
        return None

def generate_html(missions, template_file, output_file):
    """Generate HTML from template and mission data"""
    
    # Setup Jinja2 environment with whitespace control
    #   trim_blocks:   removes newline after block tags ({% %})
    #   lstrip_blocks: strips leading whitespace before block tags
    # Together these prevent {% set %}, {% if %}, {% for %} from
    # injecting blank lines and extra indentation into the output.
    env = Environment(
        loader=FileSystemLoader('.'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    env.filters['format_date'] = format_date
    env.filters['format_energy'] = format_energy
    
    template = env.get_template(template_file)
    
    html_content = template.render(
        missions=missions,
        total_missions=len(missions)
    )
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Generated {output_file} with {len(missions)} missions")


def main():
    parser = argparse.ArgumentParser(description='Generate mission table HTML from JSON')
    parser.add_argument('--json', default='missions_data.json', 
                       help='Input JSON file (default: missions_data.json)')
    parser.add_argument('--template', default='missions_template.html', 
                       help='Jinja2 template file (default: missions_template.html)')
    parser.add_argument('--output', default='missions_table.html', 
                       help='Output HTML file (default: missions_table.html)')
    
    args = parser.parse_args()
    
    # Load data
    missions = load_mission_data(args.json)
    
    # Generate HTML
    generate_html(missions, args.template, args.output)

if __name__ == '__main__':
    main()
