import streamlit as st

# Custom CSS to style the layout and content
st.markdown(
    """
    <style>
    /* Adjust margins and padding */
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem; /* Add balanced side padding */
    }
    /* Center-align the title */
    # .stTitle {
    #     text-align: center;
    #     font-size: 2.5rem; /* Larger font for emphasis */
    #     color: #4CAF50; /* Professional green color */
    # }
    # /* Style for the description section */
    # .description {
    #     font-size: 1.2rem;
    #     line-height: 1.6;
    #     text-align: justify;
    #     color: #333333; /* Dark gray for readability */
    #     background-color: #f9f9f9; /* Light gray background for contrast */
    #     border: 1px solid #e0e0e0;
    #     border-radius: 8px;
    #     padding: 1.5rem;
    #     margin-top: 1rem;
    #     box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    # }
    # /* Style for the action button */
    # div.stButton > button {
    #     background-color: #4CAF50; /* Green background */
    #     color: white; /* White text */
    #     border: none;
    #     border-radius: 8px;
    #     padding: 0.7rem 1.5rem;
    #     font-size: 1rem;
    #     font-weight: bold;
    #     cursor: pointer;
    #     transition: 0.3s;
    # }
    # div.stButton > button:hover {
    #     background-color: #45a049; /* Darker green on hover */
    # }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Title
st.title("Running Room Dashboard 🔍")

# Description Section
st.write(
    """
    <div class="description">
        <p><strong>Welcome to the Room Booking Platform for Running Rooms</strong>, developed by <em>East Coast Railway, Waltair Division</em>. This platform is designed to offer a seamless and efficient lodging experience for crew members and officials. It streamlines the booking process while catering to their specific needs.</p>
        <p>Equipped with advanced functionalities, the system enables real-time monitoring of bed availability and minimizes waiting times, ensuring timely rest for the crew. Transitioning from manual calculations, the software now proficiently automates key metrics, including:</p>
        <ul>
            <li>Crew counts by HQ</li>
            <li>Running room rest durations</li>
            <li>Meal consumption tracking</li>
            <li>Bedsheet and blanket utilization</li>
            <li>Peak occupancy analysis for any specified period</li>
        </ul>
        <p>This system is designed to enhance operational efficiency and support effective management.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Action Button
st.markdown("### Actions:")

col1,col2 = st.columns(2)
with col1:
    x = st.page_link( "Report_1.py",label="Meals Report",icon= "🍽️")
    x = st.page_link( "Report_2.py",label="Lenin Report",icon= "🛏️")

with col2:
    x = st.page_link( "Report_4.py",label="Rest Report",icon= "📊")
    x = st.page_link( "Report_5.py",label="Peak Occupation",icon= "📄")

