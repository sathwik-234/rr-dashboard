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


st.title("Linen Report 🛌")
st.markdown("---")  # Horizontal divider for neatness
st.write(f"**📅 Today's Date:** {dt.datetime.now().date().strftime('%d/%m/%Y')}")

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

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if st.button("🚀 Submit"):
    st.session_state.submitted = True

if st.session_state.submitted:

    try:
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")

        with st.spinner("Fetching data..."):
            query = sp.from_("CheckIn").select("*,Crew(*)").gte("ic_time", start_date).lte("ic_time", end_date)
            response = query.execute()

        if response.data:
            data = response.data
        else:
            st.error("Failed to fetch data. Check your query or database connection.")
            st.stop()

        if data and len(data) > 0:
            st.write(f"### 📊 Linen Report ")
            df = pd.DataFrame(data)
            crew_data = df['Crew']
            df.drop(columns=['id', 'created_at','Crew','ic_train_no'], inplace=True)

            df.insert(1, "Crew Name", crew_data.apply(lambda x: x['crewname']))
            df.insert(2,"Crew HQ", crew_data.apply(lambda x: x['hq']))
            df['ic_time'] = pd.to_datetime(df['ic_time']).dt.strftime('%d/%m/%Y %H:%M')  # Format datetime

            df.rename(columns = {"cms_id": "CMS ID", "crew_name": "Crew Name", "ic_time": "CheckIn Time","bedsheets" : "BedSheets","pillowcovers":"Pillow Covers","blankets":"Blankets","allotted_bed" : "Bed"}, inplace=True)    

            st.dataframe(df)

            pdf_data = pdf.table_generator("Linen Report", df)

            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name=f"linen_report_{dt.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.pdf",
                mime="application/pdf"
            )

        else:
            st.info("No data found for the given inputs. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
