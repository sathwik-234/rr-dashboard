import streamlit as st

st.markdown(
    """
    <style>
    /* Remove top margin */
    .block-container {
        padding-top: 1rem;
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
    </style>
    """,
    unsafe_allow_html=True,
)


nav = st.navigation([st.Page("Home.py",title="Home"),st.Page("Report_1.py",title="Meals Report 🍴"),st.Page("Report_2.py",title="Lenin Report 🛌"),st.Page("Report_4.py",title ="Rest Report 📊"),st.Page("Report_5.py",title = "Peak Occupation 📝")])
nav.run()