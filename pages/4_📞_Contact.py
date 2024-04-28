import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(
    page_title="Contact",
    page_icon="📞",
)
st.title("Contact")
st.sidebar.header("Contact")
st.write(
    """Get help by contacting GAI Support at gai@tiffin.edu"""
)
st.sidebar.image("https://i.imgur.com/PD23Zwd.png", width=250)

tawkto_iframe_html = """
<iframe src="https://tawk.to/chat/6594827c0ff6374032bb6e17/1hj61rdoe" 
        height="500" 
        width="682" 
        frameborder="0">
</iframe>
"""
# Embed the iframe in the Streamlit app
components.html(tawkto_iframe_html, height=520)


