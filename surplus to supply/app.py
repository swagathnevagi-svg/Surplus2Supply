
import streamlit as st
import sqlite3
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Surplus to Supply",
    page_icon="🍲",
    layout="centered"
)

# Database connection
conn = sqlite3.connect("donations.db")
cursor = conn.cursor()

# Create donations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    location TEXT NOT NULL,
    available_until TEXT NOT NULL
)
""")
conn.commit()

# Main heading
st.title("🍲 Surplus to Supply")
st.subheader("Smart Food Waste Management and Redistribution Platform")

st.write(
    "Reducing food waste by connecting surplus food donors "
    "with receivers."
)

st.divider()

# Choose role
st.header("Choose Your Role")

role = st.radio(
    "Are you a donor or a receiver?",
    ["Donor", "Receiver"]
)

# DONOR SECTION
if role == "Donor":

    st.success("Welcome, Donor!")
    st.write("List your surplus food for people in need.")

    st.header("Food Donation Form")

    with st.form("donation_form"):

        food_name = st.text_input("Food Name")

        quantity = st.number_input(
            "Quantity (in meals)",
            min_value=1,
            step=1
        )

        location = st.text_input("Pickup Location")

        expiry = st.date_input(
            "Food Available Until",
            min_value=date.today()
        )

        submitted = st.form_submit_button("Submit Donation")

        if submitted:
            if food_name.strip() and location.strip():

                cursor.execute(
                    """
                    INSERT INTO donations
                    (food_name, quantity, location, available_until)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        food_name.strip(),
                        quantity,
                        location.strip(),
                        expiry.isoformat()
                    )
                )

                conn.commit()

                st.success("Donation submitted successfully!")
                st.write("Food:", food_name)
                st.write("Quantity:", quantity, "meals")
                st.write("Pickup Location:", location)
                st.write("Available Until:", expiry)

            else:
                st.warning(
                    "Please enter both the food name and pickup location."
                )

# RECEIVER SECTION
elif role == "Receiver":

    st.success("Welcome, Receiver!")
    st.write("View available food donations below.")

    st.header("Available Food Donations")

    cursor.execute("""
        SELECT id, food_name, quantity, location, available_until
        FROM donations
        ORDER BY id DESC
    """)

    donations = cursor.fetchall()

    if donations:

        for donation in donations:

            donation_id = donation[0]
            food_name = donation[1]
            quantity = donation[2]
            location = donation[3]
            available_until = donation[4]

            with st.container(border=True):

                st.subheader(food_name)
                st.write("Quantity:", quantity, "meals")
                st.write("Pickup Location:", location)
                st.write("Available Until:", available_until)

                if st.button(
                    "Delete Donation",
                    key=f"delete_{donation_id}"
                ):

                    cursor.execute(
                        "DELETE FROM donations WHERE id = ?",
                        (donation_id,)
                    )

                    conn.commit()
                    st.success("Donation deleted successfully!")
                    st.rerun()

    else:
        st.info("No food donations are available yet.")

# Close database connection
conn.close()
