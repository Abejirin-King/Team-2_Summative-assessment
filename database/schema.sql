USE taxi_data;

CREATE TABLE IF NOT EXISTS vendors (
  vendor_id INT PRIMARY KEY,
  vendor_name VARCHAR(128) DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rate_codes (
  rate_code_id INT PRIMARY KEY,
  description VARCHAR(128) DEFAULT NULL
) ENGINE=InnoDB;

-- Payment types
CREATE TABLE IF NOT EXISTS payment_types (
  payment_type_id INT PRIMARY KEY,
  description VARCHAR(128) DEFAULT NULL
) ENGINE=InnoDB;

-- Locations
CREATE TABLE IF NOT EXISTS locations (
  location_id INT PRIMARY KEY,
  zone VARCHAR(128),
  borough VARCHAR(64)
) ENGINE=InnoDB;

-- Trips table aligned with yellow_tripdata.csv
CREATE TABLE IF NOT EXISTS trips (
  trip_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  vendor_id INT NOT NULL,
  pickup_dt DATETIME(6) NOT NULL,             -- from tpep_pickup_datetime
  dropoff_dt DATETIME(6) NOT NULL,            -- from tpep_dropoff_datetime
  passenger_count SMALLINT,
  trip_distance DECIMAL(8,3),
  trip_distance_km DECIMAL(8,3),              
  trip_duration_s INT,                        
  trip_speed_kmph DECIMAL(6,3),               
  fare_amount DECIMAL(9,2),
  extra DECIMAL(9,2),
  mta_tax DECIMAL(9,2),
  tip_amount DECIMAL(9,2),
  tolls_amount DECIMAL(9,2),
  improvement_surcharge DECIMAL(9,2),
  total_amount DECIMAL(9,2),
  congestion_surcharge DECIMAL(9,2),
  airport_fee DECIMAL(9,2),
  fare_per_km DECIMAL(9,3),
  tip_pct DECIMAL(5,4),
  pickup_hour TINYINT,
  pickup_weekday VARCHAR(16),
  rate_code_id INT DEFAULT NULL,              
  payment_type_id INT DEFAULT NULL,           
  pu_location_id INT,                         
  do_location_id INT,                         
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_trip_compound (
    vendor_id, pickup_dt, dropoff_dt,
    pu_location_id, do_location_id,
    passenger_count, trip_distance, fare_amount
  ),
  FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  FOREIGN KEY (payment_type_id) REFERENCES payment_types(payment_type_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  FOREIGN KEY (pu_location_id) REFERENCES locations(location_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  FOREIGN KEY (do_location_id) REFERENCES locations(location_id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED;

CREATE TABLE IF NOT EXISTS ingest_log (
  log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ingest_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  error_reason VARCHAR(255),
  raw_data JSON,
  trip_unique_hash VARCHAR(128) NULL,
  attempts INT DEFAULT 0
) ENGINE=InnoDB;

CREATE INDEX idx_trips_pickup_dt ON trips(pickup_dt);
CREATE INDEX idx_trips_pu ON trips(pu_location_id);
CREATE INDEX idx_trips_do ON trips(do_location_id);
CREATE INDEX idx_trips_speed ON trips(trip_speed_kmph);
CREATE INDEX idx_trips_fare ON trips(total_amount);
CREATE INDEX idx_trips_pickup_compound ON trips(pickup_dt, pu_location_id);
