import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

LOGIN_URL = "https://online.tiffin.edu/login/index.php"

def login_to_moodle(session, username, password):
    try:
        login_page = session.get(LOGIN_URL)
        soup = BeautifulSoup(login_page.content, "html.parser")
        
        # Get login token
        logintoken_tag = soup.find("input", {"name": "logintoken"})
        logintoken = logintoken_tag["value"] if logintoken_tag else None
        
        # Prepare login data
        login_data = {
            "username": username,
            "password": password,
            "logintoken": logintoken
        }
        
        # Attempt login
        response = session.post(LOGIN_URL, data=login_data)
        
        # Check login success
        if "login" in response.url or "Invalid login" in response.text:
            st.error("Login failed. Please check your credentials.")
            return False
        return True
        
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def extract_section_html(session, course_id, section_number):
    try:
        url = f"https://online.tiffin.edu/course/view.php?id={course_id}&section={section_number}"
        response = session.get(url)
        
        # Check if session is still valid
        if "login" in response.url:
            st.warning("Session expired. Please log in again.")
            return None
            
        if response.status_code != 200:
            st.error(f"Failed to fetch section {section_number}")
            return None
            
        soup = BeautifulSoup(response.content, "html.parser")
        section_content = soup.find("div", class_="NextGen4")
        
        if not section_content:
            st.warning(f"No content found in section {section_number}")
            return None
            
        return str(section_content)
        
    except Exception as e:
        st.error(f"Error extracting section {section_number}: {str(e)}")
        return None

def format_html_content(section_name, content):
    if not content:
        return ""
        
    return f"""
    <div class="section-container">
        <h2>{section_name}</h2>
        {content}
    </div>
    """

def main():
    st.title("Moodle Content Extractor")
    
    # Create form for user input
    with st.form("moodle_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        course_id = st.text_input("Course ID")
        submit = st.form_submit_button("Extract Content")
    
    if submit:
        if not all([username, password, course_id]):
            st.error("Please fill in all fields")
            return
            
        # Initialize session
        session = requests.Session()
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Login
        status_text.text("Logging in...")
        if not login_to_moodle(session, username, password):
            return
            
        # Extract content
        status_text.text("Extracting content...")
        all_content = ""
        sections = {
            "Week 1": 1,
            "Week 2": 2,
            "Week 3": 3
        }
        
        for index, (week_name, section_num) in enumerate(sections.items()):
            progress_bar.progress((index + 1) / len(sections))
            status_text.text(f"Processing {week_name}...")
            
            # Add delay to prevent server overload
            time.sleep(1)
            
            content = extract_section_html(session, course_id, section_num)
            if content:
                all_content += format_html_content(week_name, content)
        
        if all_content:
            # Add CSS for better formatting
            final_html = f"""
            <html>
            <head>
                <style>
                    .section-container {{
                        margin: 20px 0;
                        padding: 15px;
                        border: 1px solid #ddd;
                    }}
                    h2 {{
                        color: #2c3e50;
                        border-bottom: 2px solid #eee;
                        padding-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                {all_content}
            </body>
            </html>
            """
            
            # Offer download
            st.download_button(
                label="Download Content",
                data=final_html,
                file_name="moodle_content.html",
                mime="text/html"
            )
            
            status_text.text("Content extraction complete!")
            progress_bar.progress(100)
        else:
            st.error("No content was extracted. Please check the course ID and try again.")

if __name__ == "__main__":
    main()
