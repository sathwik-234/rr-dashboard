import streamlit as st
from supabaseClient import supabase
import datetime as dt

# Custom CSS for styling
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

st.title("Outgoing T.O. Allocation ⏲️")
st.markdown("---")
st.write(f"**📅 Today's Date:** {dt.datetime.now().date().strftime('%d/%m/%Y')}")

# Layout for the form
col1, col2, col3 = st.columns(3)

# CMS ID input field
with col1:
    cms_id = st.text_input("Enter your CMS ID:")
    cms_id = cms_id.upper()

# Date and Time input fields
with col2:
    to_date = st.date_input("Enter T.O. Date:", min_value=dt.date.today())
    to_time = st.time_input("Enter T.O. Time:", value=None)

st.markdown("---")

# Submit button
submit_button = st.button("Submit", key="submit")

if submit_button and to_date and to_time:
    try:
        # Combine the date and time inputs into a datetime object
        combined_datetime = dt.datetime.combine(to_date, to_time)

        # Store the datetime as it is (without timezone)
        iso_datetime = combined_datetime.isoformat()

        # Fetch the latest entry in the CheckIn table
        response = supabase.table("CheckIn").select("*") \
            .order("created_at", desc=True).limit(1).execute()
        
        if response.data:
            last_entry = response.data[0]
            data = last_entry  # No need to redefine, `last_entry` already holds the data
            st.write(f"Last entry CMS ID: {last_entry['cms_id']}, Check-in Time: {last_entry['ic_time']}")
        else:
            st.write("No previous entry found in the Checkin table.")

        # Insert the new data with the combined datetime
        insert_response = supabase.table("CheckIn").update({
            "to_time": iso_datetime
        }).match({"id": data["id"]}).execute()

        # Step 3: Check if the insertion was successful
        if insert_response.data:
            st.success("T.O. Allocation submitted successfully!")
        else:
            st.error(f"Error: {insert_response.error.message}")

        # Display the combined date-time
        st.write(f"Selected Date and Time: {combined_datetime.strftime('%d/%m/%Y %H:%M:%S')}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
