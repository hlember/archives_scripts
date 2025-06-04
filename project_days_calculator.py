"""takes user input for start and end date of a project
calculates the total days in a projct
skips weekends and holidays"""

import holidays
import argparse
import sys
import datetime

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%m/%d/%y').date()
    except ValueError:
        return None

def is_weekend(date_obj):
    return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday

def is_holiday(date_obj, holiday_calendar):
    return date_obj in holiday_calendar

def calculate_working_days(start_date_str, end_date_str):
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    if not start_date:
        return "Error: Invalid start date format. Please use MM/DD/YY (e.g., 06/05/25)."
    if not end_date:
        return "Error: Invalid end date format. Please use MM/DD/YY (e.g., 06/05/25)."
    if start_date > end_date:
        return "Error: Start date must be on or before end date."
    
    years = range(start_date.year, end_date.year + 1)
    us_holidays = holidays.US(years=years)

    if is_weekend(start_date):
        return "Error: Start date cannot be on a weekend."
    if is_weekend(end_date):
        return "Error: End date cannot be on a weekend."
    if is_holiday(start_date, us_holidays):
        return f"Error: Start date {start_date} is a holiday: {us_holidays.get(start_date)}."
    if is_holiday(end_date, us_holidays):
        return f"Error: End date {end_date} is a holiday: {us_holidays.get(end_date)}."

    current_date = start_date
    working_days_count = 0

    while current_date <= end_date:
        if current_date.weekday() < 5 and current_date not in us_holidays:
            working_days_count += 1
        current_date += datetime.timedelta(days=1)

    return working_days_count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Calculate project duration in working days (skip weekends and holidays)")
        parser.add_argument("start_date", type=str, help="Start date in MM/DD/YY")
        parser.add_argument("end_date", type=str, help="End date in MM/DD/YY")
        args = parser.parse_args()

        result = calculate_working_days(args.start_date, args.end_date)
        print(f"Working days between {args.start_date} and {args.end_date}: {result}" if isinstance(result, int) else result)

    else:
        today_year = datetime.date.today().year
        us_holidays = holidays.US(years=range(today_year, today_year + 5))  # support a few years out

        while True:
            start_date_str = input("Enter start date (MM/DD/YY): ")
            start_date = parse_date(start_date_str)
            if not start_date:
                print("Invalid format. Please use MM/DD/YY.")
                continue
            if is_weekend(start_date):
                print("Start date cannot be on a weekend.")
                continue
            if is_holiday(start_date, us_holidays):
                print(f"Start date is a holiday: {us_holidays.get(start_date)}.")
                continue
            break

        while True:
            end_date_str = input("Enter end date (MM/DD/YY): ")
            end_date = parse_date(end_date_str)
            if not end_date:
                print("Invalid format. Please use MM/DD/YY.")
                continue
            if end_date < start_date:
                print("End date cannot be before start date.")
                continue
            if is_weekend(end_date):
                print("End date cannot be on a weekend.")
                continue
            if is_holiday(end_date, us_holidays):
                print(f"End date is a holiday: {us_holidays.get(end_date)}.")
                continue
            break

        duration = calculate_working_days(start_date_str, end_date_str)
        print(f"Working days between {start_date_str} and {end_date_str}: {duration}")
