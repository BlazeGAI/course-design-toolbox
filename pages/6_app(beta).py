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
        return "<p>Failed to fetch section content.</p>"

    soup = BeautifulSoup(response.content, "html.parser")

    section_content = soup.find("div", class_="NextGen4")

    return str(section_content) if section_content else "<p>No relevant content found.</p>"

def extract_activity_links(session, section_url):
    """Finds required activity links in a section, stopping at <h3>Wrap-Up</h3>."""
    response = session.get(section_url)

    if response.status_code != 200:
        return set()

    soup = BeautifulSoup(response.content, "html.parser")
    activity_links = set()

    wrap_up_found = False

    for element in soup.find_all(["h3", "a"]):  # Find all headers and activity links
        if element.name == "h3" and element.text.strip() == "Wrap-Up":
            wrap_up_found = True
            break  # Stop extracting activities once Wrap-Up is found

        if element.name == "a" and "href" in element.attrs:
            url = element["href"]
            if "/mod/hsuforum/view.php?id=" in url or "/mod/assign/view.php?id=" in url:
                activity_links.add(url)

    return activity_links

def extract_activity_html(session, activity_url):
    """Extracts HTML from <div class='NextGen4 TU-activity-page'> in an activity page."""
    response = session.get(activity_url)

    if response.status_code != 200:
        return "<p>Failed to fetch activity content.</p>"

    soup = BeautifulSoup(response.content, "html.parser")
    activity_content = soup.find("div", class_="NextGen4 TU-activity-page")

    return str(activity_content) if activity_content else "<p>No activity content found.</p>"

def format_template(section_name, section_html, activities_html):
    """Formats extracted content into the Moodle template."""
    template = f"""
    <h2>{section_name}</h2>
    <div class="NextGen4">
        {section_html}
    </div>
    
    {activities_html}
    """
    return template

def main():
    st.title("Moodle Course Extractor")

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", "475074")  # Default example ID

        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.write("Logging in and extracting section content and activities...")

        session = requests.Session()
        login_successful = login_to_moodle(session, username, password)

        if not login_successful:
            return

        html_output = ""

        # Extract full section content + activities for "Start Here" and "Week 1"
        sections = {
            "Start Here": "0",
            "Week 1": "1"
        }

        base_url = f"https://online.tiffin.edu/course/section.php?id={course_id}"

        for section_name, section_id in sections.items():
            section_url = f"{base_url}#section-{section_id}"
            st.write(f"Extracting section and activities from {section_name} ({section_url})")

            # Extract full section content
            section_html = extract_section_html(session, section_url)

            # Extract activity links (stopping at Wrap-Up)
            activity_links = extract_activity_links(session, section_url)
            activities_html = ""

            for activity_url in activity_links:
                st.write(f"Extracting activity from {activity_url}")
                activity_html = extract_activity_html(session, activity_url)
                activities_html += f"<h3>Activity</h3>\n{activity_html}\n"

            # Format content into Moodle template
            formatted_section = format_template(section_name, section_html, activities_html)
            html_output += formatted_section

        # Provide downloadable HTML file
        st.download_button(
            label="Download Content as HTML",
            data=html_output,
            file_name="course_content.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
