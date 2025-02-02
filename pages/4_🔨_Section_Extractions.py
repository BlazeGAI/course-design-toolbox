import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Sections Extractor", page_icon="🔨")
st.title("Sections Extractor")
st.sidebar.header("Sections Extractor")
st.sidebar.write("This application extracts the content from each week of the course into an HTML file.")
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

LOGIN_URL = "https://online.tiffin.edu/login/index.php"

def login_to_moodle(session, username, password):
    """Authenticate with Moodle and persist the session."""
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.content, "html.parser")
    logintoken_tag = soup.find("input", {"name": "logintoken"})
    logintoken = logintoken_tag["value"] if logintoken_tag else None

    login_payload = {"username": username, "password": password}
    if logintoken:
        login_payload["logintoken"] = logintoken

    response = session.post(LOGIN_URL, data=login_payload)
    if "login" in response.url or "Invalid login" in response.text:
        st.error("Login failed. Verify your credentials.")
        return False
    return True

def verify_page_loaded(soup):
    """
    Confirm that the course page has fully loaded by checking for section elements.
    Adjust this check if a more specific marker is available.
    """
    sections = soup.find_all("li", {"class": "section"})
    return bool(sections)

def extract_section_html(soup, section_num):
    """
    Extract content from a specified section within the provided BeautifulSoup object.
    Only sections with a NextGen4 container are processed.
    """
    sections = soup.find_all("li", {"class": "section"})
    target_section = None
    for section in sections:
        section_id = section.get("id", "")
        if f"section-{section_num}" in section_id:
            target_section = section
            break

    if target_section:
        content_div = target_section.find("div", class_="NextGen4")
        if content_div:
            nav_elements = content_div.find_all("p", class_="Internal_Links")
            for nav in nav_elements:
                nav.decompose()
            return str(content_div)
        else:
            return f"<p>Error: Section {section_num} does not include the required NextGen4 container.</p>"
    return f"<p>Error: No content found for section {section_num}.</p>"

def format_template(section_name, section_html):
    """Insert the section content into the HTML template."""
    template = f"""
<h2>{section_name}</h2>
{section_html}
"""
    return template

def main():
    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", "12345")
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.write("Logging in and retrieving course content.")
        session = requests.Session()
        if not login_to_moodle(session, username, password):
            return

        course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}"
        course_response = session.get(course_url)
        if course_response.status_code != 200:
            st.error("Failed to fetch course content.")
            return

        soup = BeautifulSoup(course_response.content, "html.parser")
        if not verify_page_loaded(soup):
            st.error("Course content has not fully loaded. Confirm that all dynamic content appears before extraction.")
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
            st.write(f"Extracting content from {section_name} (Section {section_num}).")
            section_html = extract_section_html(soup, section_num)
            formatted_section = format_template(section_name, section_html)
            html_output += formatted_section

        st.download_button(
            label="Download Sections as HTML",
            data=html_output,
            file_name="sections_extraction.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()

st.markdown("""
## Using the Sections Extractor

1. **Enter Your Credentials:**  
   Type your Moodle username and password into the provided fields.

2. **Provide the Course ID:**  
   Input the course ID in the designated field (e.g., 33234).

3. **Begin Extraction:**  
   Click the Submit button. The application logs in to Moodle and retrieves content from each weekly section.

4. **Download the Extracted File:**  
   After extraction, a Download Sections as HTML button appears. Click this button to download a single HTML file containing the selected sections.
""")
