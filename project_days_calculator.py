"""takes user input for start and end date of a project
calculates the total days in a projct
skips weekends and holidays"""

import datetime
import holidays 
import argparse
import sys

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%m/%d/%y').date()
    except ValueError:
        return None

def is_weekend(date_obj):
    return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday

def calculate_working_days(start_date_str, end_date_str):
    start_date = parse_date(start_date_str)
    end_date = parse_date(end_date_str)

    if not start_date:
        return "Error: Invalid start date format. Please use MM/DD/YY (e.g., 06/05/25)."
    if not end_date:
        return "Error: Invalid end date format. Please use MM/DD/YY (e.g., 06/05/25)."
    if start_date > end_date:
        return "Error: Start date must be on or before end date."
    if is_weekend(start_date):
        return "Error: Start date cannot be on a weekend."
    if is_weekend(end_date):
        return "Error: End date cannot be on a weekend."

    # Define US holidays for all years covered by start and end date
    years = range(start_date.year, end_date.year + 1)
    us_holidays = holidays.US(years=years)

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

        duration = calculate_working_days(args.start_date, args.end_date)
        print(f"Working days between {args.start_date} and {args.end_date}: {duration}")

    else:
        while True:
            start_date = input("Enter start date (MM/DD/YY): ")
            if not parse_date(start_date):
                print("Invalid format. Please use MM/DD/YY.")
                continue
            if is_weekend(parse_date(start_date)):
                print("Start date cannot be on a weekend. Please enter a weekday.")
                continue
            break

        while True:
            end_date = input("Enter end date (MM/DD/YY): ")
            if not parse_date(end_date):
                print("Invalid format. Please use MM/DD/YY.")
                continue
            if is_weekend(parse_date(end_date)):
                print("End date cannot be on a weekend. Please enter a weekday.")
                continue
            if parse_date(end_date) < parse_date(start_date):
                print("End date cannot be before start date.")
                continue
            break

        duration = calculate_working_days(start_date, end_date)
        print(f"Working days between {start_date} and {end_date}: {duration}")
