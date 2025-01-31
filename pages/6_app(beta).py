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

def extract_forum_content(session, url):
    """Extracts content specifically from forum activities."""
    response = session.get(url)
    if response.status_code != 200:
        return "Failed to fetch forum content."
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the forum description/introduction
    intro = soup.find("div", class_="hsuforum-intro")
    intro_html = str(intro) if intro else ""
    
    # Find the forum prompt/description
    description = soup.find("div", class_="hsuforum-description")
    description_html = str(description) if description else ""
    
    return f"{intro_html}\n{description_html}"

def extract_assignment_content(session, url):
    """Extracts content specifically from assignment activities."""
    response = session.get(url)
    if response.status_code != 200:
        return "Failed to fetch assignment content."
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the assignment description
    description = soup.find("div", class_="description")
    if description:
        # Remove any submission status or grade information
        for div in description.find_all("div", class_=["submissionstatustable", "gradingsummary"]):
            div.decompose()
        return str(description)
    
    return "No assignment content found."

def extract_activity_content(session, url):
    """Extracts content based on activity type."""
    if "hsuforum" in url:
        return extract_forum_content(session, url)
    elif "assign" in url:
        return extract_assignment_content(session, url)
    else:
        return "Unsupported activity type."

def extract_section_content(session, course_id, section_num):
    """Extracts section content and its activities."""
    course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}"
    response = session.get(course_url)
    
    if response.status_code != 200:
        return "<p>Failed to fetch course content.</p>", []
    
    soup = BeautifulSoup(response.content, "html.parser")
    sections = soup.find_all("li", {"class": "section"})
    
    # Find the specific section
    target_section = None
    for section in sections:
        section_id = section.get("id", "")
        if f"section-{section_num}" in section_id:
            target_section = section
            break
    
    if not target_section:
        return f"<p>No content found for section {section_num}.</p>", []
    
    # Extract main section content
    section_content = target_section.find("div", class_="NextGen4")
    section_html = str(section_content) if section_content else ""
    
    # Extract activities
    activities = []
    activity_elements = target_section.find_all(class_="activity")
    
    for activity in activity_elements:
        # Find activity link and title
        link = activity.find("a", href=re.compile(r"mod/(hsuforum|assign)/view\.php"))
        if link:
            activity_url = link.get("href")
            # Try to find the activity title in different possible locations
            title_elem = activity.find("span", class_="instancename") or activity.find("h4", class_="instancename")
            activity_title = title_elem.get_text(strip=True) if title_elem else "Untitled Activity"
            
            if "Activity" in activity_title:
                activities.append({
                    "title": activity_title,
                    "url": activity_url,
                    "type": "forum" if "hsuforum" in activity_url else "assignment"
                })
    
    return section_html, activities

def format_template(section_name, section_html, activities_content):
    """Formats extracted section and activity content into the template."""
    template = f"""
    <h2>{section_name}</h2>
    <div class="section-content">
        {section_html}
    </div>
    <div class="activities-content">
        {activities_content}
    </div>
    """
    return template

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
        sections = {
            "Week 1": 1,
            "Week 2": 2,
            "Week 3": 3
        }
        
        for section_name, section_num in sections.items():
            st.write(f"Extracting content from {section_name} (Section {section_num})")
            
            # Extract section content and activities
            section_html, activities = extract_section_content(session, course_id, section_num)
            
            # Extract content for each activity
            activities_html = ""
            for activity in activities:
                st.write(f"Extracting {activity['title']} ({activity['type']})")
                activity_content = extract_activity_content(session, activity['url'])
                activities_html += f"""
                <h3>{activity['title']}</h3>
                <div class="activity-content">
                    {activity_content}
                </div>
                """
            
            # Format content into template
            formatted_section = format_template(section_name, section_html, activities_html)
            html_output += formatted_section
        
        # Provide downloadable HTML file
        st.download_button(
            label="Download Sections and Activities as HTML",
            data=html_output,
            file_name="sections_and_activities_content.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
