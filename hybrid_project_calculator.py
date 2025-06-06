"""calculates project timelines for hybrid projects and projects that are done for only a partial week
    skips holidays and weekend
    takes user input or command line input"""

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

def calculate_end_date(start_date_str, duration_days, days_per_week):

    start_date = parse_date(start_date_str)
    if not start_date:
        return "Error: Invalid start date format. Please use MM/DD/YY (e.g., 06/05/25)."

    # Ensure days_per_week is valid (1-5 for weekdays)
    if not (1 <= days_per_week <= 5):
        return "Error: Days per week must be between 1 and 5."

    us_holidays = holidays.US(years=range(start_date.year, start_date.year + 5))

    if is_weekend(start_date):
        return "Error: Start date cannot be on a weekend. Please choose a weekday."
    if is_holiday(start_date, us_holidays):
        return f"Error: Start date {start_date} is a holiday: {us_holidays.get(start_date)}."

    current_date = start_date
    working_days_counted = 0
    work_week_days = []

    # Determine which weekdays are considered working days
    # We assume working days start from Monday (0) and go up to days_per_week - 1
    # For example, if days_per_week = 3, work_week_days = [0, 1, 2] (Mon, Tue, Wed)
    for i in range(days_per_week):
        work_week_days.append(i)

    while working_days_counted < duration_days:
        # Check if the current date is a designated working day of the week AND not a weekend or holiday
        if current_date.weekday() in work_week_days and not is_weekend(current_date) and not is_holiday(current_date, us_holidays):
            working_days_counted += 1
        
        # If we've counted enough working days, we can stop
        if working_days_counted == duration_days:
            break
        
        # Move to the next day
        current_date += datetime.timedelta(days=1)

    return current_date.strftime('%m/%d/%y')
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate project end date (skip weekends and holidays)")
    parser.add_argument("start_date", type=str, help="Start date in MM/DD/YY (e.g., 06/05/25)")
    parser.add_argument("duration", type=int, help="Total duration in working days")
    parser.add_argument("days_per_week", type=int, help="Number of days worked per week (1-5)")

    # Check if arguments are provided, otherwise go to interactive mode
    if len(sys.argv) > 1:
        args = parser.parse_args()

        start_date_obj = parse_date(args.start_date)
        if not start_date_obj:
            print("Error: Invalid date format. Please use MM/DD/YY.")
            sys.exit(1)
        
        if not (1 <= args.days_per_week <= 5):
            print("Error: Days per week must be between 1 and 5.")
            sys.exit(1)

        us_holidays = holidays.US(years=range(start_date_obj.year, start_date_obj.year + 5))

        if is_weekend(start_date_obj):
            print("Error: Start date cannot be on a weekend.")
            sys.exit(1)
        if is_holiday(start_date_obj, us_holidays):
            print(f"Error: Start date {start_date_obj} is a holiday: {us_holidays.get(start_date_obj)}.")
            sys.exit(1)
        
        result = calculate_end_date(args.start_date, args.duration, args.days_per_week)
        print(f"Project starting on {args.start_date} with {args.duration} working days, worked {args.days_per_week} days/week, ends on: {result}")

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

        while True:
            try:
                duration = int(input("Enter total duration in working days: "))
                if duration <= 0:
                    print("Duration must be a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number for duration.")

        while True:
            try:
                days_per_week = int(input("Enter number of days worked per week (1-5): "))
                if not (1 <= days_per_week <= 5):
                    print("Days per week must be between 1 and 5.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number for days per week.")

        end_date = calculate_end_date(start_date_str, duration, days_per_week)
        print(f"Project starting on {start_date_str} with {duration} working days, worked {days_per_week} days/week, ends on: {end_date}")