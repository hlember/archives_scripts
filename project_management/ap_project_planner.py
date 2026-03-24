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
  --r_gb R_GB    Rate: Gigabytes per day (Default: 0.2., i.e., 5 days/GB)
  --staff STAFF  Number of archivists (FTE)
  --dpw DPW      Days per week project occurs (1-5)
  --start START  Start date (YYYY-MM-DD). Defaults to today
  --days            Workdays indices 0-4 (Default: 0,1,2,3,4 for Mon-Fri)

  To run script: python3 ap_project_planner.py -- enter details from above here 

  rates are hardcoded, but can be adjusted from command line with -- r_lin, -- r_ami -- r_car -- r_gb
  at least one extent type, staff required

  Also exports a visualization of staff effort for each format
"""
import datetime
import holidays
import math
import argparse
import sys
import matplotlib.pyplot as plt

def get_calendar_stats(total_working_days, staff_count, work_days_indices):
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
    us_holidays = holidays.US()
    current_date = start_date
    days_added = 0
    target_days = math.ceil(working_days)

    if start_date.weekday() in work_days_indices and start_date not in us_holidays:
        days_added = 1

    while days_added < target_days:
        current_date += datetime.timedelta(days=1)
        if current_date.weekday() in work_days_indices and current_date not in us_holidays:
            days_added += 1
    return current_date

def main():
    parser = argparse.ArgumentParser(description="Archival Project Calculator (Units per Day)")

    # Quantities
    parser.add_argument("--lin", type=float, default=0, help="Linear feet")
    parser.add_argument("--ami", type=float, default=0, help="Number of AMI recordings")
    parser.add_argument("--car", type=float, default=0, help="Number of digital carriers")
    parser.add_argument("--gb", type=float, default=0, help="Gigabytes of digital files")

    # Rates 
    parser.add_argument("--r_lin", type=float, default=1.0, help="Rate: Linear feet per day (Default: 1.0)")
    parser.add_argument("--r_ami", type=float, default=30.0, help="Rate: AMI per day")
    parser.add_argument("--r_car", type=float, default=1.0, help="Rate: Carriers per day")
    parser.add_argument("--r_gb", type=float, default=0.2, help="Rate: GB per day (Default: 0.2, i.e., 5 days/GB)")

    # Project Settings
    parser.add_argument("--staff", type=float, default=1.0, help="Number of archivists (FTE)")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--days", type=str, default="0,1,2,3,4", help="Workdays 0-4 (Mon-Fri)")

    args = parser.parse_args()
    
    HOURS_PER_DAY = 7.0
    SHORT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    try:
        work_days_indices = [int(x.strip()) for x in args.days.split(",")]
        work_days_indices = sorted(list(set([x for x in work_days_indices if 0 <= x <= 4])))
        if not work_days_indices: raise ValueError
    except:
        print("Error: Invalid workdays.")
        return

    us_holidays = holidays.US()
    start_date = datetime.datetime.strptime(args.start, "%Y-%m-%d").date() if args.start else datetime.date.today()

    # Uniform Logic: Total Days = Quantity / Rate
    efforts = {
        'Physical (Lin Ft)': (args.lin / args.r_lin) if args.lin > 0 and args.r_lin > 0 else 0,
        'AMI Recordings': (args.ami / args.r_ami) if args.ami > 0 and args.r_ami > 0 else 0,
        'Digital Carriers': (args.car / args.r_car) if args.car > 0 and args.r_car > 0 else 0,
        'Digital (GB)': (args.gb / args.r_gb) if args.gb > 0 and args.r_gb > 0 else 0
    }

    total_days = sum(efforts.values())

    if total_days == 0:
        print("No workload entered. Example: python planner.py --lin 10")
        return

    total_stats, pp_stats, calendar_days = get_calendar_stats(total_days, args.staff, work_days_indices)
    end_date = get_completion_date(start_date, calendar_days, work_days_indices)
    
    print("\n" + "="*55)
    print(f"ESTIMATED COMPLETION: {end_date.strftime('%A, %B %d, %Y')}")
    print("-" * 55)
    print(f"Total Effort:      {round(total_days, 2)} Working Days")
    print(f"Staff (FTE):       {args.staff:g}")
    print(f"Calendar Duration: {pp_stats[0]} Years, {pp_stats[1]} Months, {round(pp_stats[2], 1)} Days")
    print("="*55 + "\n")

    # Visualization
    labels = [k for k, v in efforts.items() if v > 0]
    values = [v for v in efforts.values() if v > 0]

    if labels:
        plt.figure(figsize=(10, 6))
        colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853']
        bars = plt.bar(labels, values, color=colors[:len(labels)])
        plt.title(f'Project Effort Distribution ({round(total_days, 1)} Total Days)', fontsize=14)
        plt.ylabel('Days of Labor')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom')

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()