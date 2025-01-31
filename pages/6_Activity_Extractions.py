import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

# Moodle login URL
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
    return True

def extract_activities_urls(session, course_id):
    """
    Fetches the Gradebook Setup page for `course_id` and returns
    a list of (activity_title, activity_url) tuples for each item
    found in the table.
    """
    gradebook_url = f"https://online.tiffin.edu/grade/edit/tree/index.php?id={course_id}"
    response = session.get(gradebook_url)
    if response.status_code != 200:
        st.error("Failed to retrieve Gradebook Setup page.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # The gradebook items are typically inside a table with id="gradetree" or similar.
    # We'll use CSS selectors to find links pointing to '/mod/...'
    # Adjust the selector to match your Moodle theme if needed.
    
    activity_rows = []
    # Example approach: find all <a> tags inside the gradebook table that have '/mod/' in href
    # This is a broad approach that should capture:
    #   https://online.tiffin.edu/mod/assign/view.php?id=123
    #   https://online.tiffin.edu/mod/hsuforum/view.php?id=456
    # etc.
    for link in soup.select("table#gradetree a"):
        href = link.get("href", "")
        if "/mod/" in href:  # we only want actual Moodle activities
            title = link.get_text(strip=True)
            activity_rows.append((title, href))

    return activity_rows

def main():
    st.title("Moodle Gradebook Activity Link Extractor")

    with st.form("moodle_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID", value="33234")
        submit_button = st.form_submit_button("Log in & Extract Links")

    if submit_button:
        # Create a Session to maintain cookies (logged-in state)
        session = requests.Session()

        st.write("Attempting to log in...")
        if not login_to_moodle(session, username, password):
            st.stop()  # Stop the script if login failed

        st.write("Login successful! Fetching activity URLs from Gradebook Setup...")
        activity_data = extract_activities_urls(session, course_id)

        if not activity_data:
            st.warning("No activities found or there was an error.")
        else:
            st.success(f"Found {len(activity_data)} items.")
            # Convert to DataFrame for nicer display
            df = pd.DataFrame(activity_data, columns=["Activity Title", "Activity URL"])
            st.dataframe(df)

            # Provide CSV download
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download activity links (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"course_{course_id}_activity_links.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
