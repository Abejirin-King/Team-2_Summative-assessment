from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    'user': 'etl_user',
    'password': 'King40$$',
    'host': '127.0.0.1',
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
    min_fare = float(request.args.get('min_fare', 0))
    max_fare = float(request.args.get('max_fare', 200))
    sort_by = request.args.get('sort_by', 'pickup_dt')

    if not start_date or not end_date:
        return jsonify({'error': 'Missing start or end date'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        summary_query = """
            SELECT 
                COUNT(*) AS total_trips,
                ROUND(AVG(total_amount), 2) AS avg_fare,
                ROUND(AVG(trip_distance * 1.60934), 2) AS avg_distance_km,
                ROUND(AVG(
                    (trip_distance * 1.60934) / 
                    (TIME_TO_SEC(TIMEDIFF(dropoff_dt, pickup_dt)) / 3600)
                ), 2) AS avg_speed_kmph
            FROM trips
            WHERE pickup_dt BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY)
            AND total_amount BETWEEN %s AND %s
        """
        cur.execute(summary_query, (start_date, end_date, min_fare, max_fare))
        summary = cur.fetchone()

        details_query = f"""
            SELECT 
                pickup_dt,
                dropoff_dt,
                ROUND(trip_distance * 1.60934, 2) AS trip_distance_km,
                total_amount,
                ROUND(
                    (trip_distance * 1.60934) / 
                    (TIME_TO_SEC(TIMEDIFF(dropoff_dt, pickup_dt)) / 3600),
                    2
                ) AS trip_speed_kmph
            FROM trips
            WHERE pickup_dt BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY)
            AND total_amount BETWEEN %s AND %s
            ORDER BY {sort_by} DESC
            LIMIT 100
        """
        cur.execute(details_query, (start_date, end_date, min_fare, max_fare))
        trips = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'summary': summary, 'trips': trips})

    except Error as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

