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
    /* Style for the line separating sections */
    .section-divider {
        border: 1px solid #ddd;
        margin: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = {
    "Home":[
        st.Page("Home.py", title="Home"),
    ],
    "Reports": [
        st.Page("Report_1.py", title="Meals Report 🍴"),
        st.Page("Report_2.py", title="Lenin Report 🛌"),
        st.Page("Report_4.py", title="Rest Report 📊"),
        st.Page("Report_5.py", title="Peak Occupation 📝"),
    ],
    "Operations": [
        st.Page("RoomHolding.py",title="Room Holding 🚪"),
        st.Page("TOtime.py",title="Outgoing TO Time Allocation⏲️")
    ],
}

nav = st.navigation(pages=pages)
nav.run()
