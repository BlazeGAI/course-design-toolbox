import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

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

def extract_all_sections(session, course_id):
    """
    Downloads the full course page (with a timestamp to bypass caching) and
    returns a dictionary mapping section IDs to a tuple (title, content).
    """
    course_url = f"https://online.tiffin.edu/course/view.php?id={course_id}&_={int(time.time())}"
    response = session.get(course_url)
    if response.status_code != 200:
        st.error("Failed to fetch course content.")
        return {}
    soup = BeautifulSoup(response.content, "html.parser")
    sections = soup.find_all("li", {"class": "section"})
    results = {}
    for section in sections:
        section_id = section.get("id", "")
        if not section_id.startswith("section-"):
            continue
        # Extract title from header (if present)
        title_tag = section.find(["h3", "h2"], class_="sectionname")
        title = title_tag.get_text(strip=True) if title_tag else None
        # Extract the main content from the target div (assumed to be NextGen4)
        content_div = section.find("div", class_="NextGen4")
        if content_div:
            for nav in content_div.find_all("p", class_="Internal_Links"):
                nav.decompose()
            content_html = str(content_div)
        else:
            content_html = f"<p>No content found for {section_id}.</p>"
        results[section_id] = (title, content_html)
    return results

def format_template(header_text, section_html):
    """Formats the extracted section content into an HTML template with an <h1> header."""
    template = f"""
<h1>{header_text}</h1>
{section_html}
"""
    return template

def main():
    # Map week labels to corresponding section IDs.
    sections_options = {
        "Week 1": "section-1",
        "Week 2": "section-2",
        "Week 3": "section-3",
        "Week 4": "section-4",
        "Week 5": "section-5",
        "Week 6": "section-6",
        "Week 7": "section-7",
    }

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", placeholder="Enter the ID number from the course URL")
        selected_weeks = st.multiselect(
            "Select Sections",
            options=list(sections_options.keys()),
            default=list(sections_options.keys())
        )
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not course_id:
            st.error("Please provide the Course ID.")
            return

        if not selected_weeks:
            st.error("Please select at least one section.")
            return

        st.write("Logging in and extracting section content...")
        session = requests.Session()
        if not login_to_moodle(session, username, password):
            return

        st.write("Waiting a few seconds for the login process to complete...")
        time.sleep(3)

        # Download all sections once.
        all_sections = extract_all_sections(session, course_id)
        if not all_sections:
            st.error("No sections extracted.")
            return

        html_output = ""
        # Iterate over the selected weeks in the order given by sections_options.
        for week in selected_weeks:
            sec_id = sections_options[week]
            if sec_id in all_sections:
                title, content_html = all_sections[sec_id]
                header_text = title if title else week
                formatted_section = format_template(header_text, content_html)
                html_output += formatted_section

        # Decide file name based on selection.
        if len(selected_weeks) == len(sections_options):
            file_name = f"course-{course_id}_all_sections.html"
        elif len(selected_weeks) == 1:
            week = selected_weeks[0]
            file_name = f"course-{course_id}_week-{sections_options[week].split('-')[-1]}.html"
        else:
            file_name = f"course-{course_id}_custom_sections.html"

        st.download_button(
            label="Download Extracted HTML",
            data=html_output,
            file_name=file_name,
            mime="text/html"
        )

if __name__ == "__main__":
    main()

st.markdown(
"""\
## Using the Sections Extractor

1. **Enter Your Credentials:**
   - Provide your Moodle username and password.

2. **Provide the Course ID:**
   - Enter the Course ID from the course URL. This field is required.

3. **Select Sections:**
   - Use the multi‑select to choose one or more sections (weeks) to include.
   - By default, all sections are selected.

4. **Extract and Download:**
   - Click the **Submit** button.
   - After extraction, click the **Download Extracted HTML** button.
   - The file name reflects the Course ID and the sections included.
"""
)
