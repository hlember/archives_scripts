"""takes user input for start and end date of a project
calculates the total days in a projct
skips weekends and holidays"""

import holidays
import datetime
import argparse
import sys

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%m/%d/%y').date()
    except ValueError:
        return None

def is_weekend(date_obj):
    return date_obj.weekday() >= 5

def is_holiday(date_obj, holiday_calendar):
    return date_obj in holiday_calendar

def parse_working_days(working_days_str):
    """Convert 'Monday,Wednesday,Friday' to [0,2,4]"""
    days_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    days = [days_map.get(day.strip().title()) for day in working_days_str.split(',')]
    if None in days:
        raise ValueError("Invalid weekday abbreviation.")
    return days

def calculate_custom_working_days(start_date, end_date, allowed_weekdays, holiday_calendar):
    current_date = start_date
    working_days_count = 0
    while current_date <= end_date:
        if current_date.weekday() in allowed_weekdays and current_date not in holiday_calendar:
            working_days_count += 1
        current_date += datetime.timedelta(days=1)
    return working_days_count

def get_us_holidays(start_year, end_year):
    return holidays.US(years=range(start_year, end_year + 1))

def validate_dates(start_date_str, end_date_str, us_holidays):
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    if not start_date:
        return None, None, "Error: Invalid start date format. Use MM/DD/YY."
    if not end_date:
        return None, None, "Error: Invalid end date format. Use MM/DD/YY."
    if end_date < start_date:
        return None, None, "Error: End date cannot be before start date."
    if is_weekend(start_date):
        return None, None, "Error: Start date cannot be on a weekend."
    if is_weekend(end_date):
        return None, None, "Error: End date cannot be on a weekend."
    if is_holiday(start_date, us_holidays):
        return None, None, f"Error: Start date is a holiday: {us_holidays.get(start_date)}"
    if is_holiday(end_date, us_holidays):
        return None, None, f"Error: End date is a holiday: {us_holidays.get(end_date)}"

    return start_date, end_date, None

def run_interactive():
    today_year = datetime.date.today().year
    us_holidays = get_us_holidays(today_year, today_year + 5)

    # Start Date
    while True:
        start_date_str = input("Enter start date (MM/DD/YY): ")
        end_date_str = None  # prep for later
        start_date = parse_date(start_date_str)
        if not start_date:
            print("Invalid format.")
            continue
        if is_weekend(start_date):
            print("Start date cannot be a weekend.")
            continue
        if is_holiday(start_date, us_holidays):
            print(f"Start date is a holiday: {us_holidays.get(start_date)}.")
            continue
        break

    # End Date
    while True:
        end_date_str = input("Enter end date (MM/DD/YY): ")
        end_date = parse_date(end_date_str)
        if not end_date:
            print("Invalid format.")
            continue
        if end_date < start_date:
            print("End cannot be before start.")
            continue
        if is_weekend(end_date):
            print("End date cannot be a weekend.")
            continue
        if is_holiday(end_date, us_holidays):
            print(f"End date is a holiday: {us_holidays.get(end_date)}.")
            continue
        break

    # Days per Week
    while True:
        try:
            days_per_week = int(input("How many days per week is the project? (1–5): "))
            if 1 <= days_per_week <= 5:
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter a number between 1 and 5.")

    if days_per_week == 5:
        allowed_weekdays = [0, 1, 2, 3, 4]
        working_days_input = "Monday,Tuesday,Wednesday,Thursday,Friday"
    else:
        while True:
            working_days_input = input(f"Enter the {days_per_week} weekday(s) (e.g., Monday,Wednesday,Friday): ")
            try:
                allowed_weekdays = parse_working_days(working_days_input)
                if len(allowed_weekdays) != days_per_week:
                    print("Number of days does not match. Try again.")
                    continue
                break
            except ValueError as e:
                print(f"Error: {e}")

    duration = calculate_custom_working_days(start_date, end_date, allowed_weekdays, us_holidays)
    print(f"\n Working days between {start_date_str} and {end_date_str} on {working_days_input}: {duration}")

def run_cli(args):
    start_date_str = args.start_date
    end_date_str = args.end_date
    days_per_week = args.days_per_week
    working_days_input = args.working_days

    start_year = parse_date(start_date_str).year if parse_date(start_date_str) else datetime.date.today().year
    end_year = parse_date(end_date_str).year if parse_date(end_date_str) else start_year
    us_holidays = get_us_holidays(start_year, end_year)

    start_date, end_date, error = validate_dates(start_date_str, end_date_str, us_holidays)
    if error:
        print(error)
        sys.exit(1)

    if days_per_week == 5:
        allowed_weekdays = [0, 1, 2, 3, 4]
        working_days_input = "Monday,Tuesday,Wednesday,Thursday,Friday"
    else:
        if not working_days_input:
            print("Error: Must provide working days when days_per_week < 5.")
            sys.exit(1)
        try:
            allowed_weekdays = parse_working_days(working_days_input)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        if len(allowed_weekdays) != days_per_week:
            print("Error: Mismatch between days_per_week and working_days listed.")
            sys.exit(1)

    duration = calculate_custom_working_days(start_date, end_date, allowed_weekdays, us_holidays)
    print(f"\n Working days between {start_date_str} and {end_date_str} on {working_days_input}: {duration}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate project duration skipping weekends and holidays.")
    parser.add_argument("start_date", nargs='?', help="Start date (M/D/YY)")
    parser.add_argument("end_date", nargs='?', help="End date (M/D/YY)")
    parser.add_argument("days_per_week", type=int, nargs='?', help="Number of days per week the project runs (1–5)")
    parser.add_argument("working_days", nargs='?', help="Comma-separated list of days (e.g., Monday,Wednesay,Friday) if < 5 days/week")

    args = parser.parse_args()

    if args.start_date and args.end_date and args.days_per_week:
        run_cli(args)
    else:
        run_interactive()
