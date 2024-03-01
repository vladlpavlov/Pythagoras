from datetime import datetime, timezone


def current_date_gmt_string():
    """ Return the current date and time in the format '2024_12Jan_22_utc'
    """
    # Get the current date and time in UTC (GMT)
    utc_now = datetime.now(timezone.utc)

    # Format the date as specified: "2024_12Jan_22"
    # Using %b for abbreviated month name
    date_str = utc_now.strftime("%Y_%m%b_%d_utc")

    return date_str