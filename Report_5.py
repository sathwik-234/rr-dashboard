import streamlit as st
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from supabaseClient import supabase as sp

# Custom CSS
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

st.title("Linen Report 🛌")
st.markdown("---")
st.write(f"**📅 Today's Date:** {dt.datetime.now().date().strftime('%d/%m/%Y')}")

st.markdown("### 🛠 Inputs:")
col1, col2, col3 = st.columns(3)

# Month name input
with col1:
    month_name = st.selectbox(
        "🗓 Select Month:",
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        index=dt.datetime.now().month - 1  # Default to the current month
    )

st.markdown("---")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if st.button("🚀 Submit"):
    st.session_state.submitted = True

if st.session_state.submitted:
    try:
        # Get the first and last day of the selected month
        current_year = dt.datetime.now().year
        month_num = dt.datetime.strptime(month_name, "%B").month
        start_date = dt.date(current_year, month_num, 1)

        # Calculate the last day of the month
        if month_num == 12:
            end_date = dt.date(current_year + 1, 1, 1) - dt.timedelta(days=1)
        else:
            end_date = dt.date(current_year, month_num + 1, 1) - dt.timedelta(days=1)

        # Convert to string format for query
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        with st.spinner("Fetching data..."):
            # Remove the HQ filter to get data for all HQs
            query = sp.from_("CheckOut").select("*, Crew(*), CheckIn(*)").gte("out_time", start_date_str).lte("out_time", end_date_str)

            response = query.execute()

        if response.data:
            data = response.data
        else:
            st.error("Failed to fetch data. Check your query or database connection.")
            st.stop()

        if data and len(data) > 0:
            # st.write(f"### 📊 Rest Report ")

            df = pd.DataFrame(data)

            # Safeguard against NoneType when accessing Crew and CheckIn
            crew_data = df['Crew'].apply(lambda x: x.get('crewname') if x else None)
            checkin_data = df['CheckIn'].apply(lambda x: x.get('ic_time') if x else None)

            # Drop unnecessary columns including 'Crew' column
            df.drop(columns=['id', 'created_at', 'CheckIn', 'out_train_no', 'breakfast', 'lunch', 'dinner', 'parcel', 'cleanliness', 'food', 'service', 'comfort', 'overall', 'allotted_bed', 'check_in_id'], inplace=True)

            # Insert crew data as new columns
            df.insert(1, "Crew Name", crew_data)
            df.insert(2, "Crew HQ", df['Crew'].apply(lambda x: x.get('hq') if x else None))
            df.insert(3, "CheckIn Time", checkin_data)

            # Now that we have extracted relevant crew data, we can drop the 'Crew' column
            df.drop(columns=['Crew'], inplace=True)

            # Convert times to datetime and calculate the difference
            df['out_time'] = pd.to_datetime(df['out_time'], errors='coerce')
            df['CheckIn Time'] = pd.to_datetime(df['CheckIn Time'], errors='coerce')

            # Drop rows where any of the critical columns have missing values (Crew Name, CheckIn Time, out_time)
            df.dropna(subset=["Crew Name", "CheckIn Time", "out_time"], inplace=True)

            # Safeguard for missing or invalid dates
            df["Diff"] = df.apply(lambda row: (row['out_time'] - row['CheckIn Time']).total_seconds() / 60 if pd.notna(row['out_time']) and pd.notna(row['CheckIn Time']) else None, axis=1)

            # Format output times
            df['out_time'] = df['out_time'].dt.strftime('%d/%m/%Y %H:%M')  # Format datetime

            # Handle missing data gracefully (optional)
            df.fillna("N/A", inplace=True)  # Replace NaN/None with "N/A" (or you can use other placeholder like "Unknown")

            # **Peak Occupancy per Day (Bar Graph)**

            # Generate the full date range for the month
            full_date_range = pd.date_range(start=start_date, end=end_date).date

            # Ensure 'out_time' is datetime and extract only the date part
            df['out_time'] = pd.to_datetime(df['out_time'], errors='coerce')
            df['out_date'] = df['out_time'].dt.date  # Extract date part only

            # Group by the extracted date and count occurrences for occupancy per day
            occupancy_per_day = df.groupby('out_date').size()

            # Ensure all days of the month are included, fill missing dates with 0
            occupancy_per_day_full_month = pd.Series(0, index=full_date_range).add(occupancy_per_day, fill_value=0)

            # Plotting with matplotlib
            st.write("### Peak Occupancy per Day (Bar Chart):")
            
            # Create the plot
            plt.figure(figsize=(12, 8))  # Adjusted the figure size for long charts
            bars = plt.bar(occupancy_per_day_full_month.index, occupancy_per_day_full_month.values, color='skyblue')

            # Format the plot
            plt.xlabel("Date", fontsize=14)
            plt.ylabel("Occupancy", fontsize=14)
            plt.title(f"Peak Occupancy per Day - {month_name} {current_year}", fontsize=16)

            # Format the dates on x-axis and change the date format
            formatted_dates = [date.strftime('%d/%m/%Y') for date in occupancy_per_day_full_month.index]
            plt.xticks(occupancy_per_day_full_month.index, formatted_dates, rotation=90, fontsize=10)  # Rotate x-ticks to avoid overlap

            # Adding count values on top of the bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, height, str(int(height)), ha='center', va='bottom', fontsize=10)

            # If no data exists for the month, show a message on the graph
            if occupancy_per_day_full_month.sum() == 0:
                plt.text(0.5, 0.5, "No Data Available for the Selected Month", ha='center', va='center', fontsize=14, color='red', transform=plt.gca().transAxes)

            # Show the plot in Streamlit
            st.pyplot(plt)

            # Display the DataFrame
            st.dataframe(df)
        else:
            # In case of no records in the response, show the empty chart
            st.write("### Peak Occupancy per Day (Bar Chart):")
            plt.figure(figsize=(12, 8))  # Adjusted the figure size for long charts
            plt.bar(full_date_range, [0] * len(full_date_range), color='skyblue')  # Bar with no values
            plt.xlabel("Date", fontsize=14)
            plt.ylabel("Occupancy", fontsize=14)
            plt.title(f"Peak Occupancy per Day - {month_name} {current_year}", fontsize=16)

            # Format the dates on x-axis and change the date format
            formatted_dates = [date.strftime('%d/%m/%Y') for date in full_date_range]
            plt.xticks(full_date_range, formatted_dates, rotation=90, fontsize=10)  # Rotate x-ticks to avoid overlap

            # Show the plot in Streamlit
            st.pyplot(plt)

            st.info("No data found for the given month. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
