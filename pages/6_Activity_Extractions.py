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

    login_payload = {
        "username": username,
        "password": password
    }
    if logintoken:
        login_payload["logintoken"] = logintoken

    response = session.post(LOGIN_URL, data=login_payload)
    if "login" in response.url or "Invalid login" in response.text:
        st.error("Login failed! Check your credentials.")
        return False
    return True

def get_first_five_activities(session, course_id):
    """
    Fetches the Gradebook Setup page for `course_id`.
    Finds up to the first 5 <a class="gradeitemheader"> links.
    Returns a list of (title, url) tuples.
    """
    gradebook_url = f"https://online.tiffin.edu/grade/edit/tree/index.php?id={course_id}"
    response = session.get(gradebook_url)
    if response.status_code != 200:
        st.error("Failed to retrieve Gradebook Setup page.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Find up to the first 5 links with class="gradeitemheader"
    link_tags = soup.select("a.gradeitemheader")[:5]

    activities = []
    for link_tag in link_tags:
        title = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        if href:
            activities.append((title, href))

    return activities

def get_activity_html(session, activity_url):
    """Returns the raw HTML content of the given activity URL."""
    response = session.get(activity_url)
    if response.status_code != 200:
        st.error(f"Failed to open activity URL: {activity_url}")
        return None
    return response.text  # Full HTML as a string

def extract_nextgen4_content(html_content):
    """
    Using BeautifulSoup, parse the full activity HTML
    and extract only <div class="NextGen4 TU-activity-page">.

    You can remove or clean sub-elements if needed.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    page_div = soup.find("div", class_="NextGen4 TU-activity-page")
    if not page_div:
        return "<p>No NextGen4 TU-activity-page content found.</p>"

    # Example: remove <p class="Internal_Links"> blocks if present
    nav_elements = page_div.find_all("p", class_="Internal_Links")
    for nav in nav_elements:
        nav.decompose()

    return str(page_div)

def main():
    st.title("Moodle Top 5 Activities - NextGen4 Extractor")

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", value="33234")
        submit_button = st.form_submit_button("Log in & Extract")

    if submit_button:
        session = requests.Session()
        
        st.write("Logging into Moodle...")
        if not login_to_moodle(session, username, password):
            st.stop()

        st.write("Login successful. Finding up to the first 5 activities...")
        activities = get_first_five_activities(session, course_id)

        if not activities:
            st.warning("No activity links found or unable to parse Gradebook Setup.")
            return

        st.write(f"Found {len(activities)} activities. Extracting content...")

        combined_html = "<html><body>\n"
        for idx, (act_title, act_url) in enumerate(activities, start=1):
            st.write(f"Processing Activity {idx}: {act_title}")
            raw_html = get_activity_html(session, act_url)
            if raw_html:
                snippet = extract_nextgen4_content(raw_html)
                # Insert a heading with the activity title + snippet
                combined_html += f"<h2>{act_title}</h2>\n{snippet}\n<br><hr><br>\n"
        
        combined_html += "</body></html>"

        # Provide a download button with the combined HTML of the first five activities
        st.download_button(
            label="Download Extracted NextGen4 Content (HTML)",
            data=combined_html,
            file_name=f"course_{course_id}_activities_nextgen4.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
