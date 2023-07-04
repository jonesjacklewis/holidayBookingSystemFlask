# Create email object
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from datetime import datetime, timedelta
from typing import Any, List
import requests
import os


DATE_FORMAT: str = "%Y-%m-%d"


def create_test_email() -> MIMEMultipart:
    """Creates a test email object

    Returns:
        MIMEMultipart: A test email object
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg: MIMEMultipart = MIMEMultipart("alternative")

    # Create the body of the message (a plain-text and an HTML version).

    with open(os.path.join("examples", "plain_text_body_example.txt"), "r") as f:
        plain_text_body: str = f.read()

    with open(os.path.join("examples", "html_body_example.html"), "r") as f:
        html_body: str = f.read()

    msg.attach(MIMEText(plain_text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # add sender
    msg["From"] = "test.user@domain.com"

    return msg


def extract_plain_text_body(msg: MIMEMultipart) -> Any:
    """Extracts the plain text body from an email object

    Args:
        msg (MIMEMultipart): An email object

    Returns:
        Any: The plain text body of the email
    """
    return next(
        (
            part.get_payload()
            for part in msg.walk()
            if part.get_content_type() == "text/plain"
        ),
        None,
    )


def extract_sender(msg: MIMEMultipart) -> str:
    """Extracts the sender from an email object

    Args:
        msg (MIMEMultipart): An email object

    Returns:
        str: The sender of the email
    """
    return msg["From"]


def extract_dates(plain_text_body: str) -> List[datetime]:
    """Extracts dates from a plain text body

    Args:
        plain_text_body (str): The plain text body of an email

    Returns:
        List[datetime]: A list of dates
    """

    # date format 2023-08-01
    date_regex: re.Pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

    dates: List[Any] = date_regex.findall(plain_text_body)

    # convert to datetime objects
    dates: List[datetime] = [datetime.strptime(date, DATE_FORMAT) for date in dates]

    return dates


def generate_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Generates a list of dates between a start and end date

    Args:
        start_date (datetime): The start date of the range
        end_date (datetime): The end date of the range

    Returns:
        List[datetime]: A list of dates between the start and end date (inclusive)
    """

    date_range: List[datetime] = []
    current_date: datetime = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    return date_range


def remove_weekends(date_range: List[datetime]) -> List[datetime]:
    """Removes weekends from a list of dates

    Args:
        date_range (List[datetime]): A list of dates

    Returns:
        List[datetime]: A list of dates with weekends removed
    """
    return [date for date in date_range if date.weekday() < 5]


def remove_bank_holidays(date_range: List[datetime]) -> List[datetime]:
    """Removes bank holidays from a list of dates

    Args:
        date_range (List[datetime]): A list of dates

    Returns:
        List[datetime]: A list of dates with bank holidays removed
    """
    endpoint: str = "https://www.gov.uk/bank-holidays.json"

    response: requests.Response = requests.get(endpoint)

    bank_holidays: Any = response.json()

    bank_holidays: Any = bank_holidays["england-and-wales"]["events"]

    bank_holidays: List[datetime] = [
        datetime.strptime(holiday["date"], DATE_FORMAT) for holiday in bank_holidays
    ]

    return [date for date in date_range if date not in bank_holidays]


def book_holidays(sender: str, days: List[datetime]) -> None:
    """Books holidays for a given sender on a list of dates

    Args:
        sender (str): The sender of the email
        days (List[datetime]): A list of dates to book holidays for
    """
    endpoint: str = f"http://127.0.0.1:5000/book_holiday/{sender}/{{date}}"

    for date in days:
        requests.post(endpoint.format(date=date.strftime(DATE_FORMAT)))


def get_remaining_holidays(sender: str) -> int:
    """Gets the number of remaining holidays for a given sender

    Args:
        sender (str): The sender of the email

    Returns:
        int: The number of remaining holidays
    """
    endpoint: str = f"http://127.0.0.1:5000/get_remaining_holidays/{sender}"

    response: requests.Response = requests.get(endpoint)

    return int(response.text)


def get_sender_name(sender: str) -> str:
    """Gets the name of a sender

    Args:
        sender (str): The sender of the email

    Returns:
        str: The name of the sender
    """
    endpoint: str = f"http://127.0.0.1:5000/get_name/{sender}"

    response: requests.Response = requests.get(endpoint)

    return response.text


def create_response_email(
    recipient_email: str,
    recipient_name: str,
    remaining_days: int,
    days_booked: List[datetime],
) -> MIMEMultipart:
    """Creates a response email

    Args:
        recipient_email (str): The email address of the recipient
        recipient_name (str): The name of the recipient
        remaining_days (int): The number of remaining holidays
        days_booked (List[datetime]): A list of dates that have been booked

    Returns:
        MIMEMultipart: A response email
    """
    msg: MIMEMultipart = MIMEMultipart("alternative")

    with open(os.path.join("templates", "plain_text_response_template.txt"), "r") as f:
        plain_text_body: str = f.read()

    days_booked_message: str = "".join(
        f"- {day.strftime('%A %d %B %Y')}\n" for day in days_booked
    )
    days_booked_message = days_booked_message[:-1]

    plain_text_body = plain_text_body.format(
        recipient_name, remaining_days, days_booked_message
    )

    with open(os.path.join("templates", "html_body_response_template.html"), "r") as f:
        html_body: str = f.read()

    days_booked_message = "<ul>"

    for day in days_booked:
        # add an li tag for each day
        days_booked_message += f"<li>{day.strftime('%A %d %B %Y')}</li>"

    days_booked_message += "</ul>"

    html_body = html_body.format(recipient_name, remaining_days, days_booked_message)

    msg.attach(MIMEText(plain_text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    msg["From"] = "holidays@domain.com"
    msg["To"] = recipient_email

    return msg


def write_email_to_file(
    email: MIMEMultipart, filename: str = "example", test: bool = False
) -> None:
    """Writes an email to a file

    Args:
        email (MIMEMultipart): The email to write to a file
        filename (str, optional): The name of the file to write. Defaults to "example".
        test (bool, optional): Whether or not the program is in test. Defaults to False.
    """
    path: str = "examples" if test else "output"
    with open(os.path.join(path, f"{filename}.txt"), "w") as f:
        f.write(email.as_string())


def main() -> None:
    """The main function"""

    # Create the message
    message: MIMEMultipart = create_test_email()

    plain: Any = extract_plain_text_body(message)
    sender: str = extract_sender(message)

    dates: List[datetime] = extract_dates(plain)

    start_date: datetime = min(dates)
    end_date: datetime = max(dates)

    date_range: List[datetime] = generate_date_range(start_date, end_date)

    working_days: List[datetime] = remove_weekends(date_range)

    working_days = remove_bank_holidays(working_days)

    book_holidays(sender, working_days)

    remaining_holidays: int = get_remaining_holidays(sender)
    name: str = get_sender_name(sender)

    response_email: MIMEMultipart = create_response_email(
        sender, name, remaining_holidays, working_days
    )

    write_email_to_file(response_email, test=True)


if __name__ == "__main__":
    main()
