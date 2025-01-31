import streamlit as st
import requests
from bs4 import BeautifulSoup

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

def extract_activity_content(session, activity_url):
    """Extracts content from an individual activity page."""
    response = session.get(activity_url)
    if response.status_code != 200:
        return "Failed to fetch activity content."
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Look for common content containers in Moodle activities
    content = soup.find("div", class_="activity-content") or \
             soup.find("div", class_="hsuforum-content") or \
             soup.find("div", class_="content")
    
    return str(content) if content else "No content found for this activity."

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
    activity_links = target_section.find_all("a", class_="autolink")
    
    for link in activity_links:
        activity_title = link.get("title", "").strip()
        if activity_title.startswith("Activity"):
            activity_url = link.get("href")
            activities.append({
                "title": activity_title,
                "url": activity_url
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
                st.write(f"Extracting {activity['title']}")
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
