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
    """This tool is designed to help you format the headings in your Course Build Plan HTML doc to match the Moodle template's heading styles."""
)
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

def is_week_header(text):
    """
    Checks if the text starts with a week header pattern,
    e.g., "Week 1:" or "Week 1 -".
    """
    return re.match(r'^\s*Week\s+\d+\s*[:\-]', text, re.IGNORECASE) is not None

def format_html(design_html, template_html):
    design_soup = BeautifulSoup(design_html, 'html.parser')
    template_soup = BeautifulSoup(template_html, 'html.parser')

    # Create a mapping from heading text to heading tag (e.g., "Overview": "h3")
    template_headings = {
        tag.text.strip(): tag.name
        for tag in template_soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    }

    # Process candidate header tags in the design HTML. This includes <p> tags and any existing header tags.
    for tag in design_soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = tag.get_text(strip=True)
        if is_week_header(text):
            # Convert paragraphs starting with a week header to <h1>
            tag.name = 'h1'
        elif text in template_headings:
            # Convert elements with text matching the template heading to the designated tag.
            tag.name = template_headings[text]

    # Replace curly apostrophes with straight ones.
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
<h4>What&rsquo;s Next?</h4>
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
        st.error("Please upload or paste both HTML and the template.")

st.markdown("""
### Using the HTML Formatter

Once you have completed your plan in Google Docs or Word, you will need to convert your doc to HTML in order to begin processing it for Moodle. To convert your doc, it is suggested you use a converter like Word to HTML (https://wordhtml.com/). Feel free to nest your code but do not CLEAN it.
Then copy the HTML and save it to a file or paste it in the app.

Important! You will need to delete everything unrelated to the Moodle template that is not included in Weeks 1-7. In the Course Build Plan Final, this includes everything up until Week 1 (Title, Description, CLO, Points Distribution, etc.

1. **Upload Course Build Plan HTML File or Paste HTML**:
   - You will see a section titled "Upload Course Build Plan HTML File or Paste HTML".
   - You have two options here:
     - **Upload HTML File**: Click on "Upload HTML file" and select your HTML file from your computer. The file should be in `.html` format.
     - **Paste HTML**: Alternatively, you can directly paste your HTML content into the text area provided. You'll see a box where you can type or paste your HTML.

2. **Upload HTML Template or Paste Template**:
   - Next, you’ll see another section titled "Upload HTML Header Format Template or Paste Template".
   - Similar to the previous step, you can either upload an HTML template file or paste the HTML template content directly into the text area. NOTE: The default HTML might be outdated. Edit according to your plan.
   - This template will be used as a reference to format your HTML content.

3. **Format HTML**:
   - After uploading or pasting both your HTML content and the template, click the "Format HTML" button.
   - The tool will process your HTML and format it according to the template.

4. **Download Formatted HTML**:
   - Once the processing is complete, you will see a link to download the formatted HTML file.
   - Click on this link to download the file to your computer. The file will be named "HTML_Formatted_Headings.html".

### Tips for Success
- If you have headings different from the Moodle Course Shell, remove the headings and place them under one of the existing headings. Later, you will need to manually modify them to meet your desired styling.
- Ensure that the HTML template is correctly formatted before uploading or pasting it into the tool.
- If you encounter any errors or issues, double-check the HTML syntax and template structure on both the plan and the template. A missing bracket or slash can disrupt the processing.
- The tool is designed to work with standard HTML files. If your file has any unique or complex structures, the formatting may not be perfect. For example, if you use apostrophes, @ marks or symbols, it is suggested you add them later.
""")
