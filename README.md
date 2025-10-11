# 🚖 NYC Taxi Trip Dashboard

An interactive **Flask-based web app** for analyzing New York City taxi trip data.  
The app loads data from a MySQL database, provides API endpoints for filtering,  
and renders an interactive dashboard (table or charts) in the browser.

---

## 📁 Project Structure

```
NYC_taxi_app/
│
├── app.py                   # Main Flask app (runs backend + routes)
├── load_to_mysql.py         # Script for loading CSV data into MySQL
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
│
├── database/
│   └── schema.sql           # SQL file defining table structure
│
├── static/                  # Static frontend assets
│   ├── style.css            # Dashboard styling
│   └── dashboard.js         # JS logic for fetching and displaying data
│
└── templates/
    └── index.html           # HTML template for Flask rendering
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/NYC_taxi_app.git
cd NYC_taxi_app
```

---

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate  # macOS/Linux
```

---

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Set up your database
Make sure you have **MySQL** installed and running.

Create a database:
```sql
CREATE DATABASE nyc_taxi;
USE nyc_taxi;
```

Then execute the schema file:
```sql
SOURCE database/schema.sql;
```

---

### 5. Load data into MySQL
You can load your CSV data into MySQL using:

```bash
python load_to_mysql.py
```

Make sure your connection details inside `load_to_mysql.py` are correct:
```python
engine = create_engine("mysql+pymysql://root:yourpassword@localhost/nyc_taxi")
```

---

### 6. Run the Flask app
Start the server:
```bash
python app.py
```

If successful, you’ll see:
```
Running on http://127.0.0.1:5000/
```

---

### 7. Open the Dashboard
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

You’ll see the dashboard page served from `templates/index.html`,  
which loads its logic and styling from the `/static/` folder.

---

## 🧩 Features

✅ Filter by:
- **Trip Duration**  
- **Fare Amount**  
- **Trip Distance**  
- **Pickup & Dropoff Locations**

✅ Display results in a **table format** (with sorting and pagination)

✅ Fetches data dynamically from Flask API endpoints (`/filter`)

✅ Responsive and minimalist **CSS dashboard layout**

---

## 📊 Example API Request

**Endpoint:**
```
GET /filter?min_duration=5&max_duration=30
```

**Response:**
```json
{
  "total_trips": 812,
  "avg_duration": 18.5,
  "avg_distance": 4.2,
  "avg_fare": 14.8
}
```

---

## 🧰 Tech Stack

| Layer        | Technology |
|--------------|-------------|
| **Backend**  | Python (Flask, SQLAlchemy, Pandas) |
| **Database** | MySQL |
| **Frontend** | HTML, CSS, JavaScript |
| **Visualization** | Table rendering via DOM |
| **Environment** | venv / dotenv |

---

## 🚀 Future Improvements
- Add map-based pickup/dropoff visualization  
- Include charts for fare vs. distance trends  
- Pagination for large result sets  
- Deploy with Docker or Render  

---

## 🧑‍💻 Author

**King Obafemi Abejirin**  
Made with ❤️ using Python, Flask, and MySQL.
