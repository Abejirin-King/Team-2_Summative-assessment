import pandas as pd

df = pd.read_csv("yellow_tripdata.csv")

columns_to_keep = [
    "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
    "passenger_count", "trip_distance", "RatecodeID",
    "PULocationID", "DOLocationID", "payment_type",
    "fare_amount", "extra", "mta_tax", "tip_amount",
    "tolls_amount", "improvement_surcharge", "total_amount"
]
df = df[columns_to_keep]

df.dropna(inplace=True)

df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce")

df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])

df["trip_duration_min"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60

df.to_csv("cleaned_data.csv", index=False)

print("✅ cleaned_data.csv created successfully!")
