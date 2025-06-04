""" takes user input of:
    a start datw
    total number of days 
 calculates the end date 
  skips holidays and weekends"""

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
    return date_obj.weekday() >= 5  # 5 = Saturday, 6 = Sunday

def is_holiday(date_obj, holiday_calendar):
    return date_obj in holiday_calendar

def calculate_end_date(start_date_str, duration_days):
    start_date = parse_date(start_date_str)
    if not start_date:
        return "Error: Invalid start date format. Please use MM/DD/YY (e.g., 06/05/25)."

    us_holidays = holidays.US(years=range(start_date.year, start_date.year + 5))

    if is_weekend(start_date):
        return "Error: Start date cannot be on a weekend. Please choose a weekday."
    if is_holiday(start_date, us_holidays):
        return f"Error: Start date {start_date} is a holiday: {us_holidays.get(start_date)}."

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
        parser = argparse.ArgumentParser(description="Calculate project end date (skip weekends and holidays)")
        parser.add_argument("start_date", type=str, help="Start date in MM/DD/YY")
        parser.add_argument("duration", type=int, help="Duration in working days")
        args = parser.parse_args()

        start_date_obj = parse_date(args.start_date)
        if not start_date_obj:
            print("Error: Invalid date format. Please use MM/DD/YY.")
            sys.exit(1)

        us_holidays = holidays.US(years=range(start_date_obj.year, start_date_obj.year + 5))

        if is_weekend(start_date_obj):
            print("Error: Start date cannot be on a weekend.")
            sys.exit(1)
        if is_holiday(start_date_obj, us_holidays):
            print(f"Error: Start date {start_date_obj} is a holiday: {us_holidays.get(start_date_obj)}.")
            sys.exit(1)

        result = calculate_end_date(args.start_date, args.duration)
        print(f"Project starting on {args.start_date} with {args.duration} working days ends on: {result}")

    else:
        # Interactive input
        today_year = datetime.date.today().year
        us_holidays = holidays.US(years=range(today_year, today_year + 5))

        while True:
            start_date_str = input("Enter start date (MM/DD/YY): ")
            start_date_obj = parse_date(start_date_str)
            if not start_date_obj:
                print("Invalid format. Please use MM/DD/YY.")
                continue
            if is_weekend(start_date_obj):
                print("Start date cannot be on a weekend.")
                continue
            if is_holiday(start_date_obj, us_holidays):
                print(f"Start date is a holiday: {us_holidays.get(start_date_obj)}.")
                continue
            break

        duration = int(input("Enter duration in working days: "))
        end_date = calculate_end_date(start_date_str, duration)
        print(f"Project starting on {start_date_str} with {duration} working days ends on: {end_date}")