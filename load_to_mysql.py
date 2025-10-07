import os
import json
import mysql.connector
import pandas as pd
from mysql.connector import errorcode
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # optional .env support

DB_USER = "etl_user"
DB_PASS = "King40$$"
DB_HOST = "127.0.0.1"
DB_NAME = "taxi_data"
DB_PORT =  3306

CLEANED_CSV = "cleaned_data.csv"
BATCH_SIZE = 5000

def connect_db():
    return mysql.connector.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        database=DB_NAME,
        port=DB_PORT
    )

def upsert_lookup(cur, table, pk_col, pk_val, extra_cols=None):
    if pk_val is None:
        return
    extra_cols = extra_cols or {}
    cols = [pk_col] + list(extra_cols.keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    update_list = ", ".join([f"{c}=VALUES({c})" for c in extra_cols.keys()]) or f"{pk_col}={pk_col}"
    sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_list}"
    params = [pk_val] + list(extra_cols.values())
    cur.execute(sql, params)

def log_ingest_error(cur, reason, raw_row, trip_hash=None, attempts=0):
    safe_dict = {}
    for k, v in raw_row.items():
        try:
            if pd.isna(v):
                safe_dict[k] = None
            elif isinstance(v, (pd.Timestamp, datetime)):
                safe_dict[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            else:
                safe_dict[k] = str(v)
        except Exception:
            safe_dict[k] = None

    raw_json = json.dumps(safe_dict, ensure_ascii=False)
    sql = "INSERT INTO ingest_log (error_reason, raw_data, trip_unique_hash, attempts) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (reason[:255], raw_json, trip_hash, attempts))

def row_to_tuple(row):
    def safe_int(k):
        v = row.get(k)
        if pd.isna(v):
            return None
        return int(v)
    def safe_float(k):
        v = row.get(k)
        if pd.isna(v):
            return None
        return float(v)
    def safe_dt(k):
        v = row.get(k)
        if pd.isna(v):
            return None
        return pd.to_datetime(v).to_pydatetime().replace(tzinfo=None)
    return (
        safe_int("VendorID"),
        safe_dt("pickup_dt"),
        safe_dt("dropoff_dt"),
        safe_int("passenger_count"),
        safe_float("trip_distance"),
        safe_float("trip_distance_km"),
        safe_int("trip_duration_s"),
        safe_float("trip_speed_kmph"),
        safe_float("fare_amount"),
        safe_float("extra") if "extra" in row else None,
        safe_float("mta_tax") if "mta_tax" in row else None,
        safe_float("tip_amount") if "tip_amount" in row else None,
        safe_float("tolls_amount") if "tolls_amount" in row else None,
        safe_float("improvement_surcharge") if "improvement_surcharge" in row else None,
        safe_float("total_amount") if "total_amount" in row else None,
        safe_float("congestion_surcharge") if "congestion_surcharge" in row else None,
        safe_float("Airport_fee") if "Airport_fee" in row else None,
        safe_float("cbd_congestion_fee") if "cbd_congestion_fee" in row else None,
        safe_float("fare_per_km") if "fare_per_km" in row else None,
        safe_float("tip_pct") if "tip_pct" in row else None,
        safe_int("pickup_hour") if "pickup_hour" in row else None,
        row.get("pickup_weekday") if "pickup_weekday" in row and not pd.isna(row.get("pickup_weekday")) else None,
        safe_int("estimated_moving_time_s") if "estimated_moving_time_s" in row else None,
        safe_int("estimated_idle_time_s") if "estimated_idle_time_s" in row else None,
        bool(row["suspicious_flag"]) if "suspicious_flag" in row and not pd.isna(row["suspicious_flag"]) else False,
        safe_int("PULocationID") if "PULocationID" in row else None,
        safe_int("DOLocationID") if "DOLocationID" in row else None,
        safe_int("RatecodeID") if "RatecodeID" in row else None,
        safe_int("payment_type") if "payment_type" in row else None
    )

def build_insert_sql():
    cols = [
        "vendor_id","pickup_dt","dropoff_dt","passenger_count","trip_distance","trip_distance_km",
        "trip_duration_s","trip_speed_kmph","fare_amount","extra","mta_tax","tip_amount","tolls_amount",
        "improvement_surcharge","total_amount","congestion_surcharge","airport_fee","cbd_congestion_fee",
        "fare_per_km","tip_pct","pickup_hour","pickup_weekday","estimated_moving_time_s",
        "estimated_idle_time_s","suspicious_flag","pu_location_id","do_location_id","rate_code_id","payment_type_id"
    ]
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    ondup = "ON DUPLICATE KEY UPDATE total_amount=VALUES(total_amount), tip_amount=VALUES(tip_amount), suspicious_flag=VALUES(suspicious_flag)"
    sql = f"INSERT INTO trips ({col_list}) VALUES ({placeholders}) {ondup}"
    return sql

def main():
    if not os.path.exists(CLEANED_CSV):
        raise FileNotFoundError(f"{CLEANED_CSV} not found in cwd.")

    conn = connect_db()
    cur = conn.cursor(buffered=True)
    insert_sql = build_insert_sql()
    total_inserted = 0
    total_errors = 0

    for chunk in pd.read_csv(
    CLEANED_CSV,
    chunksize=BATCH_SIZE,
    low_memory=False,
    parse_dates=['pickup_dt', 'dropoff_dt'],
    date_format='%Y-%m-%d %H:%M:%S'
):

        rows_to_insert = []
        for _, row in chunk.iterrows():
            try:
                if not pd.isna(row.get('VendorID')):
                    upsert_lookup(cur, "vendors", "vendor_id", int(row['VendorID']))
                if 'RatecodeID' in row and not pd.isna(row['RatecodeID']):
                    upsert_lookup(cur, "rate_codes", "rate_code_id", int(row['RatecodeID']))
                if 'payment_type' in row and not pd.isna(row['payment_type']):
                    upsert_lookup(cur, "payment_types", "payment_type_id", int(row['payment_type']))
                if 'PULocationID' in row and not pd.isna(row['PULocationID']):
                    upsert_lookup(cur, "locations", "location_id", int(row['PULocationID']))
                if 'DOLocationID' in row and not pd.isna(row['DOLocationID']):
                    upsert_lookup(cur, "locations", "location_id", int(row['DOLocationID']))
            except Exception as e:
                log_ingest_error(cur, f"lookup_upsert_failed: {str(e)}", row.to_dict())
                conn.commit()
                total_errors += 1
                continue

            try:
                tup = row_to_tuple(row)
                rows_to_insert.append(tup)
            except Exception as e:
                log_ingest_error(cur, f"row_map_failed: {str(e)}", row.to_dict())
                conn.commit()
                total_errors += 1
                continue

        if not rows_to_insert:
            continue

        try:
            cur.executemany(insert_sql, rows_to_insert)
            conn.commit()
            total_inserted += len(rows_to_insert)
        except mysql.connector.Error as err:
            conn.rollback()
            total_errors += len(rows_to_insert)
            for r in rows_to_insert:
                log_ingest_error(cur, f"insert_failed: {str(err)}", {"row_tuple": str(r)})
            conn.commit()

    cur.close()
    conn.close()
    print(f"Completed. inserted (attempted): {total_inserted}, errors logged: {total_errors}")

if __name__ == "__main__":
    main()
