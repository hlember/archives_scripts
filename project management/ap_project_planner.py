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
  --r_ami R_AMI  Rate: Recordings processed per 1 day (Default: 30)
  --r_car R_CAR  Rate: Days per digital carrier (Default: 5)
  --r_gb R_GB    Rate: Days per Gigabyte (Default: 10)
  --staff STAFF  Number of archivists (FTE)
  --dpw DPW      Days per week project occurs (1-5)
  --start START  Start date (YYYY-MM-DD). Defaults to today.

  To run script: python3 ap_project_planner.py -- enter details from above here 

  rates are hardcoded, but can be adjusted from command line with --r_lin, --r_ami --r_car --r_gb
  at least one extent type, staff required
"""
import datetime
import holidays
import math
import argparse
import sys

def get_calendar_stats(total_working_days, staff_count, days_per_week):
    """Calculates year/month/day breakdown based on project schedule."""
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
    days_per_person = total_working_days / staff_count
    per_person_stats = breakdown(days_per_person)

    return total_stats, per_person_stats, days_per_person

def get_completion_date(start_date, working_days, days_per_week):
    """Steps through calendar skipping weekends, holidays, and non-work days."""
    us_holidays = holidays.US()
    current_date = start_date
    days_added = 0
    target_days = math.ceil(working_days)

    while days_added < target_days:
        current_date += datetime.timedelta(days=1)
        if current_date.weekday() >= 5 or current_date in us_holidays or current_date.weekday() >= days_per_week:
            continue
        days_added += 1
    return current_date

def main():
    parser = argparse.ArgumentParser(description="Archival Project Calculator with Custom Rates")

    # Quantities
    parser.add_argument("--lin", type=float, default=0, help="Linear feet")
    parser.add_argument("--ami", type=float, default=0, help="Number of AMI recordings")
    parser.add_argument("--car", type=float, default=0, help="Number of digital carriers")
    parser.add_argument("--gb", type=float, default=0, help="Gigabytes of digital files")

    # Rates (Days per Unit)
    parser.add_argument("--r_lin", type=float, default=1.0, help="Rate: Days per linear foot (Default: 1)")
    parser.add_argument("--r_ami", type=float, default=30.0, help="Rate: Recordings processed per 1 day (Default: 30)")
    parser.add_argument("--r_car", type=float, default=5.0, help="Rate: Days per digital carrier (Default: 5)")
    parser.add_argument("--r_gb", type=float, default=10.0, help="Rate: Days per Gigabyte (Default: 10)")

    # Project Settings
    parser.add_argument("--staff", type=float, default=1.0, help="Number of archivists (FTE)")
    parser.add_argument("--dpw", type=float, default=5.0, help="Days per week project occurs (1-5)")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD). Defaults to today.")

    args = parser.parse_args()

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

    # Check if starting on a valid workday
    if start_date.weekday() >= args.dpw or start_date.weekday() >= 5 or start_date in us_holidays:
        print(f"Warning: {start_date} is a non-work day. The first day of work will be the next available workday.")

    # Calculation Logic
    # (Note: AMI rate is 'units per day', others are 'days per unit')
    total_days = (args.lin * args.r_lin) + \
                 (args.ami / args.r_ami) + \
                 (args.car * args.r_car) + \
                 (args.gb * args.r_gb)

    if total_days == 0:
        print("No workload entered. Use --help to see how to provide quantities.")
        return

    total_stats, pp_stats, calendar_days = get_calendar_stats(total_days, args.staff, args.dpw)
    end_date = get_completion_date(start_date, calendar_days, args.dpw)

    # Final Report
    print("\n" + "="*50)
    print(f"PROJECT START: {start_date.strftime('%A, %B %d, %Y')}")
    print(f"SCHEDULE: {args.dpw:g} days/week with {args.staff:g} staff")
    print(f"RATES USED: {args.r_lin}d/ft, {args.r_ami}ami/d, {args.r_car}d/car, {args.r_gb}d/GB")
    print(f"TOTAL WORKLOAD: {round(total_days, 2)} Working Days")
    print("="*50)
    print(f"TOTAL LABOR EFFORT (Sequential)")
    print(f"{total_stats[0]} Years, {total_stats[1]} Months, {total_stats[2]} Days")
    print("-" * 50)
    print(f"PROJECT TIMELINE (Calendar Duration)")
    print(f"Duration: {pp_stats[0]} Years, {pp_stats[1]} Months, {pp_stats[2]} Days")
    print(f"Estimated Completion: {end_date.strftime('%A, %B %d, %Y')}")
    print("="*50)

if __name__ == "__main__":
    main()