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
    """Extracts content from <div class='NextGen4'> for a specific section."""
    # Use the proper URL format for accessing specific sections
    section_url = f"https://online.tiffin.edu/course/view.php?id={course_id}&section={section_num}"
    
    response = session.get(section_url)
    if response.status_code != 200:
        return f"<p>Failed to fetch section content from section {section_num}.</p>"
    
    soup = BeautifulSoup(response.content, "html.parser")
    # Find the specific section content
    section_content = soup.find("div", class_="NextGen4")
    return str(section_content) if section_content else f"<p>No content found in section {section_num}.</p>"

def format_template(section_name, section_html):
    """Formats extracted section content into the Moodle template."""
    template = f"""
    <h2>{section_name}</h2>
    {section_html}
    """
    return template

def main():
    st.title("Moodle Section Extractor")
    
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
        # Define sections to extract with their proper section numbers
        sections = {
            "Week 1": 1,
            "Week 2": 2,
            "Week 3": 3
        }
        
        for section_name, section_num in sections.items():
            st.write(f"Extracting content from {section_name} (Section {section_num})")
            # Extract section content using the section number
            section_html = extract_section_html(session, course_id, section_num)
            # Format content into Moodle template
            formatted_section = format_template(section_name, section_html)
            html_output += formatted_section
        
        # Provide downloadable HTML file
        st.download_button(
            label="Download Sections as HTML",
            data=html_output,
            file_name="sections_1_3_content.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
