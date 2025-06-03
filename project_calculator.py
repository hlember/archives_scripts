""" takes user input of:
    a start datw
    total number of days 
 calculates the end date 
  skips holidays and weekends"""

import datetime
import holidays 
import argparse
import sys

def is_weekend(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, '%m/%d/%y').date()
    except ValueError:
        return None  # Invalid format
    return date_obj.weekday() >= 5  # 5 = Saturday, 6 = Sunday

def calculate_end_date(start_date_str, duration_days):
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%m/%d/%y').date()
    except ValueError:
        return "Error: Invalid start date format. Please use MM/DD/YY (e.g., 06/05/25)."

    if start_date.weekday() >= 5:
        return "Error: Start date cannot be on a weekend. Please choose a weekday."

    us_holidays = holidays.US(years=range(start_date.year, start_date.year + 5))
    current_date = start_date
    working_days_counted = 0

    while working_days_counted < duration_days:
        if current_date.weekday() < 5 and current_date not in us_holidays:
            working_days_counted += 1
        if working_days_counted == duration_days:
            break
        current_date += datetime.timedelta(days=1)

    return current_date.strftime('%m/%d/%y')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command-line input
        parser = argparse.ArgumentParser(description="Calculate project end date (skip weekends)")
        parser.add_argument("start_date", type=str, help="Start date in MM/DD/YY")
        parser.add_argument("duration", type=int, help="Duration in working days")
        args = parser.parse_args()
        start_date = args.start_date
        duration = args.duration

        if is_weekend(start_date):
            print("Error: Start date cannot be on a weekend.")
            sys.exit(1)
    else:
        # Interactive input
        while True:
            start_date = input("Enter start date (MM/DD/YY): ")
            if is_weekend(start_date) is None:
                print("Invalid format. Please use MM/DD/YY.")
                continue
            elif is_weekend(start_date):
                print("Start date cannot be on a weekend. Please enter a weekday.")
                continue
            break

        duration = int(input("Enter duration in working days: "))

    end_date = calculate_end_date(start_date, duration)
    print(f"Project starting on {start_date} with {duration} working days ends on: {end_date}")