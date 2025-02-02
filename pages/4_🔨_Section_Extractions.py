import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Sections Extractor",
    page_icon="🔨",
)
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

def extract_section_html(session, course_id, target_section_id):
    """Extracts content from a specific section using the course view page."""
    course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}"
    response = session.get(course_url)

    if response.status_code != 200:
        return "<p>Failed to fetch course content.</p>"

    soup = BeautifulSoup(response.content, "html.parser")
    sections = soup.find_all("li", {"class": "section"})

    target_section = None
    for section in sections:
        section_id_attr = section.get("id", "")
        if section_id_attr == target_section_id:
            target_section = section
            break

    if target_section:
        content = target_section.find("div", class_="NextGen4")
        if content:
            nav_elements = content.find_all("p", class_="Internal_Links")
            for nav in nav_elements:
                nav.decompose()
            return str(content)

    return f"<p>No content found for {target_section_id}.</p>"

def format_template(section_name, section_html):
    """Formats extracted section content into an HTML template."""
    template = f"""
    <h2>{section_name}</h2>
    {section_html}
    """
    return template

def main():
    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        mode = st.radio("Select extraction mode", ("All Sections", "Single Section"))
        course_id = st.text_input("Course ID", placeholder="Enter the ID number from the course URL")
        if mode == "Single Section":
            section_id = st.selectbox(
                "Select Section",
                options=["section-1", "section-2", "section-3", "section-4", "section-5", "section-6", "section-7"]
            )
        else:
            section_id = ""
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not course_id:
            st.error("Please provide the Course ID.")
            return

        st.write("Logging in and extracting section content...")
        session = requests.Session()
        if not login_to_moodle(session, username, password):
            return

        html_output = ""
        if mode == "All Sections":
            sections = {
                "Week 1": "section-1",
                "Week 2": "section-2",
                "Week 3": "section-3",
                "Week 4": "section-4",
                "Week 5": "section-5",
                "Week 6": "section-6",
                "Week 7": "section-7"
            }
            for section_name, sec_id in sections.items():
                st.write(f"Extracting content from {section_name} ({sec_id})")
                section_html = extract_section_html(session, course_id, sec_id)
                formatted_section = format_template(section_name, section_html)
                html_output += formatted_section
        else:
            st.write(f"Extracting content from {section_id}")
            section_html = extract_section_html(session, course_id, section_id)
            formatted_section = format_template(section_id, section_html)
            html_output = formatted_section

        st.download_button(
            label="Download Extracted HTML",
            data=html_output,
            file_name="sections_extraction.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()

st.markdown(
    """
## Using the Sections Extractor

1. **Enter Your Credentials:**
   - Provide your Moodle username and password.

2. **Select Extraction Mode:**
   - Choose **All Sections** to extract content from every section of a course.
   - Choose **Single Section** to extract content from one section only.

3. **Provide Required IDs:**
   - In both modes, enter the Course ID (from the course URL).
   - In **Single Section** mode, use the dropdown to select the specific section (e.g., section-1, section-2, etc.).

4. **Extract and Download:**
   - Click the **Submit** button.
   - After extraction, click the **Download Extracted HTML** button.
    """
)
