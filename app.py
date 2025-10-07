from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    'user': 'etl_user',
    'password': 'King40$$',
    'host': 'localhost',
    'database': 'taxi_data',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trips', methods=['GET'])
def get_trips():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    min_fare = request.args.get('min_fare', 0)
    max_fare = request.args.get('max_fare', 1000)
    sort_by = request.args.get('sort_by', 'pickup_dt')

    if not start_date or not end_date:
        return jsonify({'error': 'Missing start or end date'}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Main summary query
    query_summary = f"""
        SELECT 
            COUNT(*) AS total_trips,
            ROUND(AVG(total_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance_km), 2) AS avg_distance,
            ROUND(AVG(trip_speed_kmph), 2) AS avg_speed
        FROM trips
        WHERE pickup_dt BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY)
        AND total_amount BETWEEN %s AND %s
    """
    cur.execute(query_summary, (start_date, end_date, min_fare, max_fare))
    summary = cur.fetchone()

    # Detailed trips for table display
    query_details = f"""
        SELECT 
            pickup_dt, dropoff_dt, trip_distance_km, total_amount, trip_speed_kmph
        FROM trips
        WHERE pickup_dt BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY)
        AND total_amount BETWEEN %s AND %s
        ORDER BY {sort_by} DESC
        LIMIT 100
    """
    cur.execute(query_details, (start_date, end_date, min_fare, max_fare))
    trips = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        'summary': summary,
        'trips': trips
    })

if __name__ == '__main__':
    app.run(debug=True)
