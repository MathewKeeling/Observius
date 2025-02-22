import datetime


def get_current_datetime() -> str:
    """Returns the current date and time in the format: 'Monday July 18, 2024, 15:30:00'."""
    return datetime.datetime.now().strftime("%A %B %d, %Y, %H:%M:%S")


def get_current_date_time_sqlite() -> str:
    """Returns the current date and time in the format: '2024-07-18 15:30:00'."""
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


if __name__ == "__main__":
    print("This file is running directly.")
