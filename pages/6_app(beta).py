import streamlit as st
import requests
from bs4 import BeautifulSoup
from docx import Document

def parse_template(doc_file):
    """
    Parses a Word document template and returns a structured representation of the course.
    """
    doc = Document(doc_file)
    course_structure = []
    current_section = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("Week"):  
            current_section = {"section": text, "resources": []}
            course_structure.append(current_section)
        elif text and current_section is not None:
            current_section["resources"].append(text)

    return course_structure

def scrape_section_html(session, section_url):
    """
    Extracts the full HTML content from the 'Edit Section' page of a Moodle section.
    """
    response = session.get(section_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the "Edit Section" button or link (Modify based on Moodle's structure)
    edit_button = soup.find("a", string="Edit section")
    if edit_button:
        edit_section_url = edit_button["href"]
        edit_page = session.get(edit_section_url)
        edit_soup = BeautifulSoup(edit_page.content, "html.parser")

        # Locate the text editor where HTML is stored
        html_content_area = edit_soup.find("textarea", {"id": "id_summary"})
        if html_content_area:
            return html_content_area.text.strip()

    return "<p>No section content found.</p>"

def scrape_activity_html(session, activity_url):
    """
    Extracts the full HTML content of a Moodle activity.
    """
    response = session.get(activity_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract main content area (Modify based on Moodle's structure)
    content_area = soup.find("div", class_="activity-content")
    return str(content_area) if content_area else "<p>No activity content found.</p>"

def main():
    st.title("Moodle HTML Extractor")

    uploaded_template = st.file_uploader("Choose a course template", type=["docx"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_url = st.text_input("Login URL", "https://moodle.example.com/login/index.php")
    base_url = st.text_input("Course Base URL", "https://moodle.example.com/course/view.php?id=123")

    if uploaded_template is not None and username and password:
        course_structure = parse_template(uploaded_template)
        st.write("Extracting Moodle Content...")

        session = requests.Session()
        session.post(login_url, data={"username": username, "password": password})

        html_output = "<html><head><title>Course Content</title></head><body>"

        for sec in course_structure:
            section_name = sec['section']
            st.write(f"Extracting: {section_name}")

            section_url = f"{base_url}#section-{section_name.split()[-1]}"  # Adjust as needed
            section_html = scrape_section_html(session, section_url)

            html_output += f"<h2>{section_name}</h2>\n{section_html}\n"

            for res in sec['resources']:
                activity_url = f"{base_url}/mod/{res.replace(' ', '_').lower()}/view.php"
                activity_html = scrape_activity_html(session, activity_url)

                html_output += f"<h3>{res}</h3>\n{activity_html}\n"

        html_output += "</body></html>"

        # Download the extracted HTML content
        st.download_button(
            label="Download as HTML",
            data=html_output,
            file_name="course_content.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()
