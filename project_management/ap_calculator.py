'''
Script that calculates archival processing timelines based on user input of:

- linear feet 
- number of audio and moving image recordings
- number of digital carriers
- number of gigabytes
- number of archivists (includes option for part times)
- number of workdays in a work week (accounts for bybrid schedules)

processing metrics hard-coded into script, but can be adjusted based on local repo rates

prints:
- total years, months, days 
- totals per archivist
- start and end dates based on curent date

'''
import datetime
import holidays
import math

import datetime
import holidays
import math

def get_calendar_stats(total_working_days, staff_count, days_per_week):
    """
    Calculates year/month/day breakdown.
    Adjusts 'working days per year/month' based on the project's weekly schedule.
    """
    # Adjust standard work year (52 weeks) to the project's actual days per week
    days_in_year = 52 * days_per_week
    days_in_month = days_in_year / 12

    def breakdown(days):
        if days_in_year == 0: return 0, 0, 0
        years = int(days // days_in_year)
        remaining_after_years = days % days_in_year
        months = int(remaining_after_years // days_in_month)
        remaining_days = round(remaining_after_years % days_in_month, 2)
        return years, months, remaining_days

    total_stats = breakdown(total_working_days)
    
    # Divide work by staff (FTE) to get the actual calendar duration
    days_per_person = total_working_days / staff_count
    per_person_stats = breakdown(days_per_person)

    return total_stats, per_person_stats, days_per_person

def get_completion_date(start_date, working_days, days_per_week):
    """
    Steps through the calendar skipping weekends, US holidays, 
    and days exceeding the project's weekly schedule.
    """
    us_holidays = holidays.US()
    current_date = start_date
    days_added = 0
    
    target_days = math.ceil(working_days)

    while days_added < target_days:
        current_date += datetime.timedelta(days=1)
        
        # 1. Skip Weekends (5=Sat, 6=Sun)
        if current_date.weekday() >= 5:
            continue
            
        # 2. Skip Holidays
        if current_date in us_holidays:
            continue
            
        # 3. Skip if day of week exceeds the project's set days per week
        if current_date.weekday() >= days_per_week:
            continue

        days_added += 1
    return current_date

def main():
    print("---- Archival Project Calculator ----")
    us_holidays = holidays.US()
    
    try:
        # 1. Inputs
        print("\nEnter quantities (e.g., 12.5):")
        lin_feet = float(input("Linear feet (1 day/ft): ") or 0)
        ami_recs = float(input("AMI recordings (1 day/30 recs): ") or 0)
        dig_carriers = float(input("Digital carriers (5 days/ea): ") or 0)
        gigabytes = float(input("Gigabytes of digital files (10 days/GB): ") or 0)
        
        staff_num = float(input("\nNumber of archivists (FTE, e.g., 1.5): ") or 1)
        if staff_num <= 0:
            print("Error: Staff count must be at least 0.1")
            return

        days_per_week = float(input("Days per week project occurs (1-5): ") or 5)
        days_per_week = min(max(days_per_week, 1), 5) # Cap between 1 and 5

        # 2. Start Date Loop
        while True:
            date_input = input("\nEnter start date (YYYY-MM-DD) or press Enter for today: ").strip()
            
            if not date_input:
                start_date = datetime.date.today()
            else:
                try:
                    start_date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
                except ValueError:
                    print(">> Invalid format! Please use YYYY-MM-DD.")
                    continue

            # Validation: Is start_date a valid work day?
            if start_date.weekday() >= days_per_week or start_date.weekday() >= 5 or start_date in us_holidays:
                print(f">> Error: {start_date} is a non-work day. Please choose a scheduled workday.")
                continue
            
            break

        # 3. Logic: Calculate Workload & Timeline
        total_days = (lin_feet * 1.0) + (ami_recs / 30.0) + (dig_carriers * 5.0) + (gigabytes * 10.0)
        
        total_stats, pp_stats, calendar_days = get_calendar_stats(total_days, staff_num, days_per_week)
        end_date = get_completion_date(start_date, calendar_days, days_per_week)

        # 4. Final Report
        print("\n" + "="*50)
        print(f"PROJECT START: {start_date.strftime('%A, %B %d, %Y')}")
        print(f"SCHEDULE: {days_per_week:g} days/week with {staff_num:g} staff")
        print(f"TOTAL WORKLOAD: {round(total_days, 2)} Working Days")
        print("="*50)
        print(f"TOTAL LABOR EFFORT (Sequential)")
        print(f"{total_stats[0]} Years, {total_stats[1]} Months, {total_stats[2]} Days")
        print("-" * 50)
        print(f"PROJECT TIMELINE (Calendar Duration)")
        print(f"Duration: {pp_stats[0]} Years, {pp_stats[1]} Months, {pp_stats[2]} Days")
        print(f"Estimated Completion: {end_date.strftime('%A, %B %d, %Y')}")
        print("="*50)
        print(f"*Note: Skips weekends, US Holidays, and non-project days.")

    except ValueError:
        print("Invalid input. Please use numbers for quantities.")

if __name__ == "__main__":
    main()