from datetime import datetime, timezone
from pythagoras._05_mission_control.events_and_exceptions import get_current_date_gmt

def test_return_type():
    """ Test if the return type is a tuple of three strings """
    result = get_current_date_gmt()
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 3, "Tuple should have three elements"
    for element in result:
        assert isinstance(element, str), "Each element should be a string"

def test_date_format():
    """ Test if the date is correctly formatted """
    year, month, day = get_current_date_gmt()
    now = datetime.now(timezone.utc)
    assert year == str(now.year), "Year should match current year"
    assert month == now.strftime('%m'), "Month should match current month"
    assert day == now.strftime('%d'), "Day should match current day"

def test_length_of_date_components():
    """ Test if the month and day are two digits long """
    year, month, day = get_current_date_gmt()
    assert len(year) == 4, "Year should be four digits"
    assert len(month) == 2, "Month should be two digits"
    assert len(day) == 2, "Day should be two digits"

# To run the tests, execute pytest in the terminal in the directory containing this test file
