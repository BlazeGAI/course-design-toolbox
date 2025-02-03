import streamlit as st
from bs4 import BeautifulSoup
import base64
import re

st.set_page_config(
    page_title="Format HTML Headings",
    page_icon="🔠",
)

st.title("Format HTML Headings")
st.sidebar.header("Format HTML Headings")
st.sidebar.write(
    """This tool formats the headings in your Course Build Plan HTML document to match the Moodle template."""
)
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

def normalize_text(text):
    """
    Normalizes text by replacing curly quotes with straight ones,
    converting to lower case, and trimming whitespace.
    """
    text = text.replace('‘', "'").replace('’', "'")
    return text.strip().lower()

def is_week_header(text):
    """
    Checks if the text starts with a week header pattern,
    e.g., "Week 1:" or "Week 1 -".
    """
    return re.match(r'^\s*week\s+\d+\s*[:\-]', text, re.IGNORECASE) is not None

def format_html(design_html, template_html):
    design_soup = BeautifulSoup(design_html, 'html.parser')
    template_soup = BeautifulSoup(template_html, 'html.parser')

    # Build a dictionary mapping normalized heading text to the desired tag name.
    template_headings = {
        normalize_text(tag.get_text()): tag.name
        for tag in template_soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    }

    # Process <p> tags and any header tags in the design HTML.
    for tag in design_soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = tag.get_text(strip=True)
        norm_text = normalize_text(text)
        if is_week_header(norm_text):
            tag.name = 'h1'
        elif norm_text in template_headings:
            tag.name = template_headings[norm_text]

    # After processing, replace any remaining curly apostrophes with straight ones.
    formatted_html = str(design_soup).replace('‘', "'").replace('’', "'")
    return formatted_html

def get_html_download_link(html, filename):
    b64 = base64.b64encode(html.encode()).decode()
    href = f'<a href="data:file/html;base64,{b64}" download="{filename}">Download formatted HTML file</a>'
    return href

def process_html(uploaded_html, html_text):
    if uploaded_html is not None:
        return uploaded_html.getvalue().decode("utf-8")
    else:
        return html_text

def process_template(uploaded_template, template_text):
    if uploaded_template is not None:
        return uploaded_template.getvalue().decode("utf-8")
    else:
        return template_text

# HTML upload or input
uploaded_html = st.file_uploader("Upload Course Build Plan HTML file", type=['html'])
html_text = st.text_area("Or paste HTML here", height=150)

# Template upload or input
default_template = """
 <h3>Overview</h3>
<h4>This Week's Learning Goals</h4>
<h4>Key Topics for the Week</h4>
<h4>Resources</h4>
<h4>Significance</h4>
<h4>What's Next?</h4>
<h3>Introduction</h3>
<h3>Initial Post Instructions (Due Wednesday)</h3>
<h3>Follow-up Post Instructions (Due Saturday)</h3>
<h3>Tips for Success</h3>
<h3>Writing Requirements</h3>
<h3>Weekly Learning Goal(s)</h3>
<h3>Introduction</h3>
<h3>Activity Instructions</h3>
<h3>Tips for Success</h3>
<h3>Writing and Submission Requirements</h3>
<h3>Weekly Learning Goal(s)</h3>
"""
uploaded_template = st.file_uploader("Upload HTML Header Format Template", type=['html'])
template_text = st.text_area("Or paste HTML template here", value=default_template, height=150)

if st.button("Format HTML"):
    design_html = process_html(uploaded_html, html_text)
    template_html = process_template(uploaded_template, template_text)
    
    if design_html and template_html:
        formatted_html = format_html(design_html, template_html)
        st.markdown(get_html_download_link(formatted_html, "HTML_Formatted_Headings.html"), unsafe_allow_html=True)
    else:
        st.error("Please upload or paste both the HTML content and the template.")

st.markdown("""
### Using the HTML Formatter

Once you have completed your plan in Google Docs or Word, convert your document to HTML before processing it for Moodle. You can use a converter such as Word to HTML (https://wordhtml.com/). Save or paste the HTML content into the tool.

1. **Upload or Paste HTML Content**:
   - Use the provided section to either upload an HTML file or paste the HTML content.

2. **Upload or Paste the HTML Template**:
   - Use the provided section to either upload the HTML header format template or paste its content.
   - Ensure the template is formatted correctly. Edit if necessary.

3. **Format HTML**:
   - Click the "Format HTML" button to process the HTML according to the template rules.
   - The tool converts week headers (e.g., "Week 1:" or "Week 1 -") into `<h1>` tags and matches other headings based on the template.

4. **Download Formatted HTML**:
   - Click the provided download link to retrieve the formatted HTML file.
""")
