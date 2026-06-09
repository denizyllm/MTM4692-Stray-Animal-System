## 🐾 Stray Animal Foster & Health Tracking System 
This repository contains the completed engineering implementation for the Applied SQL database project, designed to solve real-world data fragmentation in stray animal management through a cloud-deployed relational system.

## 🎓 Course Context
- **University:** Yildiz Technical University   
- **Faculty:** Faculty of Chemical Metallurgical   
- **Department:** Mathematical Engineering   
- **Instructor:** Lecturer Dr. Fettah KIRAN   
- **Project Team:** Deniz YILMAZ, Batuhan TEKİNALP, Arif Emre POLAT, Damla Hilal ERDEN
- **Presentation:** https://drive.google.com/drive/folders/1gItPUUwl4_j682JJKSe-UMilgwsm74RG?usp=drive_link 

## 🚩 Problem Definition & Justification
### The Problem
Stray animal management by local municipalities and NGOs often suffers from fragmented data systems. This disconnection leads to critical operational failures:  

- **📉 Overcrowded Fosters:** Volunteers receiving more animals than their safe capacity limits.  
- 💉 **Missed Medical Dates:** Lost track of crucial vaccination and treatment schedules.  
- 📦 **Unassigned Donations:** Inefficient tracking of supplies (food, medicine) donated to specific volunteers.  
- **🏠 Adoption Bottlenecks:** Lack of centralized tracking for adoption requests and animal statuses.  

### The Solution
This project introduces a fully normalized, relational database system acting as a central coordination layer. It seamlessly connects animals, volunteers, clinics, and donations to ensure data integrity, automate capacity checks, and streamline health tracking via an interactive web dashboard.

## 🛠️ Technology Stack & Cloud Deployment
Unlike traditional, local-only SQL projects, this system has been deployed as a live cloud-based application: 

- **PostgreSQL:** Relational database management system ensuring robust schemas and transactional control.  
- **Supabase:** Cloud database platform hosting the PostgreSQL instance remotely.  
- **Streamlit:** Python-driven framework supplying a dynamic and interactive web user interface.  
- **Python:** Middleware controller handling connections, transactional logic, and DML query execution.  

## 🏗️ Schema Overview (3NF Target)
The system architecture features 7 tables meticulously normalized up to Third Normal Form (3NF) to eliminate redundancies and optimize join operations:

## Tables

| Table Name | Description | Key Relationship |
|:--------:|:------:|:------:|
| `Animal_Types` | Master data for animal species and breeds. | $1:N$ with `Animals`    |
| `Foster_Volunteers` | Volunteer contact profiles and max safe capacity limits. | $1:N$ with `Animals` & `Supplies_Donations` |
| `Animals` | Core identity, age, health status, and foster assignments. | FK to `Foster_Volunteers` & `Animal_Types` |
| `Vaccination_Records` | Logs of applied vaccines and automated next due dates. | FK to `Animals` |
| `Vet_Visits` | Clinical case sheets, diagnosis records, and treatment logs.| FK to `Animals` |
| `Adoption_Requests` | Ledger for potential adopters and sequential request statuses. | FK to `Animals` |
| `Supplies_Donations` |Asset ledger for tracking physical goods allocated to fosters. | FK to `Foster_Volunteers` |

## 🗺️ Entity Relationship Diagram (ERD)
Below is the structured schema design mapping primary keys, foreign keys, and internal relational dependencies:  

![Entity Relationship Diagram](erd.png)

## 🛡️ Business Rules Implemented in SQL
The core logical bounds are strictly enforced natively at the database level using SQL constraints to secure data integrity: 

- **Capacity Integrity:** A volunteer's maximum safe room threshold must remain strictly above zero (CHECK capacity > 0).  
- **Age Validation:** An animal's registered age cannot register as a negative integer (CHECK age >= 0).  
- **Status Control:** Restricts lifecycle data entry fields to discrete domain matrices (e.g., 'Fostered', 'Adopted', 'Under Treatment').  
- **Referential Integrity:** Enforces absolute standard consistency preventing unlinked animal mappings to orphaned or non-existent volunteer IDs.  

## 💻 Implemented Production Queries
Real-time operations are powered by advanced SQL query structures executed dynamically via the client dashboard:

### Query 1: The Active Roster (INNER JOIN)
Retrieves a list of all currently fostered stray animals, matching them with their taxonomic classification and their host volunteer’s contact coordinates.

```sql
SELECT
    a.name AS Animal_Name,
    t.type_name AS Species,
    a.age,
    f.name AS Foster_Name,
    f.phone
FROM Animals a
INNER JOIN Foster_Volunteers f 
    ON a.volunteer_id = f.volunteer_id
INNER JOIN Animal_Types t 
    ON a.type_id = t.type_id
WHERE a.status = 'Fostered'
ORDER BY t.type_name, a.name;
```

### Query 2: Capacity Control (GROUP BY + HAVING)
Identifies individual foster volunteers who are currently running at or over their pre-defined maximum safe structural load capacity.

```sql
SELECT
    f.name AS Volunteer_Name,
    f.capacity AS Max_Capacity,
    COUNT(a.animal_id) AS Current_Fosters
FROM Foster_Volunteers f
LEFT JOIN Animals a 
    ON f.volunteer_id = a.volunteer_id
GROUP BY f.name, f.capacity
HAVING COUNT(a.animal_id) >= f.capacity;
```

### Query 3: Urgent Vaccination Pipeline (PostgreSQL CTE)
Isolates a time-sensitive pipeline of upcoming medical intervention deadlines windowed dynamically over the next 30 days.

```sql
WITH Upcoming_Vaccines AS (
    SELECT
        animal_id,
        vaccine_name,
        next_due_date
    FROM Vaccination_Records
    WHERE next_due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
)
SELECT
    a.name AS Animal_Name,
    f.name AS Volunteer_Name,
    u.vaccine_name,
    u.next_due_date
FROM Animals a
INNER JOIN Upcoming_Vaccines u 
    ON a.animal_id = u.animal_id
INNER JOIN Foster_Volunteers f 
    ON a.volunteer_id = f.volunteer_id
ORDER BY u.next_due_date ASC;
```

## 📂 Repository Structure

```plaintext
MTM4692-Stray-Animal-System/
├── README.md                 ← Documented system specs, schema layouts, and operational scripts
├── erd.png                   ← High-resolution Entity Relationship Diagram (3NF)
├── app.py                    ← Streamlit production interface file connected to cloud PostgreSQL
├── requirements.txt          ← Python dependencies package list (streamlit, psycopg2-binary, etc.)
├── sql/
│   ├── 01_schema.sql         ← Database DDL scripts (Table creations & CHECK domains)
│   └── 02_mock_data.sql      ← Seed scripts representing real-world sample baselines
└── Technical_Report5.pdf     ← Final Comprehensive Engineering Milestone PDF submission
``` 

