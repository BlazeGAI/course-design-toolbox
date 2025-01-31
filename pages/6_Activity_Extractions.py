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

def get_first_activity_url(session, course_id):
    """
    Fetches the Gradebook Setup page for `course_id`.
    Looks for the first <a class="gradeitemheader">.
    Returns the URL if found, else None.
    """
    gradebook_url = f"https://online.tiffin.edu/grade/edit/tree/index.php?id={course_id}"
    response = session.get(gradebook_url)
    if response.status_code != 200:
        st.error("Failed to retrieve Gradebook Setup page.")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the first link with class "gradeitemheader"
    link_tag = soup.select_one("a.gradeitemheader")
    if link_tag:
        return link_tag.get("href")
    return None

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
    
    You can also clean or remove sub-elements here as needed.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the specific div
    page_div = soup.find("div", class_="NextGen4 TU-activity-page")
    if not page_div:
        return "<p>No NextGen4 TU-activity-page content found.</p>"
    
    # Optional: remove unwanted navigation or other elements
    # For example, removing <p class="Internal_Links"> blocks:
    nav_elements = page_div.find_all("p", class_="Internal_Links")
    for nav in nav_elements:
        nav.decompose()

    # Return just the HTML for that specific div
    return str(page_div)

def main():
    st.title("Moodle First-Activity NextGen4 Extractor")

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

        st.write("Login successful. Finding the first activity link...")
        first_activity_url = get_first_activity_url(session, course_id)

        if not first_activity_url:
            st.warning("No activity link found or unable to parse Gradebook Setup.")
            return

        st.write(f"First activity link found: {first_activity_url}")
        st.write("Extracting activity page HTML...")

        raw_html = get_activity_html(session, first_activity_url)
        if raw_html:
            st.success("Successfully retrieved the first activity's HTML.")
            
            # Now parse or clean the HTML, extracting only the NextGen4 TU-activity-page div
            cleaned_html = extract_nextgen4_content(raw_html)
            
            # Provide a download button for the user to save ONLY the extracted HTML portion
            st.download_button(
                label="Download NextGen4 HTML snippet",
                data=cleaned_html,
                file_name="activity_nextgen4_page.html",
                mime="text/html"
            )

if __name__ == "__main__":
    main()
