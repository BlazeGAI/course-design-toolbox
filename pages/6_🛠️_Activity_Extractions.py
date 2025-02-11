import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(
page_title="Activity Extractor",
page_icon="🛠️",)
st.title("Activity Extractor")
st.sidebar.header("Activity Extractor")
st.sidebar.write(
    """This application application extracts the content from each activity in the course into an HTML file."""
    )
st.sidebar.image("https://i.imgur.com/BPN9akd.png", width=250)

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

def get_all_activities(session, course_id):
    """
    Fetches the Gradebook Setup page for `course_id`
    and returns a list of (activity_title, activity_url)
    by locating <a class="gradeitemheader"> links.
    """
    gradebook_url = f"https://online.tiffin.edu/grade/edit/tree/index.php?id={course_id}"
    response = session.get(gradebook_url)
    if response.status_code != 200:
        st.error("Failed to retrieve Gradebook Setup page.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Find ALL links with class="gradeitemheader"
    link_tags = soup.select("a.gradeitemheader")

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
        # If there's an issue fetching the page, return an empty string or None
        st.error(f"Failed to open activity URL: {activity_url}")
        return ""
    return response.text  # Full HTML as a string

def extract_nextgen4_content(html_content):
    """
    Using BeautifulSoup, parse the full activity HTML
    and extract only <div class="NextGen4 TU-activity-page">.
    
    You can optionally remove or modify any sub-elements here as needed.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    page_div = soup.find("div", class_="NextGen4 TU-activity-page")
    if not page_div:
        # Return a simple placeholder if there's no NextGen4 content
        return "<p>No NextGen4 TU-activity-page content found.</p>"
    
    # Example: remove <p class="Internal_Links"> blocks
    nav_elements = page_div.find_all("p", class_="Internal_Links")
    for nav in nav_elements:
        nav.decompose()

    # Return just the HTML for that specific div
    return str(page_div)

def main():

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", value="12345")
        submit_button = st.form_submit_button("Log in & Extract All Activities")

    if submit_button:
        session = requests.Session()

        st.write("Logging into Moodle...")
        if not login_to_moodle(session, username, password):
            st.stop()

        st.write("Login successful. Finding all activity links from Gradebook Setup...")
        activities = get_all_activities(session, course_id)

        if not activities:
            st.warning("No activities found or unable to parse the Gradebook Setup.")
            return

        st.success(f"Found {len(activities)} activity link(s). Extracting content...")

        combined_html = "<html>\n<head><meta charset='UTF-8'></head>\n<body>\n"
        combined_html += f"<h1>Extracted Activities for Course {course_id}</h1>\n"

        for idx, (title, url) in enumerate(activities, start=1):
            st.write(f"Fetching Activity {idx}: {title}")
            raw_html = get_activity_html(session, url)
            if not raw_html:
                # If fetch failed, skip
                continue

            # Extract only the NextGen4 content
            nextgen4_html = extract_nextgen4_content(raw_html)

            # Append to our combined HTML, prefixed by an H2 title
            combined_html += f"<h2>{title}</h2>\n{nextgen4_html}\n"

        combined_html += "</body>\n</html>"

        # Provide a download button for the user to save the combined HTML
        st.download_button(
            label="Download All Activities (HTML)",
            data=combined_html,
            file_name=f"course_{course_id}_activities.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
    
    st.markdown("""

    ## Using the Activity Extractor
    
    1. **Provide Credentials:**
       - Enter your Moodle **Username** and **Password** in the form.
    
    2. **Specify the Course ID:**
       - Enter the numeric Course ID (for example, 33234) in the **Course ID** field.
    
    3. **Extract Activities:**
       - Click **Log in & Extract All Activities**.
       - The application logs into Moodle and scans the Gradebook Setup page for all activity links.
    
    4. **Download the Consolidated File:**
       - After extraction, the application creates a single HTML file containing all activities.
       - Click **Download All Activities (HTML)** to save the file to your device.

    
    """)
