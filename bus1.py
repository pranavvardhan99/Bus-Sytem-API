from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import logging

app = FastAPI()

# Postgres connection details
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'FinalBus'
DB_USER = 'postgres'
DB_PASSWORD = '310D60c9@'

# Define request body schema


class TransportRegistrationRequest(BaseModel):
    userid: str
    semstr_details_semester_sub_id: str


# Set up logger
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Define route to handle incoming requests


@app.post('/TR')
def get_transport_registration(request: TransportRegistrationRequest):
    # Extract parameters from request body
    user_id = request.userid
    sem_sub_id = request.semstr_details_semester_sub_id

    # Connect to Postgres
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except psycopg2.Error as e:
        # Log error and raise HTTPException if connection fails
        logging.error('Failed to connect to database')
        raise HTTPException(
            status_code=500, detail='Failed to connect to database')

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute SQL query with parameters
    try:
        cur.execute(
            "SELECT * FROM transport.transport_registration WHERE userid=%s AND semstr_details_semester_sub_id=%s", (
                user_id, sem_sub_id,)
        )
    except psycopg2.Error as e:
        # Rollback transaction and log error, then raise HTTPException if query fails
        conn.rollback()
        cur.close()
        conn.close()
        logging.error('Failed to execute query')
        raise HTTPException(status_code=500, detail='Failed to execute query')

    # Fetch column names
    columns = [desc[0] for desc in cur.description]

    # Fetch all rows of result
    rows = cur.fetchall()

    # Close database connection
    cur.close()
    conn.close()

    # If no rows were found, log error and return 404 response
    if len(rows) == 0:
        try:
            # Connect to Postgres
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )

            # Open a cursor to perform database operations
            cur = conn.cursor()

            # Execute SQL query to insert error details into bus_qr_scan_log table
            cur.execute(
                "INSERT INTO transport.bus_qr_scan_log (log_userid, semstr_details_semester_sub_id) VALUES (%s, %s)",
                (user_id, sem_sub_id,)
            )

            # Commit transaction and close database connection
            conn.commit()
            cur.close()
            conn.close()

        except psycopg2.Error as e:
            # Rollback transaction, log error, and raise HTTPException if query fails
            conn.rollback()
            cur.close()
            conn.close()
            logging.error('Failed to insert error details into database')
            raise HTTPException(
                status_code=500, detail='Failed to insert error details into database')

        raise HTTPException(
            status_code=404, detail='No records found for the given user id and semester subject id'
        )

    # Convert result to list of dictionaries with column names as keys
    result = [dict(zip(columns, row)) for row in rows]

    return result
