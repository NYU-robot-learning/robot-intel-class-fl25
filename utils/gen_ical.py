import re
import pytz
from ics import Calendar, Event
from datetime import datetime


COURSE_ID = "CSCI-UA 480-073 Robotics" 
COURSE_LOCATION = "Room C15, 60 5th Ave"

# TODO: office hours

# Function to parse the markdown table
def parse_markdown_table(markdown):
    lines = markdown.strip().splitlines()
    syllabus = []

    for line in lines[3:]:  # Skip the header lines
        columns = re.split(r'\s*\|\s*', line.strip())
        if len(columns) < 3:
            continue
        
        date = columns[1]
        if not date or 'Part' in columns[2]:
            continue
        
        # Extract date and day
        match = re.match(r'(\d{2}/\d{2}/\d{4}) \((\w{3})\)', date)
        if match:
            date_str = match.group(1)
            day_str = match.group(2)
            title = re.sub(r'<[^>]+>', '', columns[2]).strip()  # Remove HTML tags
            description = title.split(': ', 1)[1] if ': ' in title else ''
            homework = columns[3].strip()
            
            syllabus.append({
                "date": date_str,
                "day": day_str,
                "title": title.split(': ', 1)[0],
                "description": description,
                "homework": homework
            })
    
    return syllabus

def generate_ics(syllabus, output_file="syllabus.ics"):
    calendar = Calendar()
    eastern = pytz.timezone('America/New_York')
    
    for item in syllabus:
        event_date = datetime.strptime(item["date"], "%m/%d/%Y")
        event_start = eastern.localize(event_date.replace(hour=15, minute=30))
        event_end = eastern.localize(event_date.replace(hour=16, minute=45))

        event = Event()
        event.name = f"{item['title']}: {item['description']}"
        event.begin = event_start.isoformat()
        event.end = event_end.isoformat()
        event.description = item["title"] + ": " + item["description"]
        
        if item["homework"]:
            event.description += f"\nHomework: {item['homework']}"
            event.name += ' / ' + item['homework']
        
        event.location = COURSE_LOCATION
        event.description += "\n\nTo get to C15, go down the stairs to the right after you enter the building."
        calendar.events.add(event)
    
    with open(output_file, "w") as f:
        f.writelines(calendar)
    
    print(f"ICS file generated successfully: {output_file}")

if __name__ == "__main__":
    with open("../docusaurus/website/src/pages/syllabus.md") as f:
        markdown_syllabus = f.readlines()
    markdown_syllabus = [x for x in markdown_syllabus if "|" in x]
    markdown_syllabus = "\n".join(markdown_syllabus)
    parsed_syllabus = parse_markdown_table(markdown_syllabus)

    generate_ics(parsed_syllabus)

