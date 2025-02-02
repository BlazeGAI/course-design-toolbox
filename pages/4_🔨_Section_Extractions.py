import streamlit as st
import requests
from bs4 import BeautifulSoup
import time  # Import time module for sleep delays

st.set_page_config(page_title="Sections Extractor", page_icon="🔨")
st.title("Sections Extractor")
st.sidebar.header("Sections Extractor")
st.sidebar.write("This application extracts content from Moodle courses into an HTML file.")
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

LOGIN_URL = "https://online.tiffin.edu/login/index.php"

def login_to_moodle(session, username, password):
    """Logs into Moodle and maintains session authentication."""
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

def extract_section(session, course_id, target_section_id):
    """
    Extracts the title and content of a given section from the course page.
    Returns a tuple: (title, content).
    Attempts to locate the title in a header element (e.g., <h3 class="sectionname">).
    """
    course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}"
    response = session.get(course_url)
    if response.status_code != 200:
        return None, "<p>Failed to fetch course content.</p>"
    soup = BeautifulSoup(response.content, "html.parser")
    sections = soup.find_all("li", {"class": "section"})
    target_section = None
    for section in sections:
        section_id_attr = section.get("id", "")
        if section_id_attr == target_section_id:
            target_section = section
            break

    if target_section:
        # Try to extract the section title (Moodle might use <h3> or <h2> with class "sectionname")
        title_tag = target_section.find(["h3", "h2"], class_="sectionname")
        title = title_tag.get_text(strip=True) if title_tag else None

        # Extract the main content; the target div is assumed to be 'NextGen4'
        content_div = target_section.find("div", class_="NextGen4")
        if content_div:
            # Remove unwanted navigation elements.
            for nav in content_div.find_all("p", class_="Internal_Links"):
                nav.decompose()
            content_html = str(content_div)
            return title, content_html

    return None, f"<p>No content found for {target_section_id}.</p>"

def format_template(header_text, section_html):
    """Formats the extracted section content into an HTML template with an <h1> header."""
    template = f"""
    <h1>{header_text}</h1>
    {section_html}
    """
    return template

def main():
    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", placeholder="Enter the ID number from the course URL")
        section_choice = st.selectbox(
            "Select Section (optional)",
            options=["All Sections", "section-1", "section-2", "section-3", "section-4", "section-5", "section-6", "section-7"],
            index=0
        )
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not course_id:
            st.error("Please provide the Course ID.")
            return

        st.write("Logging in and extracting section content...")
        session = requests.Session()
        if not login_to_moodle(session, username, password):
            return

        # Pause for a few seconds to ensure the login session is fully established.
        st.write("Waiting a few seconds for the login process to complete...")
        time.sleep(3)

        html_output = ""
        if section_choice == "All Sections":
            file_name = f"course-{course_id}_all_sections.html"
            # Map week labels to section IDs.
            sections = {
                "Week 1": "section-1",
                "Week 2": "section-2",
                "Week 3": "section-3",
                "Week 4": "section-4",
                "Week 5": "section-5",
                "Week 6": "section-6",
                "Week 7": "section-7"
            }
            for week_label, sec_id in sections.items():
                st.write(f"Extracting content for {week_label} ({sec_id})")
                title, section_html = extract_section(session, course_id, sec_id)
                if title:
                    header_text = title
                else:
                    header_text = week_label
                formatted_section = format_template(header_text, section_html)
                html_output += formatted_section
        else:
            # Single section extraction.
            week_num = section_choice.split("-")[-1]
            title, section_html = extract_section(session, course_id, section_choice)
            if title:
                header_text = title
            else:
                header_text = f"Week {week_num}"
            file_name = f"course-{course_id}_week-{week_num}.html"
            formatted_section = format_template(header_text, section_html)
            html_output = formatted_section

        st.download_button(
            label="Download Extracted HTML",
            data=html_output,
            file_name=file_name,
            mime="text/html"
        )

if __name__ == "__main__":
    main()

st.markdown(
    """
## Using the Sections Extract
