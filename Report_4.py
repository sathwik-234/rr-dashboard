import streamlit as st
import datetime as dt
import pandas as pd
from supabaseClient import supabase as sp
import pdf_reports as pdf

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

st.title("Rest Report 📊")
st.markdown("---")
st.write(f"**📅 Today's Date:** {dt.datetime.now().date().strftime('%d/%m/%Y')}")

st.markdown("### 🛠 Inputs:")
col1, col2, col3 = st.columns(3)

with col1:
    hq = st.text_input(
        "🏨 HeadQuarters(hq)",
        placeholder="Enter the hq"
    )

with col2:
    today = dt.datetime.now().date()
    ten_days_before = today - dt.timedelta(days=10)
    date_range = st.date_input(
        "🗓 Time Range:",
        (ten_days_before, today)
    )

st.markdown("---")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if st.button("🚀 Submit"):
    st.session_state.submitted = True

if st.session_state.submitted:
    try:
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")

        with st.spinner("Fetching data..."):
            if hq:
                query = sp.from_("CheckOut").select("*, Crew(*), CheckIn(*)").eq("Crew.hq", hq.upper()).gte("out_time", start_date).lte("out_time", end_date)
            else:
                query = sp.from_("CheckOut").select("*, Crew(*), CheckIn(*)").gte("out_time", start_date).lte("out_time", end_date)

            response = query.execute()

        if response.data:
            data = response.data
        else:
            st.error("Failed to fetch data. Check your query or database connection.")
            st.stop()

        if data and len(data) > 0:
            st.write(f"### 📊 Rest Report ")

            df = pd.DataFrame(data)
            crew_data = df['Crew'].apply(lambda x: x.get('crewname') if x else None)
            checkin_data = df['CheckIn'].apply(lambda x: x.get('ic_time') if x else None)

            df.drop(columns=['id', 'created_at', 'CheckIn', 'out_train_no', 'breakfast', 'lunch', 'dinner', 'parcel', 'cleanliness', 'food', 'service', 'comfort', 'overall', 'allotted_bed', 'check_in_id'], inplace=True)


            df.insert(1, "Crew Name", crew_data)
            df.insert(2, "Crew HQ", df['Crew'].apply(lambda x: x.get('hq') if x else None))
            df.insert(3, "CheckIn Time", checkin_data)

            df.drop(columns=['Crew'], inplace=True)

            df['out_time'] = pd.to_datetime(df['out_time'], errors='coerce')
            df['CheckIn Time'] = pd.to_datetime(df['CheckIn Time'], errors='coerce')
            df.dropna(subset=["Crew Name", "CheckIn Time", "out_time"], inplace=True)
            df["Diff"] = df.apply(lambda row: round((row['out_time'] - row['CheckIn Time']).total_seconds() / 3600, 2) if pd.notna(row['out_time']) and pd.notna(row['CheckIn Time']) else None, axis=1)
            df.fillna("N/A", inplace=True) 
            df.rename(columns = {"cms_id": "CMS ID", "crew_name": "Crew Name", "out_time": "CheckOut Time","Diff":"Difference"}, inplace=True)
            st.dataframe(df)

            pdf_data = pdf.table_generator("Rest Report", df)

            st.download_button(
                label="Download Report",
                data=pdf_data,
                file_name=f"Rest_Report_{dt.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf",
                mime="application/pdf",
            )
        else:
            st.info("No data found for the given inputs. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
