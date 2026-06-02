import streamlit as st
import psycopg2


DB_URL = st.secrets["DB_URL"]

st.set_page_config(page_title="Stray Animal System", page_icon="🐾", layout="wide")

@st.cache_resource
def init_connection():
    return psycopg2.connect(DB_URL)

try:
    conn = init_connection()
    cursor = conn.cursor()
    
    st.title("🐾 Stray Animal Health & Foster Dashboard")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 System Overview", 
        "🚨 Alerts & Reports", 
        "➕ Register Volunteer", 
        "🐶 Register Animal"
    ])
    
    with tab1:
        st.subheader("👥 All Foster Volunteers (Tüm Gönüllüler)")
        cursor.execute("SELECT volunteer_id AS \"ID\", name AS \"Name\", phone AS \"Phone\", address AS \"Address\", capacity AS \"Capacity\" FROM Foster_Volunteers ORDER BY volunteer_id;")
        volunteers = cursor.fetchall()
        if volunteers:
            st.dataframe([dict(zip([desc[0] for desc in cursor.description], row)) for row in volunteers], use_container_width=True)
        else:
            st.info("There are no registered volunteers in the system yet.")

        st.divider()

        st.subheader("🐾 All Registered Animals")
        cursor.execute("""
            SELECT a.animal_id AS "ID", a.name AS "Name", a.age AS "Age", a.gender AS "Gender", 
                   t.type_name AS "Species", a.health_status AS "Health Status", a.status AS "Foster Status",
                   COALESCE(f.name, 'Unassigned') AS "Foster Volunteer"
            FROM Animals a
            LEFT JOIN Animal_Types t ON a.type_id = t.type_id
            LEFT JOIN Foster_Volunteers f ON a.volunteer_id = f.volunteer_id
            ORDER BY a.animal_id;
        """)
        animals = cursor.fetchall()
        if animals:
            st.dataframe([dict(zip([desc[0] for desc in cursor.description], row)) for row in animals], use_container_width=True)
        else:
            st.info("There are no animals registered in the system yet.")
    
    with tab2:
        st.subheader("Capacity Warning System")
        if st.button("Show Volunteers at Max Capacity"):
            query1 = """
            SELECT f.name AS "Volunteer Name", f.capacity AS "Max Capacity", COUNT(a.animal_id) AS "Current Fosters"
            FROM Foster_Volunteers f
            LEFT JOIN Animals a ON f.volunteer_id = a.volunteer_id
            GROUP BY f.name, f.capacity
            HAVING COUNT(a.animal_id) >= f.capacity;
            """
            cursor.execute(query1)
            results1 = cursor.fetchall()
            if results1:
                st.dataframe([dict(zip([desc[0] for desc in cursor.description], row)) for row in results1], use_container_width=True)
            else:
                st.success("All volunteers' capacity is currently at a safe level!")

        st.divider()

        st.subheader("Upcoming Vaccinations (Next 30 Days)")
        if st.button("Get Urgent Vaccination List"):
            query2 = """
            WITH Upcoming_Vaccines AS (
                SELECT animal_id, vaccine_name, next_due_date
                FROM Vaccination_Records
                WHERE next_due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
            )
            SELECT a.name AS "Animal Name", f.name AS "Volunteer Name", u.vaccine_name AS "Vaccine", u.next_due_date AS "Due Date"
            FROM Animals a
            INNER JOIN Upcoming_Vaccines u ON a.animal_id = u.animal_id
            LEFT JOIN Foster_Volunteers f ON a.volunteer_id = f.volunteer_id
            ORDER BY u.next_due_date ASC;
            """
            cursor.execute(query2)
            results2 = cursor.fetchall()
            if results2:
                st.dataframe([dict(zip([desc[0] for desc in cursor.description], row)) for row in results2], use_container_width=True)
            else:
                st.success("There is no urgent vaccine that needs to be administered within the next 30 days!")
    
    with tab3:
        st.subheader("Add New Foster Volunteer")
        with st.form("new_volunteer_form"):
            v_name = st.text_input("Full Name")
            v_phone = st.text_input("Phone Number")
            v_address = st.text_input("Address")
            v_capacity = st.number_input("Max Capacity", min_value=1, step=1)
            
            submit_volunteer = st.form_submit_button("Save to Database")
            
            if submit_volunteer:
                cursor.execute(
                    "INSERT INTO Foster_Volunteers (name, phone, address, capacity) VALUES (%s, %s, %s, %s)",
                    (v_name, v_phone, v_address, v_capacity)
                )
                conn.commit()
                st.success(f"{v_name} successfully added to the live database!")
    
    with tab4:
        st.subheader("Register a New Rescued Animal")
        with st.form("new_animal_form"):
            a_name = st.text_input("Animal Name")
            a_age = st.number_input("Age", min_value=0, step=1)
            a_gender = st.selectbox("Gender", ["Male", "Female"])
            
            a_type = st.selectbox("Species", options=[1, 2, 3], format_func=lambda x: "Dog" if x==1 else ("Cat" if x==2 else "Bird"))
            a_health = st.selectbox("Health Status", ["Healthy", "Under Treatment", "Critical"])
            
            submit_animal = st.form_submit_button("Save to Database")
            
            if submit_animal:
                cursor.execute(
                    "INSERT INTO Animals (name, age, gender, type_id, health_status, arrival_date, status) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, 'Fostered')",
                    (a_name, a_age, a_gender, a_type, a_health)
                )
                conn.commit()
                st.success(f"{a_name} successfully registered! ")

except Exception as e:
    st.error(f"Connection Error: {e}")