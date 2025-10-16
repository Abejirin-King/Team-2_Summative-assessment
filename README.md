# Taxi Data Flask App

## Overview

This project is a Flask web dashboard that visualizes NYC Taxi Trip data loaded into a MySQL database. It displays average fares, distances, and speeds for trips within a selected date range.

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Purpose | Version (recommended) |
|------|---------|---------------------|
| Python | Backend runtime | 3.9 or newer |
| MySQL Server | Stores taxi data | 8.0+ |
| pip | Python package manager | latest |
| VS Code (optional) | Development IDE | latest |

## Setup Instructions (Use VS Code)

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/your-username/Team-2_Summative-assessment.git
cd Team-2_Summative-assessment
```

(Use the zip file, as the csv file was too large to push to github)

### Step 2: Create a Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install flask mysql-connector-python python-dotenv pandas
```

### Step 4: Create the MySQL Database

Open your MySQL client and run:

```sql
CREATE DATABASE taxi_data;
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'King40$$';
GRANT ALL PRIVILEGES ON taxi_data.* TO 'etl_user'@'localhost';
FLUSH PRIVILEGES;
```

Then run the SQL schema file you used earlier (or recreate your tables using your ETL script).

### Step 5: Load Data into MySQL

Run your data ingestion script to load the cleaned CSV file:

```bash
python load_to_mysql.py
```

You should see output like:

```
 CSV file found
 Connected to database
➡ Processing chunk 1 with 5000 rows
 Inserted 5000 rows in chunk 1
 All done! Inserted: 15000, Errors: 0
```

## Running the Flask App

Start the Flask server:

```bash
python app.py
```

If successful, you’ll see:

```
 * Running on http://127.0.0.1:5000
```

Then open your browser and visit:

👉 http://127.0.0.1:5000

## App Features

**Frontend (index.html):**
- Date range selection
- Min/Max fare filters
- “Sort by” dropdown (Pickup time, fare, etc.)
- Table of recent trips
- Summary stats: average fare, distance, and speed

**Backend (Flask):**
- `/api/trips` endpoint queries MySQL dynamically
- Calculates distance (km) and speed (km/h)
- Returns data as JSON for the frontend to render

## Folder Structure

```
taxi-data-flask-app/
│
├── app.py                    # Flask web app
├── load_to_mysql.py          # Data ingestion script
├── cleaned_data.csv          # Clean dataset
│
├── templates/
│   └── index.html            # Frontend HTML
│
├── static/
│   ├── style.css             # CSS styling
│   └── script.js             # Frontend logic
│
└── README.md                 # Project documentation
```

## Common Issues

| Issue | Fix |
|-------|-----|
| ModuleNotFoundError: No module named 'flask' | Make sure you activated your virtual environment and ran `pip install flask` |
| Access denied for user 'etl_user'@'localhost' | Run the SQL GRANT commands again or check your MySQL password |
| Out of range value for column 'trip_speed_kmph' | Ensure your ETL script caps unrealistic speed values (e.g. >300 km/h) |
| Webpage shows no data | Check the date range filters and make sure your trips table has data within that range |

## Optional Enhancements

- Add charts (e.g. Plotly or Chart.js)
- Export filtered data as CSV
- Add authentication (Flask-Login)
- Containerize using Docker
- Deploy to AWS / Render / Railway

