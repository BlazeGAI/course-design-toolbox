import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(
    page_title="HTML Merge to Moodle",
    page_icon="🎓",
)
st.title("HTML Merge to Moodle")
st.sidebar.header("HTML Merge to Moodle")
st.sidebar.write(
    """Once you have the HTML formatted correctly, this application will help you merge the Course Build Plan Final with the HTML code in Moodle."""
)
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

# Updated function to read HTML content from an uploaded file
def read_html_content(uploaded_file):
    return uploaded_file.getvalue().decode("utf-8")

# Your existing functions...
def extract_content_by_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    weeks_data = []

    weeks = soup.find_all('h1')
    for week in weeks:
        week_title = week.get_text(strip=True)

        # Initialize each content type
        content = {
            'week': week_title, 
            'overview': '', 
            'learning_goals': '', 
            'key_topics': '', 
            'resources': '', 
            'significance': '', 
            'whats_next': ''
        }

        # Find the next <h3> and <h4> tags
        overview_tag = week.find_next('h3')
        learning_goals_tag = overview_tag.find_next('h4') if overview_tag else None
        key_topics_tag = learning_goals_tag.find_next('h4') if learning_goals_tag else None
        resources_tag = key_topics_tag.find_next('h4') if key_topics_tag else None
        significance_tag = resources_tag.find_next('h4') if resources_tag else None
        whats_next_tag = significance_tag.find_next('h4') if significance_tag else None

        # Extract content for each section
        content['overview'] = extract_section_content(overview_tag, ['h3', 'h4', 'h1'])
        content['learning_goals'] = extract_section_content(learning_goals_tag, ['h4', 'h1'])
        content['key_topics'] = extract_section_content(key_topics_tag, ['h4', 'h1'])
        content['resources'] = extract_section_content(resources_tag, ['h4', 'h1'])
        content['significance'] = extract_section_content(significance_tag, ['h4', 'h1'])
        content['whats_next'] = extract_section_content(whats_next_tag, ['h1'])

        weeks_data.append(content)

    return weeks_data

def extract_section_content(tag, stop_tags):
    """Extract all content until a tag from stop_tags is encountered."""
    content = ''
    if tag:  # Check if tag is not None
        for sibling in tag.next_siblings:
            if sibling.name in stop_tags:
                break
            content += str(sibling)
    return content.strip()

def insert_content_into_template_string_manipulation(template_html, weeks_data):
    for i, week_data in enumerate(weeks_data, start=1):
        template_html = template_html.replace(f"[contentOverview{i}]", week_data['overview'])
        template_html = template_html.replace(f"[contentWLG{i}]", week_data['learning_goals'])
        template_html = template_html.replace(f"[contentTopics{i}]", week_data['key_topics'])
        template_html = template_html.replace(f"[contentResources{i}]", week_data['resources'])
        template_html = template_html.replace(f"[contentSignificance{i}]", week_data['significance'])
        template_html = template_html.replace(f"[contentWhatsNext{i}]", week_data['whats_next'])

    return template_html

# Streamlit UI for file upload
design_plan_file = st.file_uploader("Upload Course Build Plan File", key="design_plan")
template_file = st.file_uploader("Upload Moodle HTML Template File", key="template")

# Instructions and Links
st.markdown("""
This application will help you merge the Course Build Plan Final with the HTML code in Moodle. Upload the Course Build Plan Final after it has been converted to HTML and the headings have been formatted correctly. Then, upload the Moodle HTML Template.

**Step 1:** Upload your correctly formatted HTML Course Build Plan. (IMPORTANT: The headings must match the Course Build Template exactly)  
**Step 2:** Upload the Moodle HTML Template.  
**Step 3:** Click "Download Processed HTML"  
**Step 4:** Save the file.  
**Step 5:** Copy and paste the HTML into the Moodle course shell.

[Course Build Template](https://docs.google.com/document/d/1UF8XEIzQMhntWtXVRs0HcnAtfxznVijCI8j55ectKzI/edit?usp=sharing)

[Moodle HTML](https://drive.google.com/file/d/1EhHnYhfxOl7xRk6pP9iEcYZxU-uLOFbD/view?usp=sharing)
""")

if design_plan_file and template_file:
    design_plan_html = read_html_content(design_plan_file)
    template_html = read_html_content(template_file)

    weeks_data = extract_content_by_tags(design_plan_html)
    final_html = insert_content_into_template_string_manipulation(template_html, weeks_data)

    # Displaying the final HTML or providing a download link
    st.download_button(label="Download Processed HTML", data=final_html, file_name="processed_course.html", mime="text/html")

