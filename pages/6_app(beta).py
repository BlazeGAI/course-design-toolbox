import streamlit as st
import requests
from bs4 import BeautifulSoup

# Define the headings to extract
HEADINGS_TO_LOOK_FOR = [
    "Overview", "This Week's Learning Goals", "Key Topics for the Week", "Resources",
    "Significance", "What's Next?", "What’s Next?", "Introduction",
    "Initial Post Instructions (Due Wednesday)", "Follow-up Post Instructions (Due Saturday)",
    "Tips for Success", "Writing Requirements", "Weekly Learning Goal(s)",
    "Activity Instructions", "Writing and Submission Requirements"
]

def login_to_moodle(session, login_url, username, password):
    """Logs into Moodle using the provided session and credentials."""
    login_payload = {"username": username, "password": password}
    session.post(login_url, data=login_payload)

def extract_section_html(session, section_url):
    """Extracts relevant HTML content from a Moodle course section."""
    response = session.get(section_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Collect relevant headings and content
    extracted_html = ""
    for tag in soup.find_all(["h3", "h4"]):
        if tag.text.strip() in HEADINGS_TO_LOOK_FOR:
            extracted_html += f"<{tag.name}>{tag.text.strip()}</{tag.name}>\n"
            next_element = tag.find_next_sibling()
            while next_element and next_element.name not in ["h3", "h4"]:
                extracted_html += str(next_element) + "\n"
                next_element = next_element.find_next_sibling()

    return extracted_html if extracted_html else "<p>No relevant content found.</p>"

def extract_activities_html(session, section_url):
    """Extracts HTML for activities linked within a Moodle section."""
    response = session.get(section_url)
    soup = BeautifulSoup(response.content, "html.parser")

    activities_html = ""
    activity_links = soup.find_all("a", class_="activity-title")

    for link in activity_links:
        activity_name = link.text.strip()
        activity_url = link.get("href")

        if activity_url:
            activity_html = scrape_activity_html(session, activity_url)
            activities_html += f"<h3>{activity_name}</h3>\n{activity_html}\n"

    return activities_html

def scrape_activity_html(session, activity_url):
    """Extracts the full HTML content of a Moodle activity page."""
    response = session.get(activity_url)
    soup = BeautifulSoup(response.content, "html.parser")

    content_area = soup.find("div", class_="activity-content")
    return str(content_area) if content_area else "<p>No activity content found.</p>"

def main():
    st.title("Moodle Course HTML Extractor")

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_url = st.text_input("Login URL", "https://your-moodle-site.com/login/index.php")
        base_url = st.text_input("Course Base URL", "https://your-moodle-site.com/course/view.php?id=123")
        
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.write("Extracting Moodle Content...")

        session = requests.Session()
        login_to_moodle(session, login_url, username, password)

        html_output = "<html><head><title>Course Content</title></head><body>"

        for week in range(1, 15):  # Adjust for the number of weeks
            section_url = f"{base_url}#section-{week}"  
            st.write(f"Extracting Week {week}")

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
