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

st.title("Peak Occupation 📊")
st.markdown("---")
st.write(f"**📅 Today's Date:** {dt.datetime.now().date().strftime('%d/%m/%Y')}")

st.markdown("### 🛠 Inputs:")
col1, col2, col3 = st.columns(3)

with col1:
    month_name = st.selectbox(
        "🗓 Select Month:",
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        index=dt.datetime.now().month - 1  
    )

st.markdown("---")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if st.button("🚀 Submit"):
    st.session_state.submitted = True

if st.session_state.submitted:
    try:
        current_year = dt.datetime.now().year
        month_num = dt.datetime.strptime(month_name, "%B").month
        start_date = dt.date(current_year, month_num, 1)

        if month_num == 12:
            end_date = dt.date(current_year + 1, 1, 1) - dt.timedelta(days=1)
        else:
            end_date = dt.date(current_year, month_num + 1, 1) - dt.timedelta(days=1)

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        with st.spinner("Fetching data..."):
            query = sp.from_("CheckIn").select("*, Crew(*)").gte("ic_time", start_date_str).lte("ic_time", end_date_str)
            print(f"Executing query: {query}")
            response = query.execute()
            print(f"Response Data: {response.data}")

        if response:
            data = response.data
        else:
            st.error("Failed to fetch data. Check your query or database connection.")
            st.stop()

        if data and len(data) > 0:
            df = pd.DataFrame(data)
            
            # Extract Crew data
            crew_data = df['Crew'].apply(lambda x: x.get('crewname') if isinstance(x, dict) else None)
            crew_hq = df['Crew'].apply(lambda x: x.get('hq') if isinstance(x, dict) else None)
            
            # Extract check-in time data
            checkin_data = df['ic_time']
            
            # Clean DataFrame by dropping unnecessary columns
            df.drop(columns=['id', 'created_at', 'ic_train_no', 'bedsheets', 'pillowcovers', 'Crew'], inplace=True)
            
            # Insert Crew and CheckIn columns at correct positions
            df.insert(1, "Crew Name", crew_data)
            df.insert(2, "Crew HQ", crew_hq)
            df.insert(3, "CheckIn Time", checkin_data)

            # Convert CheckIn Time to datetime
            df['CheckIn Time'] = pd.to_datetime(df['CheckIn Time'], errors='coerce')
            df.dropna(subset=["Crew Name", "CheckIn Time"], inplace=True)

            df.fillna("N/A", inplace=True)

            # Add a Date and Hour column from the CheckIn Time
            df['CheckIn Date'] = df['CheckIn Time'].dt.date
            df['CheckIn Hour'] = df['CheckIn Time'].dt.hour

            # Peak Occupancy per Hour calculation
            full_date_range = pd.date_range(start=start_date, end=end_date).date  # All days in the month
            full_hour_range = list(range(24))  # 24 hours in a day

            # Create an empty DataFrame to store occupancy data for each day and hour
            occupancy_data = []

            for date in full_date_range:
                for hour in full_hour_range:
                    occupancy_count = len(df[(df['CheckIn Date'] == date) & (df['CheckIn Hour'] == hour)])
                    occupancy_data.append({'Date': date, 'Hour': hour, 'Occupancy': occupancy_count})

            occupancy_df = pd.DataFrame(occupancy_data)

            # Pivot data to get each day as a row and hours (0-23) as columns
            occupancy_pivot = occupancy_df.pivot_table(index='Date', columns='Hour', values='Occupancy', aggfunc='sum', fill_value=0)

            st.write("### Peak Occupancy per Hour (Bar Chart):")

            # Plot occupancy per hour for each day (24 hours for each day)
            plt.figure(figsize=(16, 10)) 

            # Create a bar chart for each hour of each day
            ax = occupancy_pivot.plot(kind='bar', figsize=(16, 10), stacked=False, width=0.8)

            plt.xlabel("Date", fontsize=14)
            plt.ylabel("Occupancy", fontsize=14)
            plt.title(f"Peak Occupancy per Hour for Each Day - {month_name} {current_year}", fontsize=16)
            plt.xticks(rotation=90, fontsize=10)
            plt.legend(title="Hour", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

            # Add values on top of the bars
            for p in ax.patches:
                height = p.get_height()
                width = p.get_width()
                x, y = p.get_xy()  # Get the x and y positions of the bars
                ax.annotate(f'{int(height)}', (x + width / 2, y + height), ha='center', va='center', fontsize=10, color='black')

            st.pyplot(plt)

            st.dataframe(occupancy_pivot)
        else:
            st.write("### Peak Occupancy per Hour (Bar Chart):")
            plt.figure(figsize=(16, 10))
            plt.bar(full_hour_range, [0] * len(full_hour_range), color='skyblue') 
            plt.xlabel("Hour of the Day", fontsize=14)
            plt.ylabel("Occupancy", fontsize=14)
            plt.title(f"Peak Occupancy per Hour - {month_name} {current_year}", fontsize=16)
            plt.xticks(full_hour_range, [f"{i}:00" for i in full_hour_range], rotation=90, fontsize=10)
            st.pyplot(plt)

            st.info("No data found for the given month. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
