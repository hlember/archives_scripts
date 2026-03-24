"""
Advanced version of project planner than is run from the command line
Does not take User Input
Allows user to adjust processing rates from the command line
options:
  -h, --help     show this help message and exit
  --lin LIN      Linear feet
  --ami AMI      Number of AMI recordings
  --car CAR      Number of digital carriers
  --gb GB        Gigabytes of digital files
  --r_lin R_LIN  Rate: Days per linear foot (Default: 1)
  --r_ami R_AMI  Rate: Recordings processed per day (Default: 30)
  --r_car R_CAR  Rate: Digital carriers per day (Default: 1)
  --r_gb R_GB    Rate: Days per Gigabyte (Default: 5)
  --staff STAFF  Number of archivists (FTE)
  --dpw DPW      Days per week project occurs (1-5)
  --start START  Start date (YYYY-MM-DD). Defaults to today
  --days            Workdays indices 0-4 (Default: 0,1,2,3,4 for Mon-Fri)

  To run script: python3 ap_project_planner.py -- enter details from above here 

  rates are hardcoded, but can be adjusted from command line with -- r_lin, -- r_ami -- r_car -- r_gb
  at least one extent type, staff required
"""
import datetime
import holidays
import math
import argparse
import sys

def get_calendar_stats(total_working_days, staff_count, work_days_indices):
    """Calculates year/month/day breakdown based on the specific work schedule."""
    days_per_week = len(work_days_indices)
    days_in_year = 52 * days_per_week
    days_in_month = days_in_year / 12 if days_in_year > 0 else 0

    def breakdown(days):
        if days_in_year == 0: return 0, 0, 0
        years = int(days // days_in_year)
        remaining_after_years = days % days_in_year
        months = int(remaining_after_years // days_in_month)
        remaining_days = round(remaining_after_years % days_in_month, 2)
        return years, months, remaining_days

    total_stats = breakdown(total_working_days)
    days_per_person = total_working_days / staff_count if staff_count > 0 else 0
    per_person_stats = breakdown(days_per_person)

    return total_stats, per_person_stats, days_per_person

def get_completion_date(start_date, working_days, work_days_indices):
    """Steps through calendar skipping weekends, holidays, and non-work days."""
    us_holidays = holidays.US()
    current_date = start_date
    days_added = 0
    target_days = math.ceil(working_days)

    # Check if the start date itself is a valid workday
    if start_date.weekday() in work_days_indices and start_date not in us_holidays:
        days_added = 1

    while days_added < target_days:
        current_date += datetime.timedelta(days=1)
        if current_date.weekday() in work_days_indices and current_date not in us_holidays:
            days_added += 1
    return current_date

def main():
    parser = argparse.ArgumentParser(description="Archival Project Calculator with Custom Workdays")

    # Quantities
    parser.add_argument("--lin", type=float, default=0, help="Linear feet")
    parser.add_argument("--ami", type=float, default=0, help="Number of AMI recordings")
    parser.add_argument("--car", type=float, default=0, help="Number of digital carriers")
    parser.add_argument("--gb", type=float, default=0, help="Gigabytes of digital files")

    # Rates
    parser.add_argument("--r_lin", type=float, default=1.0, help="Rate: Days per linear foot")
    parser.add_argument("--r_ami", type=float, default=30.0, help="Rate: AMI per day")
    parser.add_argument("--r_car", type=float, default=1.0, help="Rate: Carriers per day")
    parser.add_argument("--r_gb", type=float, default=5.0, help="Rate: Days per GB")

    # Project Settings
    parser.add_argument("--staff", type=float, default=1.0, help="Number of archivists (FTE)")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    # Custom workdays input (e.g., 0,2,4 for Mon,Wed,Fri)
    parser.add_argument("--days", type=str, default="0,1,2,3,4", 
                        help="Workdays indices 0-4 (Default: 0,1,2,3,4 for Mon-Fri)")

    args = parser.parse_args()
    
    # Constants
    HOURS_PER_DAY = 7.0
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    SHORT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    # Parse workdays
    try:
        work_days_indices = [int(x.strip()) for x in args.days.split(",")]
        work_days_indices = sorted(list(set([x for x in work_days_indices if 0 <= x <= 4])))
        if not work_days_indices:
            raise ValueError
    except:
        print("Error: Invalid workdays. Use indices 0-4 (e.g., --days 0,2,4)")
        return

    # Handle start date
    us_holidays = holidays.US()
    if args.start:
        try:
            start_date = datetime.datetime.strptime(args.start, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        start_date = datetime.date.today()

    # Validation: Start date must be a scheduled workday
    if start_date.weekday() not in work_days_indices or start_date in us_holidays:
        print(f"Warning: {start_date} ({DAY_NAMES[start_date.weekday()]}) is not a scheduled workday or is a holiday.")
        print("Finding the next available workday...")
        # Move start_date to the next valid workday for the calculation
        while start_date.weekday() not in work_days_indices or start_date in us_holidays:
            start_date += datetime.timedelta(days=1)

    # Calculation Logic
    total_days = (args.lin * args.r_lin) + (args.ami / args.r_ami) + \
                 (args.car * args.r_car) + (args.gb * args.r_gb)

    if total_days == 0:
        print("No workload entered.")
        return

    total_stats, pp_stats, calendar_days = get_calendar_stats(total_days, args.staff, work_days_indices)
    end_date = get_completion_date(start_date, calendar_days, work_days_indices)
    total_hours = total_days * HOURS_PER_DAY

    # Final Report
    sched_str = ", ".join([SHORT_DAYS[i] for i in work_days_indices])
    
    print("\n" + "="*55)
    print(f"ESTIMATED COMPLETION: {end_date.strftime('%A, %B %d, %Y')}")
    print("-" * 55)
    print(f"Team Size:         {args.staff:g} Staff (FTE)")
    print(f"Schedule:          {sched_str} ({len(work_days_indices)} days/week at {HOURS_PER_DAY} hrs/day)")
    print(f"Total Effort:      {round(total_days, 2)} Working Days")
    print(f"Total Staff Hours: {round(total_hours, 1)} Hours")
    print(f"Calendar Duration: {pp_stats[0]} Years, {pp_stats[1]} Months, {round(pp_stats[2], 1)} Days")
    print("-" * 55)
    print(f"Project Start:     {start_date.strftime('%Y-%m-%d')}")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()