Ah, I understand - we need to find all activity URLs within each section that match those patterns, regardless of the specific ID. Let me update the code to handle this.



```python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

LOGIN_URL = "https://online.tiffin.edu/login/index.php"

def login_to_moodle(session, username, password):
    """Logs into Moodle and ensures session authentication persists."""
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.content, "html.parser")
    logintoken_tag = soup.find("input", {"name": "logintoken"})
    logintoken = logintoken_tag["value"] if logintoken_tag else None
    
    login_payload = {"username": username, "password": password}
    if logintoken:
        login_payload["logintoken"] = logintoken
    
    response = session.post(LOGIN_URL, data=login_payload)
    if "login" in response.url or "Invalid login" in response.text:
        st.error("Login failed! Check your credentials.")
        return False
    return True

def find_activity_links(section_soup):
    """Finds all forum and assignment links within a section."""
    activities = []
    
    # Define patterns for forum and assignment URLs
    activity_patterns = [
        r'https://online\.tiffin\.edu/mod/hsuforum/view\.php\?id=\d+',
        r'https://online\.tiffin\.edu/mod/assign/view\.php\?id=\d+'
    ]
    
    # Find all links in the section
    links = section_soup.find_all('a')
    
    for link in links:
        href = link.get('href', '')
        for pattern in activity_patterns:
            if re.match(pattern, str(href)):
                # Get the activity title
                title_elem = link.find("span", class_="instancename") or link.find_parent().find("span", class_="instancename")
                title = title_elem.get_text(strip=True) if title_elem else "Untitled Activity"
                
                # Only include if it's an activity (usually numbered like "Activity 1.1")
                if re.search(r'Activity\s+\d+\.\d+', title):
                    activity_type = "forum" if "hsuforum" in href else "assignment"
                    activities.append({
                        "title": title,
                        "url": href,
                        "type": activity_type
                    })
    
    # Sort activities by their numbers (e.g., "Activity 1.1" comes before "Activity 1.2")
    activities.sort(key=lambda x: [int(n) for n in re.findall(r'\d+', x['title'])])
    return activities

def extract_forum_content(session, url):
    """Extracts content specifically from forum activities."""
    response = session.get(url)
    if response.status_code != 200:
        return "Failed to fetch forum content."
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Get the forum description
    forum_desc = soup.find("div", class_="hsuforum-description") or \
                 soup.find("div", class_="instructions") or \
                 soup.find("div", class_="content")
    
    return str(forum_desc) if forum_desc else "No forum content found."

def extract_assignment_content(session, url):
    """Extracts content specifically from assignment activities."""
    response = session.get(url)
    if response.status_code != 200:
        return "Failed to fetch assignment content."
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Get the assignment description
    assign_desc = soup.find("div", class_="assignmenttext") or \
                 soup.find("div", class_="description")
    
    if assign_desc:
        # Remove submission status and other non-description elements
        for div in assign_desc.find_all(["div", "table"], class_=["submissionstatustable", "gradingsummary"]):
            div.decompose()
        return str(assign_desc)
    
    return "No assignment content found."

def extract_section_html(session, course_id, section_num):
    """Extracts content from a specific section."""
    course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}"
    response = session.get(course_url)
    
    if response.status_code != 200:
        return None, []
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the specific section
    section = soup.find("li", id=f"section-{section_num}")
    if not section:
        return None, []
        
    # Get the main section content
    content_div = section.find("div", class_="NextGen4")
    section_html = str(content_div) if content_div else ""
    
    # Find all activities in this section
    activities = find_activity_links(section)
    
    return section_html, activities

def main():
    st.title("Moodle Section and Activity Extractor")
    
    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", "33234")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button:
        st.write("Logging in and extracting content...")
        session = requests.Session()
        login_successful = login_to_moodle(session, username, password)
        
        if not login_successful:
            return
        
        html_output = ""
        for week_num in range(1, 4):  # Weeks 1-3
            section_name = f"Week {week_num}"
            st.write(f"Processing {section_name}...")
            
            # Get section content and activities
            section_html, activities = extract_section_html(session, course_id, week_num)
            
            if section_html is None:
                st.error(f"Failed to extract content for {section_name}")
                continue
                
            # Start building this section's HTML
            html_output += f"<h2>{section_name}</h2>\n"
            html_output += f"<div class='section-content'>{section_html}</div>\n"
            
            # Process each activity
            for activity in activities:
                st.write(f"Extracting {activity['title']}")
                
                # Extract content based on activity type
                if activity['type'] == 'forum':
                    content = extract_forum_content(session, activity['url'])
                else:  # assignment
                    content = extract_assignment_content(session, activity['url'])
                
                html_output += f"""
                <h3>{activity['title']}</h3>
                <div class='activity-content'>
                    {content}
                </div>
                """
        
        # Provide downloadable HTML file
        if html_output:
            st.download_button(
                label="Download Content",
                data=html_output,
                file_name="course_content.html",
                mime="text/html"
            )
        else:
            st.error("No content was extracted.")

if __name__ == "__main__":
    main()

```

Key changes made:

1. Added `find_activity_links()` function that:
   - Uses regex patterns to find all forum and assignment URLs in a section
   - Specifically looks for titles containing "Activity X.Y" format
   - Sorts activities by their numbers

2. Improved URL detection:
   - Now finds all URLs matching the forum/assignment patterns
   - Doesn't rely on specific IDs
   - Handles both types of activities (forum and assignment)

3. Better activity filtering:
   - Only includes links that are actually activities (with "Activity X.Y" in the title)
   - Sorts them in numerical order
   - Properly identifies activity types from URLs

4. Enhanced error handling:
   - Better feedback when sections or activities aren't found
   - Clearer progress indicators

Would you like me to make any adjustments to how the activities are detected or processed?
