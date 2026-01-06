#SQLite for local app and demos and zero setup

import sqlite3
from datetime import datetime
import json

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
        ticker TEXT,
        spot_price REAL,
        strike_price REAL,
        time_to_maturity REAL,
        volatility REAL,
        risk_free_rate REAL,
        option_type TEXT,
        option_price REAL,
        delta REAL,
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
    ticker,
    spot_price,
    strike_price,
    time_to_maturity,
    volatility,
    risk_free_rate,
    option_type,
    option_price,
    delta,
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
        ticker,
        spot_price,
        strike_price,
        time_to_maturity,
        volatility,
        risk_free_rate,
        option_type,
        option_price,
        delta,
        gamma,
        theta,
        vega,
        rho
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(),
        ticker,
        spot_price,
        strike_price,
        time_to_maturity,
        volatility,
        risk_free_rate,
        option_type,
        option_price,
        delta,
        gamma,
        theta,
        vega,
        rho
    ))

    conn.commit()
    conn.close()


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
        call_heatmap TEXT,
        put_heatmap TEXT,
        vol_shock REAL,
        call_pnl TEXT,
        put_pnl TEXT,
        timestamp TEXT,
        FOREIGN KEY(input_id) REFERENCES option_calculations(id)
    )
    """)

    conn.commit()
    conn.close()

def save_output(input_id, call_grid, put_grid, vol_shock, call_pnl, put_pnl):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO option_outputs (
        input_id,
        call_heatmap,
        put_heatmap,
        vol_shock,
        call_pnl,
        put_pnl,
        timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        input_id,
        json.dumps(call_grid.tolist()),   # convert numpy array to list -> JSON
        json.dumps(put_grid.tolist()),
        vol_shock,
        json.dumps(call_pnl.tolist()),
        json.dumps(put_pnl.tolist()),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def initialize_db():
    create_table()
    create_output_table()

def get_outputs(input_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM options_outputs
        WHERE input_id = ?
    """, (input_id,))
    row = cursor.fetchone()
    conn.close()
    return row
    