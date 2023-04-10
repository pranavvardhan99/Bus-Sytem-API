from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI()

# Postgres connection details
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'app pro'
DB_USER = 'postgres'
DB_PASSWORD = '310D60c9@'

# Define request body schema


class TransportRegistrationRequest(BaseModel):
    userid: str
    semstr_details_semester_sub_id: str

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
        # Raise HTTPException if connection fails
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
        # Rollback transaction and raise HTTPException if query fails
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=500, detail='Failed to execute query')

    # Fetch column names
    columns = [desc[0] for desc in cur.description]

    # Fetch all rows of result
    rows = cur.fetchall()

    # Close database connection
    cur.close()
    conn.close()

    # Raise HTTPException if no rows were found
    if len(rows) == 0:
        raise HTTPException(
            status_code=404, detail='No records found for the given user id and semester subject id'
        )

    # Convert result to list of dictionaries with column names as keys
    result = [dict(zip(columns, row)) for row in rows]

    return result
