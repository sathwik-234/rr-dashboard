import streamlit as st
from datetime import datetime
from supabaseClient import supabase
import pytz

# Fetch occupancy data
def fetch_occupancy_data():
    try:
        response = supabase.table("Rooms").select("*,Crew(*)").execute()
        if not response.data:
            raise Exception("No data found or an error occurred.")
        sorted_data = sorted(response.data, key=lambda room: room["room_no"])
        return sorted_data, None
    except Exception as e:
        return [], str(e)

# Update room status
def update_room_status(room_no, status):
    try:
        # Update the Rooms table
        response = supabase.table("Rooms").update({"status": status}).eq("room_no", room_no).execute()

        if response.data and response.data[0]["status"] == status:
            success, error_msg = log_room_hold_data(room_no, status)
            if not success:
                return False, error_msg
            return True, None
        elif response.error:
            return False, response.error.message
        else:
            return False, "Unexpected response, status not updated."
    except Exception as e:
        return False, str(e)

# Log hold data
from datetime import datetime

def log_room_hold_data(room_no, status):
    try:
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist).isoformat()

        if status: 
            response = supabase.table("RoomHoldData").insert({
                "room_no": room_no,
                "hold_on_time": now,
                "hold_off_time": None
            }).execute()

            if not response.data:
                return False, response.error.message
            return True, None

        else: 
            fetch_response = supabase.table("RoomHoldData").select("id") \
                .eq("room_no", room_no) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()

            if not fetch_response.data:
                return False, "No record found for the specified room."
            latest_record_id = fetch_response.data[0]["id"]
            update_response = supabase.table("RoomHoldData").update({
                "hold_off_time": now
            }).eq("id", latest_record_id).execute()

            if not update_response and not update_response.data:
                return False, update_response.error.message
            return True, None

    except Exception as e:
        return False, str(e)


occupancy_data, error = fetch_occupancy_data()

st.title("Room Occupancy Dashboard")

if error:
    st.error(f"Error fetching room occupancy data: {error}")
else:
    for i in range(0, len(occupancy_data), 4):
        cols = st.columns(4)

        for col, room in zip(cols, occupancy_data[i:i + 4]):
            with col:
                st.markdown(f"### Room {room['room_no']}")
                button_key = f"hold_{room['room_no']}"

                if room["status"] and not room["allotted_to"]:
                    if st.button("Un Hold", key=button_key):
                        success, error_msg = update_room_status(room["room_no"], False)
                        if success:
                            st.rerun()
                        else:
                            st.error(f"Failed to unhold room: {error_msg}")
                elif room["status"] and room["allotted_to"]:
                    st.markdown(f"""
                        <button class="in-occupancy-btn" id="{button_key}" disabled>
                            In Occupancy
                        </button>""", unsafe_allow_html=True)
                else:
                    if st.button("Hold", key=f"not_hold_{room['room_no']}"):
                        success, error_msg = update_room_status(room["room_no"], True)
                        if success:
                            st.rerun()
                        else:
                            st.error(f"Failed to hold room: {error_msg}")

                st.divider()

# Add custom CSS for button styling
st.markdown("""
    <style>
        .hold-btn {
            background-color: #ff6347; /* Tomato color for 'Hold' */
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }

        .hold-btn:hover {
            background-color: #ff4500; /* Darker red for hover */
        }

        .in-occupancy-btn {
            background-color: #ff0000; /* Grey color for 'In Occupancy' */
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: not-allowed;
            font-size: 16px;
            width: 100%;
        }

        .in-occupancy-btn:disabled {
            cursor: not-allowed;
        }
    </style>
""", unsafe_allow_html=True)
