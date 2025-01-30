import streamlit as st
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://online.tiffin.edu/login/index.php"  # Hardcoded Moodle login page

def login_to_moodle(session, username, password):
    """Logs into Moodle and ensures session authentication persists."""
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.content, "html.parser")

    # Extract login token if required
    logintoken_tag = soup.find("input", {"name": "logintoken"})
    logintoken = logintoken_tag["value"] if logintoken_tag else None

    login_payload = {"username": username, "password": password}
    if logintoken:
        login_payload["logintoken"] = logintoken

    response = session.post(LOGIN_URL, data=login_payload)

    # Check if login was successful
    if "login" in response.url or "Invalid login" in response.text:
        st.error("Login failed! Check your credentials.")
        return False

    return True  # Login successful, session now stores authentication cookies

def extract_section_html(session, section_url):
    """Extracts content from <div class='NextGen4'> in each Moodle section."""
    response = session.get(section_url)

    if response.status_code != 200:
        return "<p>Failed to fetch section content.</p>"

    soup = BeautifulSoup(response.content, "html.parser")

    section_content = soup.find("div", class_="NextGen4")

    return str(section_content) if section_content else "<p>No relevant content found.</p>"

def extract_activities_html(session, section_url):
    """Extracts HTML for activities linked within a Moodle section."""
    response = session.get(section_url)

    if response.status_code != 200:
        return "<p>Failed to fetch activities.</p>"

    soup = BeautifulSoup(response.content, "html.parser")
    activities_html = ""

    activity_links = soup.find_all("a", class_="activity-title")

    for link in activity_links:
        activity_name = link.text.strip()
        activity_url = link.get("href")

        if activity_url:
            activity_html = scrape_activity_html(session, activity_url)
            activities_html += f"<h3>{activity_name}</h3>\n{activity_html}\n"

    return activities_html if activities_html else "<p>No activities found.</p>"

def scrape_activity_html(session, activity_url):
    """Extracts the full HTML content of a Moodle activity page."""
    response = session.get(activity_url)

    if response.status_code != 200:
        return "<p>Failed to fetch activity content.</p>"

    soup = BeautifulSoup(response.content, "html.parser")
    content_area = soup.find("div", class_="activity-content")

    return str(content_area) if content_area else "<p>No activity content found.</p>"

def main():
    st.title("Moodle Course HTML Extractor")

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        base_url = st.text_input("Course Base URL", "https://online.tiffin.edu/course/view.php?id=33234")
        
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.write("Logging in and extracting course content...")

        session = requests.Session()
        login_successful = login_to_moodle(session, username, password)

        if not login_successful:
            return

        html_output = "<html><head><title>Course Content</title></head><body>"

        for week in range(1, 15):  # Adjust for the number of weeks
            section_url = f"{base_url}#section-{week}"  # Correct format
            st.write(f"Extracting Week {week} from {section_url}")

            section_html = extract_section_html(session, section_url)
            activities_html = extract_activities_html(session, section_url)

            html_output += f"<h2>Week {week}</h2>\n{section_html}\n{activities_html}\n"

        html_output += "</body></html>"

        st.download_button(
            label="Download as HTML",
            data=html_output,
            file_name="course_content.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
