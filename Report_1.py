import streamlit as st
import datetime as dt
import pandas as pd
from supabaseClient import supabase as sp
import pdf_reports as pdf  # This imports your custom PDF generation code

# Set up the page layout
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
    }
    .stTitle {
        text-align: center;
    }
    .stColumns > div {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Page Title
st.title("Meals Report 🍴")
st.markdown("---")  # Horizontal divider for neatness
st.write(f"**📅 Today's Date:** {dt.datetime.now().date().strftime('%d/%m/%Y')}")

# Inputs Section
st.markdown("### 🛠 Inputs:")
col1, col2, col3 = st.columns(3)

with col1:
    today = dt.datetime.now().date()
    ten_days_before = today - dt.timedelta(days=10)
    date_range = st.date_input(
        "🗓 Time Range:",
        (ten_days_before, today)
    )
st.markdown("---")

# Handle submission
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if st.button("🚀 Submit"):
    st.session_state.submitted = True

if st.session_state.submitted:
    try:
        # Convert dates to strings for querying
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")

        # Fetch data from the database
        with st.spinner("Fetching data..."):
            query = sp.from_("CheckOut").select("*,Crew(*),CheckIn(*)").gte("out_time", start_date).lte("out_time", end_date)
            response = query.execute()

        # Process the response
        if response.data:
            data = response.data
        else:
            st.error("Failed to fetch data. Check your query or database connection.")
            st.stop()

        # Display the data
        if data and len(data) > 0:
            st.write(f"### 📊 Meals Report ")
            df = pd.DataFrame(data)
            crew_data = df["Crew"]
            checkin_data = df["CheckIn"]
            df.drop(columns=["id", "created_at", "out_train_no", "cleanliness", "service", "overall", "comfort", "Crew", "CheckIn","check_in_id"], inplace=True)
            df.insert(1, "crew_name", [crew["crewname"] for crew in crew_data], True)
            df.insert(2, "checkin_time", [checkin["ic_time"] for checkin in checkin_data], True)
            
            df.rename(columns={"cms_id": "CMS ID", "crew_name": "Crew Name", "checkin_time": "CheckIn Time", "out_time": "CheckOut Time", "breakfast": "Breakfast", "lunch": "Lunch", "dinner": "Dinner", "parcel": "Parcel","allotted_bed" : "Bed"}, inplace=True)
            st.dataframe(df)
            # Generate PDF and provide download link
            pdf_data = pdf.table_generator("Meals Report", df)  # Pass the DataFrame directly

            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name=f"meals_report_{dt.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf",
                mime="application/pdf"
            )
        else:
            st.info("No data found for the given inputs. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
