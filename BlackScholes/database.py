#SQLite for local app and demos and zero setup

import sqlite3
from datetime import datetime
import json
import numpy as np

DB_NAME = "option_calculations.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

#separate db logic for moduclar architecture
def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS option_calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        spot_price REAL,
        strike_price REAL,
        time_to_maturity REAL,
        volatility REAL,
        risk_free_rate REAL,
        option_type TEXT,
        option_price REAL,
        call_delta REAL,
        put_delta REAL,
        gamma REAL,
        theta REAL,
        vega REAL,
        rho REAL
    )
    """)

    conn.commit()
    conn.close()

#writes one row to DB, input + output
def save_calculation(
    spot_price,
    strike_price,
    time_to_maturity,
    volatility,
    risk_free_rate,
    option_type,
    option_price,
    call_delta,
    put_delta,
    gamma,
    theta,
    vega,
    rho
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO option_calculations (
        timestamp,
        spot_price,
        strike_price,
        time_to_maturity,
        volatility,
        risk_free_rate,
        option_type,
        option_price,
        call_delta,
        put_delta,
        gamma,
        theta,
        vega,
        rho
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(),
        spot_price,
        strike_price,
        time_to_maturity,
        volatility,
        risk_free_rate,
        option_type,
        option_price,
        call_delta,
        put_delta,
        gamma,
        theta,
        vega,
        rho
    ))

    conn.commit()
    input_id = cursor.lastrowid
    conn.close()
    return input_id


def get_calculations(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
    SELECT * FROM option_calculations
    ORDER BY timestamp DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def create_output_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS option_outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_id INTEGER,
        spot_price REAL,
        volatility REAL,
        call_price REAL,
        put_price REAL,
        call_pnl TEXT,
        put_pnl TEXT,
        timestamp TEXT,
        FOREIGN KEY(input_id) REFERENCES option_calculations(id)
    )
    """)

    conn.commit()
    conn.close()

def save_output(input_id, spot_price, volatility, call_price, put_price, call_pnl, put_pnl):
    conn = get_connection()
    cursor = conn.cursor()

    # Convert numpy arrays to JSON strings
    call_pnl_json = json.dumps(call_pnl.tolist()) if isinstance(call_pnl, np.ndarray) else json.dumps(call_pnl)
    put_pnl_json = json.dumps(put_pnl.tolist()) if isinstance(put_pnl, np.ndarray) else json.dumps(put_pnl)
    

    cursor.execute("""
        INSERT INTO option_outputs (
            input_id,
            spot_price,
            volatility,
            call_price,
            put_price,
            call_pnl,
            put_pnl,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        input_id,
        spot_price,
        volatility,
        call_price,
        put_price,
        call_pnl_json,
        put_pnl_json,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def initialize_db():
    create_table()
    create_output_table()

def get_outputs(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.id,
            o.input_id,
            o.spot_price,
            c.strike_price,
            o.volatility,
            o.call_price,
            o.put_price,
            o.call_pnl,
            o.put_pnl,
            o.timestamp
        FROM option_outputs o
        JOIN option_calculations c
        ON o.input_id = c.id
        ORDER BY o.timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    
    # Parse PnL and calculate max values
    processed_rows = []
    for row in rows:
        try:
            call_pnl_array = json.loads(row[7]) if row[7] else []
            put_pnl_array = json.loads(row[8]) if row[8] else []
            
            max_call_pnl = max(call_pnl_array) if call_pnl_array else 0
            max_put_pnl = max(put_pnl_array) if put_pnl_array else 0
            
            processed_rows.append([
                row[0],  # id
                row[1],  # input_id
                row[2],  # spot_price
                row[3],  # strike_price
                row[4],  # volatility
                row[5],  # call_price
                row[6],  # put_price
                max_call_pnl,  # max call pnl
                max_put_pnl,   # max put pnl
                row[9]   # timestamp
            ])
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # Skip corrupted rows
            print(f"Skipping corrupted row {row[0]}: {e}")
            continue
    
    return processed_rows
