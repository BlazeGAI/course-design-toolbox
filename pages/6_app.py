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

        if text.startswith("Week"):  # Section identifier
            current_section = {"section": text, "resources": []}
            course_structure.append(current_section)
        elif text and current_section is not None:
            current_section["resources"].append(text)

    return course_structure

def scrape_live_content(session, url, selectors):
    """
    Scrapes content from the Moodle course's live site.

    Args:
    - session: requests.Session() object for authenticated requests.
    - url: URL of the course section or activity to scrape.
    - selectors: A list of specific selectors to capture content accurately.
    """
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    content_texts = []

    for selector in selectors:
        elements = soup.find_all(selector["tag"], class_=selector.get("class")) if "class" in selector else soup.find_all(selector["tag"])
        content_texts.extend([element.get_text().strip() for element in elements])

    return "\n".join(content_texts)

def main():
    st.title("Moodle Scraping Tool")

    # Upload template document
    uploaded_template = st.file_uploader("Choose a course template", type=["docx"])

    # Collect credentials and URLs
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_url = st.text_input("Login URL", "https://moodle.example.com/login/index.php")  # Adjust to your Moodle structure
    base_url = st.text_input("Course Base URL", "https://moodle.example.com/course/view.php?id=123")  # Adjust default to your Moodle structure

    if uploaded_template is not None and username and password:
        # Parse the template
        course_structure = parse_template(uploaded_template)

        st.write("Course Structure:")

        content_output = []

        # Setup session
        session = requests.Session()

        # Login to Moodle platform
        session.post(login_url, data={"username": username, "password": password})

        for sec in course_structure:
            st.write(f"Section: {sec['section']}")
            content_output.append(f"Section: {sec['section']}")

            for res in sec['resources']:
                st.write(f"  - Resource: {res}")
                content_output.append(f"  - Resource: {res}")

                # Construct URL for resource scraping
                resource_url = f"{base_url}/section/{sec['section'].replace(' ', '').lower()}/{res.replace(' ', '').lower()}"
                # Modify selectors as needed to focus on specific content types
                selectors = [
                    {"tag": "p"},  # Paragraphs
                    {"tag": "div", "class": "content-class"},  # Specific content divs
                ]
                live_content = scrape_live_content(session, resource_url, selectors)

                # Include live content in output
                st.write(live_content)
                content_output.append(live_content)

            content_output.append("\n")

        # Save content to a text file
        text_file_content = "\n".join(content_output)
        st.download_button(label="Download as Text File", data=text_file_content, file_name="course_content.txt", mime="text/plain")


if __name__ == "__main__":
    main()
