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

    return True  # Login successful

def extract_section_html(session, section_url):
    """Extracts content from <div class='NextGen4'> for each section."""
    response = session.get(section_url)

    if response.status_code != 200:
        return f"<p>Failed to fetch section content from {section_url}.</p>"

    soup = BeautifulSoup(response.content, "html.parser")
    section_content = soup.find("div", class_="NextGen4")

    return str(section_content) if section_content else "<p>No relevant content found.</p>"

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
        course_id = st.text_input("Course ID", "33234")  # Default course ID

        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.write("Logging in and extracting section content...")

        session = requests.Session()
        login_successful = login_to_moodle(session, username, password)

        if not login_successful:
            return

        html_output = ""

        # Extract content only for Sections 1 to 3
        sections = {
            "Week 1": f"https://online.tiffin.edu/course/view.php?id={course_id}#section-1",
            "Week 2": f"https://online.tiffin.edu/course/view.php?id={course_id}#section-2",
            "Week 3": f"https://online.tiffin.edu/course/view.php?id={course_id}#section-3"
        }

        for section_name, section_url in sections.items():
            st.write(f"Extracting section content from {section_name} ({section_url})")

            # Extract full section content
            section_html = extract_section_html(session, section_url)

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
