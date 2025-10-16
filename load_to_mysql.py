import os
import json
import mysql.connector
import pandas as pd
from mysql.connector import errorcode
from datetime import datetime
from dotenv import load_dotenv

print("Script started")

load_dotenv()

DB_USER = os.getenv("DB_USER", "etl_user")
DB_PASS = os.getenv("DB_PASS", "King40$$")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "taxi_data")
DB_PORT = int(os.getenv("DB_PORT", 3306))

CLEANED_CSV = "cleaned_data.csv"
BATCH_SIZE = 5000

def connect_db():
    try:
        return mysql.connector.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            database=DB_NAME,
            port=DB_PORT
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise

def log_ingest_error(cur, reason, raw_row):
    raw_json = json.dumps({k: str(v) for k, v in raw_row.items()}, ensure_ascii=False)
    cur.execute(
        "INSERT INTO ingest_log (error_reason, raw_data) VALUES (%s, %s)",
        (reason[:255], raw_json)
    )

def row_to_tuple(row):
    def safe_float(v):
        if pd.isna(v): return None
        try:
            return float(v)
        except:
            return None

    def safe_int(v):
        if pd.isna(v): return None
        try:
            return int(v)
        except:
            return None

    def safe_dt(v):
        if pd.isna(v): return None
        return pd.to_datetime(v).to_pydatetime().replace(tzinfo=None)

    pickup = safe_dt(row.get("tpep_pickup_datetime"))
    dropoff = safe_dt(row.get("tpep_dropoff_datetime"))

    duration_s = None
    speed_kmph = None
    distance = safe_float(row.get("trip_distance"))

    if pickup and dropoff:
        duration_s = (dropoff - pickup).total_seconds()
        if duration_s > 0 and distance:
            speed_kmph = (distance * 1.609) / (duration_s / 3600)
            if speed_kmph > 200 or speed_kmph < 0:
                speed_kmph = None

    distance_km = distance * 1.609 if distance else None

    return (
        safe_int(row.get("VendorID")),
        pickup,
        dropoff,
        safe_int(row.get("passenger_count")),
        distance,
        distance_km,
        duration_s,
        speed_kmph,
        safe_float(row.get("fare_amount")),
        safe_float(row.get("extra")),
        safe_float(row.get("mta_tax")),
        safe_float(row.get("tip_amount")),
        safe_float(row.get("tolls_amount")),
        safe_float(row.get("improvement_surcharge")),
        safe_float(row.get("total_amount")),
        None, 
        None,  
        None,  
        None,  
        None,  
        None,  
        None,  
        None,  
        False, 
        safe_int(row.get("PULocationID")),
        safe_int(row.get("DOLocationID")),
        safe_int(row.get("RatecodeID")),
        safe_int(row.get("payment_type"))
    )

def build_insert_sql():
    cols = [
        "vendor_id","pickup_dt","dropoff_dt","passenger_count",
        "trip_distance","trip_distance_km","trip_duration_s","trip_speed_kmph",
        "fare_amount","extra","mta_tax","tip_amount","tolls_amount",
        "improvement_surcharge","total_amount",
        "airport_fee","cbd_congestion_fee","fare_per_km","tip_pct",
        "pickup_hour","pickup_weekday","estimated_moving_time_s",
        "estimated_idle_time_s","suspicious_flag","pu_location_id",
        "do_location_id","rate_code_id","payment_type_id"
    ]
    placeholders = ", ".join(["%s"] * len(cols))
    ondup = """
        ON DUPLICATE KEY UPDATE 
        total_amount=VALUES(total_amount),
        tip_amount=VALUES(tip_amount)
    """
    return f"INSERT INTO trips ({', '.join(cols)}) VALUES ({placeholders}) {ondup}"

def main():
    print("Step 1: Checking if CSV exists...")
    if not os.path.exists(CLEANED_CSV):
        raise FileNotFoundError(f"{CLEANED_CSV} not found.")
    print("CSV file found")

    print("Step 2: Connecting to database...")
    conn = connect_db()
    cur = conn.cursor(buffered=True)
    print("Connected to database")

    insert_sql = build_insert_sql()
    total_inserted = 0
    total_errors = 0

    print("Step 3: Reading CSV in chunks...")
    for chunk_index, chunk in enumerate(pd.read_csv(
        CLEANED_CSV,
        chunksize=BATCH_SIZE,
        low_memory=False
    )):
        print(f"➡ Processing chunk {chunk_index + 1} with {len(chunk)} rows")

        rows_to_insert = []
        for i, (_, row) in enumerate(chunk.iterrows()):
            try:
                tup = row_to_tuple(row)
                if len(tup) != 29:
                    raise ValueError(f"Tuple length {len(tup)} != 29")
                rows_to_insert.append(tup)
            except Exception as e:
                total_errors += 1
                log_ingest_error(cur, f"Row error: {str(e)}", row.to_dict())

        if not rows_to_insert:
            continue

        try:
            cur.executemany(insert_sql, rows_to_insert)
            conn.commit()
            total_inserted += len(rows_to_insert)
            print(f"Inserted {len(rows_to_insert)} rows in chunk {chunk_index + 1}")
        except mysql.connector.Error as err:
            conn.rollback()
            total_errors += len(rows_to_insert)
            print(f"MySQL insert failed: {err}")
            for r in rows_to_insert:
                log_ingest_error(cur, f"MySQL insert failed: {str(err)}", {"row_tuple": str(r)})
            conn.commit()

    cur.close()
    conn.close()
    print(f"Done! Inserted: {total_inserted}, Errors: {total_errors}")

if __name__ == "__main__":
    main()


