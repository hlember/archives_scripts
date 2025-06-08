"""script to calculate hybrid work schedules
    run from the command liine or with user input
    input:
    start date
    days of week
    number of days
    script will provide end date"""

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
    return date_obj.weekday() >= 5 # 5 = Saturday, 6 = Sunday

def is_holiday(date_obj, holiday_calendar):
    return date_obj in holiday_calendar

def get_working_days_input(days_per_week_expected):
    day_names_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4,
        'saturday': 5, 'sunday': 6
    }
    
    while True:
        days_input = input(f"Enter the {days_per_week_expected} working days of the week (e.g., Monday,Tuesday,Wednesday,Thursday,Friday or 0,1,2,3,4 for Monday-Friday): ").strip()
        valid_days = []
        parts = [part.strip().lower() for part in days_input.split(',')]

        all_valid = True
        for part in parts:
            if part.isdigit() and 0 <= int(part) <= 6:
                day_num = int(part)
                if day_num >= 5: # Check for weekends
                    print(f"Error: Day '{part}' is a weekend. Working days cannot include weekends.")
                    all_valid = False
                    break
                valid_days.append(day_num)
            elif part in day_names_map:
                day_num = day_names_map[part]
                if day_num >= 5: # Check for weekends
                    print(f"Error: Day '{part}' is a weekend. Working days cannot include weekends.")
                    all_valid = False
                    break
                valid_days.append(day_names_map[part])
            else:
                print(f"Invalid day '{part}'. Please use full day names (e.g., Monday) or numbers (0-4 for weekdays).")
                all_valid = False
                break
        
        if not all_valid:
            continue # Re-prompt for input

        if not valid_days:
            print("No valid working days entered. Please try again.")
            continue

        # Ensure unique days and sort them
        valid_days = sorted(list(set(valid_days)))
        
        if len(valid_days) != days_per_week_expected:
            print(f"Error: You entered {len(valid_days)} working days, but you specified {days_per_week_expected} days per week. Please enter exactly {days_per_week_expected} valid weekdays.")
            continue
            
        return valid_days

