from typing import Any, List, Tuple, Union
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os

app: Flask = Flask(__name__)

DATABASE_NAME: str = os.path.join('database', 'holiday.db')

def database_setup() -> None:
    """Creates database and tables if they do not exist.
    """

    # create connection and cursor
    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    # read create statements from database_setup.sql
    with open(os.path.join('database', 'scripts', 'database_setup.sql'), 'r') as f:
        sql: str = f.read()

    # execute sql statements as script
    cursor.executescript(sql)

    # commit changes and close connection
    conn.commit()
    conn.close()

@app.route('/get_remaining_holidays/<email>')
def get_remaining_holidays(email: str) -> str:
    """Returns the remaining holidays for a user.

    Args:
        email (str): The email of the user.

    Returns:
        str: The remaining holidays for the user.
    """

    # create database connection and cursor
    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    with open(os.path.join('database', 'scripts', 'get_remaining_holiday.sql'), "r") as f:
        sql: str = f.read()

    # execute sql statement
    cursor.execute(sql, (email,))
    user: Any = cursor.fetchone()

    # close connection
    conn.close()

    # return remaining holidays
    return str(user[0])

@app.route('/reduce_remaining_holidays/<email>/<days>', methods=['GET', 'POST'])
def reduce_remaining_holidays(email: str, days: int) -> Union[redirect, str]:
    """Reduces the remaining holidays for a user.

    Args:
        email (str): The email of the user.
        days (int): The number of days to reduce the remaining holidays by.

    Returns:
        Union[redirect, str]: If GET request redirects to /get_remaining_holidays/<email>. If POST request returns 201 status code.
    """

    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    with open(os.path.join('database', 'scripts', 'reduce_remaining_holidays.sql'), "r") as f:
        sql: str = f.read()
    
    cursor.execute(sql, (days, days, email))

    # commit changes and close
    conn.commit()
    conn.close()

    # if GET request redirect to /get_remaining_holidays/<email>
    if request.method == 'GET':
        return redirect(url_for('get_remaining_holidays', email=email))

    # if POST request return 201 status code
    return '', 201

@app.route('/reset_remaining_holidays/<email>')
def reset_remaining_holidays(email: str) -> redirect:
    """Resets the remaining holidays for a user.

    Args:
        email (str): The email of the user.

    Returns:
        redirect: Redirects to /get_remaining_holidays/<email>.
    """

    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    with open(os.path.join('database', 'scripts', 'reset_remaining_holidays.sql'), "r") as f:
        sql: str = f.read()

    cursor.execute(sql, (email,))

    conn.commit()
    conn.close()

    return redirect(url_for('get_remaining_holidays', email=email))

@app.route('/book_holiday/<email>/<date>', methods=['POST'])
def book_holiday(email: str, date: str) -> Tuple[str]:
    """Books a holiday for a user.

    Args:
        email (str): The email of the user.
        date (str): The date of the holiday.

    Returns:
        str: Returns 201 status code if holiday is booked successfully.
    """

    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    with open(os.path.join('database', 'scripts', 'book_holiday.sql'), "r") as f:
        sql: sql = f.read()

    # if sqlite3.IntegrityError: UNIQUE constraint failed, early return 201 status code
    # if sqlite3.OperationalError : database is locked, early return 400 status code
    # if sqlite3.OperationalError : no such table: holiday, create table (run database_setup.sql) and try again

    inserted: bool = False

    try:
        cursor.execute(sql, (date, email))
        inserted = True
    except sqlite3.IntegrityError:
        return '', 201
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            return '', 400
        elif "no such table: holiday" in str(e):
            # rerun database_setup()
            database_setup()

            # try again
            cursor.execute(sql, (date, email))
    finally:
        if inserted:
            conn.commit()
            conn.close()

            # reduce users remaining holidays by 1
            reduce_remaining_holidays(email, 1)

    return '', 201

@app.route('/get_name/<email>')
def get_name(email: str) -> str:
    """Returns the name of a user.

    Args:
        email (str): The email of the user.

    Returns:
        str: The name of the user.
    """

    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    with open(os.path.join('database', 'scripts', 'get_name.sql'), "r") as f:
        sql: str = f.read()

    cursor.execute(sql, (email,))
    user: Any = cursor.fetchone()

    conn.close()

    return str(user[0])

@app.route('/get_holidays/<email>')
def get_holidays(email: str) -> str:
    """Returns the holidays for a user.

    Args:
        email (str): The email of the user.

    Returns:
        str: The holidays for the user.
    """

    conn: sqlite3.Connection = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
    cursor: sqlite3.Cursor = conn.cursor()

    with open(os.path.join('database', 'scripts', 'get_holidays.sql'), "r") as f:
        sql: str = f.read()

    cursor.execute(sql, (email,))
    holidays: List[Any] = cursor.fetchall()

    conn.close()

    return str(holidays)

# run app
if __name__ == '__main__':
    database_setup()
    app.run(debug=True)

