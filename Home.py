import streamlit as st

# Inject custom CSS
st.markdown(
    """
    <style>
    /* Remove top margin */
    .block-container {
        padding-top: 12rem;
    }
    /* Center-align title */
    .stTitle {
        text-align: center;
    }
    /* Align columns neatly */
    .stColumns > div {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    /* Style for the line separating sections */
    .section-divider {
        border: 1px solid #ddd;
        margin: 20px 0;
    }
    /* Center the image */
    .center-img {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create two columns
col1, col2 = st.columns(2)

# In the first column, display the image (use markdown with the center-img class for centering)
with col1:
    st.markdown("<div class='center-img'><img src='https://media.9curry.com/uploads/organization/image/928/eastcoastrailway.png' width='200'></div>", unsafe_allow_html=True)

# In the second column, display the text and center it using markdown
with col2:
    st.markdown("<h1 style='text-align: center;'>Vizianagaram Running Room</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Waltair Division</h3>", unsafe_allow_html=True)