def calculate_end_date(start_date_str, duration_days, days_per_week, specified_working_days=None):

    start_date = parse_date(start_date_str)
    if not start_date:
        return "Error: Invalid start date format. Please use MM/DD/YY (e.g., 06/05/25)."

    us_holidays = holidays.US(years=range(start_date.year, start_date.year + 5))

    work_week_days = []
    if specified_working_days is not None:
        work_week_days = specified_working_days
    elif days_per_week == 5:
        work_week_days = [0, 1, 2, 3, 4]  # Monday to Friday
    else:
       
        return "Error: Working days not specified for partial week, and days_per_week is not 5."

    if len(work_week_days) != days_per_week:
        return f"Error: Internal logic error: The number of specified working days ({len(work_week_days)}) does not match 'days per week' ({days_per_week})."

    if is_weekend(start_date):
        return "Error: Start date cannot be on a weekend. Please choose a weekday."
    if is_holiday(start_date, us_holidays):
        return f"Error: Start date {start_date.strftime('%m/%d/%y')} is a holiday: {us_holidays.get(start_date)}."
    if start_date.weekday() not in work_week_days:
        return f"Error: Start date {start_date.strftime('%m/%d/%y')} is not one of your specified working days ({', '.join(datetime.date(1,1,day).strftime('%a') for day in sorted(work_week_days))})."

    current_date = start_date
    working_days_counted = 0
    
   
    if current_date.weekday() in work_week_days and not is_holiday(current_date, us_holidays):
        working_days_counted = 1
    else:
      
        pass 

        if working_days_counted == 0:
            while True:
                current_date += datetime.timedelta(days=1)
                if current_date.weekday() in work_week_days and not is_holiday(current_date, us_holidays):
                    working_days_counted = 1 # Start counting from this valid day
                    break
                if current_date > start_date + datetime.timedelta(days=365*2): 
                    return "Error: Could not find a valid first working day within two years of the start date."

    while working_days_counted < duration_days:
        current_date += datetime.timedelta(days=1) 
        
        if current_date.weekday() in work_week_days and not is_holiday(current_date, us_holidays):
            working_days_counted += 1
  
    if current_date.weekday() not in work_week_days or is_holiday(current_date, us_holidays):
        return f"Internal Error: Calculated end date {current_date.strftime('%m/%d/%y')} is not a valid working day."


    return current_date.strftime('%m/%d/%y')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate project end date (skip weekends, holidays, and non-working days).")
    parser.add_argument("start_date", type=str, nargs='?', help="Start date in MM/DD/YY (e.g., 06/05/25)")
    parser.add_argument("duration", type=int, nargs='?', help="Total duration in working days")
    parser.add_argument("days_per_week", type=int, nargs='?', help="Number of days worked per week (1-5)")
    parser.add_argument("--working_days", type=str, help="Comma-separated list of working days (e.g., Monday,Tuesday,Wednesday or 0,1,2). Only applies if days_per_week < 5.")

    args = parser.parse_args()

    if all([args.start_date, args.duration, args.days_per_week]):

        start_date_str = args.start_date
        duration = args.duration
        days_per_week = args.days_per_week

        if not (1 <= days_per_week <= 5):
            print("Error: Days per week must be between 1 and 5.")
            sys.exit(1)

        specified_working_days = None
        if days_per_week < 5:
            if not args.working_days:
                print("Error: For days per week less than 5, you must specify working days using --working_days (e.g., --working_days Monday,Tuesday,Wednesday).")
                sys.exit(1)
            

            day_names_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4,
                'saturday': 5, 'sunday': 6
            }
            parsed_days = []
            for day_part in args.working_days.split(','):
                day_part_lower = day_part.strip().lower()
                if day_part_lower.isdigit() and 0 <= int(day_part_lower) <= 6:
                    day_num = int(day_part_lower)
                    if day_num >= 5:
                        print(f"Error: Day '{day_part}' in --working_days is a weekend. Please select only weekdays.")
                        sys.exit(1)
                    parsed_days.append(day_num)
                elif day_part_lower in day_names_map:
                    day_num = day_names_map[day_part_lower]
                    if day_num >= 5:
                        print(f"Error: Day '{day_part}' in --working_days is a weekend. Please select only weekdays.")
                        sys.exit(1)
                    parsed_days.append(day_num)
                else:
                    print(f"Error: Invalid day '{day_part}' in --working_days. Please use full day names (e.g., Mon) or numbers (0-4 for weekdays).")
                    sys.exit(1)
            specified_working_days = sorted(list(set(parsed_days)))
            
            if len(specified_working_days) != days_per_week:
                print(f"Error: The number of specified working days ({len(specified_working_days)}) does not match 'days per week' ({days_per_week}).")
                sys.exit(1)
        elif days_per_week == 5: 
             specified_working_days = [0, 1, 2, 3, 4]


        result = calculate_end_date(start_date_str, duration, days_per_week, specified_working_days)
        if "Error:" in result:
            print(result)
            sys.exit(1)
        print(f"Project starting on {start_date_str} with {duration} working days, worked {days_per_week} days/week, ends on: {result}")

    else:
        today_year = datetime.date.today().year
        us_holidays = holidays.US(years=range(today_year, today_year + 5))

        while True:
            try:
                days_per_week = int(input("Enter number of days worked per week (1-5): "))
                if not (1 <= days_per_week <= 5):
                    print("Days per week must be between 1 and 5.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number for days per week.")
        
        specified_working_days = None
        if days_per_week < 5:
            specified_working_days = get_working_days_input(days_per_week)
        elif days_per_week == 5:
            specified_working_days = [0, 1, 2, 3, 4] # Default to Mon-Fri for 5 days

        # Now get start date, validating against all criteria
        while True:
            start_date_str = input("Enter start date (MM/DD/YY): ")
            start_date_obj = parse_date(start_date_str)

            if not start_date_obj:
                print("Invalid format. Please use MM/DD/YY.")
                continue
    
            if is_weekend(start_date_obj):
                print("Error: Start date cannot be on a weekend. Please choose a weekday.")
                continue
            if is_holiday(start_date_obj, us_holidays):
                print(f"Error: Start date {start_date_obj.strftime('%m/%d/%y')} is a holiday: {us_holidays.get(start_date_obj)}.")
                continue
            if start_date_obj.weekday() not in specified_working_days:
    
                working_day_names = ', '.join(datetime.date(1,1,day).strftime('%a') for day in sorted(specified_working_days))
                print(f"Error: Start date {start_date_obj.strftime('%m/%d/%y')} ({start_date_obj.strftime('%a')}) is not one of your specified working days: {working_day_names}.")
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

        end_date = calculate_end_date(start_date_str, duration, days_per_week, specified_working_days)
        if "Error:" in end_date:
            print(end_date)
        else:
            print(f"Project starting on {start_date_str} with {duration} working days, worked {days_per_week} days/week, ends on: {end_date}")