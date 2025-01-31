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

def extract_section_html(session, course_id, section_num):
    """Extracts content from a specific section using a direct course view."""
    # First, get the main course page
    course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}"
    response = session.get(course_url)
    
    if response.status_code != 200:
        return f"<p>Failed to fetch course content.</p>"
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all sections
    sections = soup.find_all("li", {"class": "section"})
    
    # Find the specific section we want
    target_section = None
    for section in sections:
        section_id = section.get("id", "")
        if f"section-{section_num}" in section_id:
            target_section = section
            break
    
    if target_section:
        # Find the NextGen4 div within this section
        content = target_section.find("div", class_="NextGen4")
        if content:
            # Clean up the content by removing any unwanted elements
            # Remove navigation elements that might cause confusion
            nav_elements = content.find_all("p", class_="Internal_Links")
            for nav in nav_elements:
                nav.decompose()
            
            return str(content)
    
    return f"<p>No content found for section {section_num}.</p>"

def format_template(section_name, section_html):
    """Formats extracted section content into the template."""
    template = f"""
    <h2>{section_name}</h2>
    {section_html}
    """
    return template

def main():
    st.title("Section Extractor")
    
    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", "33234")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button:
        st.write("Logging in and extracting section content...")
        session = requests.Session()
        login_successful = login_to_moodle(session, username, password)
        
        if not login_successful:
            return
        
        html_output = ""
        sections = {
            "Week 1": 1,
            "Week 2": 2,
            "Week 3": 3,
            "Week 4": 4,
            "Week 5": 5,
            "Week 6": 6,
            "Week 7": 7
        }
        
        for section_name, section_num in sections.items():
            st.write(f"Extracting content from {section_name} (Section {section_num})")
            # Extract section content
            section_html = extract_section_html(session, course_id, section_num)
            # Format content into template
            formatted_section = format_template(section_name, section_html)
            html_output += formatted_section
        
        # Provide downloadable HTML file
        st.download_button(
            label="Download Sections as HTML",
            data=html_output,
            file_name="sections_extraction.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
