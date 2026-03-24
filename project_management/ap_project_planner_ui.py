"""
User-friendly version of project planner 
Asks user to input data about processing/acessioning rates
Takes input on collection extents:

  - total linear feet
  - number of AMI recordings
  - number of digital carriers
  - gigabytes of digital files

Also take user input on process/accessiong rates (hardcoded but can be revised)
  - linear foot per day (default: 1)
  - AMI processed/accessioned per day (default 30)
  - digital carriers per day (default: 1)
  - gigabyes per day (default: 0.2 per day, e.g. 5 days per GB)

  - total staff working on project (can enter part time, e.g. 0.5)

Takes user input for timelines
  - days per week that project occurs, defaults to 5 days
  - start date (YYYY-MM-DD). Defaults to today 

To run enter in commandline: python3 ap_project_planner_ui.py 

"""
import datetime
import holidays
import math
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

    days_per_person = total_working_days / staff_count if staff_count > 0 else 0
    per_person_stats = breakdown(days_per_person)
    return per_person_stats, days_per_person

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

def get_work_days_input():
    days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    print("\nWhich days of the week will work occur?")
    for i, day in enumerate(days_map, 1):
        print(f"  {i}. {day}")
    
    user_input = input("Enter numbers (e.g., 1,3,5) or press Enter for Mon-Fri: ").strip()
    if not user_input:
        return [0, 1, 2, 3, 4]
    try:
        selected = [int(x.strip()) - 1 for x in user_input.split(",") if x.strip().isdigit()]
        selected = [x for x in selected if 0 <= x <= 4]
        return sorted(list(set(selected))) if selected else [0, 1, 2, 3, 4]
    except ValueError:
        return [0, 1, 2, 3, 4]

def get_numeric_input(prompt, default_val):
    while True:
        user_val = input(f"{prompt} (Default: {default_val}): ").strip()
        if not user_val:
            return float(default_val)
        try:
            val = float(user_val)
            if val < 0:
                print("  ! Please enter a positive number.")
                continue
            return val
        except ValueError:
            print("  ! Invalid input. Please enter a number.")

def get_valid_date_input(prompt, work_days_indices):
    us_holidays = holidays.US()
    days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    while True:
        start_str = input(f"{prompt} (YYYY-MM-DD) or press Enter for Today: ").strip()
        if not start_str:
            target_date = datetime.date.today()
        else:
            try:
                target_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
            except ValueError:
                print("  ! Invalid format. Please use YYYY-MM-DD.")
                continue
        
        if target_date.weekday() not in work_days_indices:
            print(f"  ! {days_map[target_date.weekday()]} is not a scheduled work day.")
        elif target_date in us_holidays:
            print(f"  ! {target_date} is a holiday.")
        else:
            return target_date

def main_interactive():
    HOURS_PER_DAY = 7.0

    while True:
        print("\n" + "="*55 + "\n      ARCHIVAL PROJECT PLANNER\n" + "="*55)
        
        print("--- STEP 1: COLLECTION EXTENT ---")
        lin = get_numeric_input("Linear feet", 0)
        ami = get_numeric_input("AMI recordings", 0)
        car = get_numeric_input("Digital carriers", 0)
        gb  = get_numeric_input("Gigabytes", 0)

        print("\n--- STEP 2: PROCESSING RATES ---")
        r_lin = get_numeric_input("Lin ft per day", 1.0) if lin > 0 else 1.0
        r_ami = get_numeric_input("AMI per day", 30.0) if ami > 0 else 30.0
        r_car = get_numeric_input("Carriers per day", 1.0) if car > 0 else 1.0
        r_gb  = get_numeric_input("GB per day", 0.2) if gb > 0 else 0.2

        print("\n--- STEP 3: WORK DAYS AND STAFFING ---")
        staff = get_numeric_input("Staff members (FTE)", 1.0)
        work_days_indices = get_work_days_input()
        start_date = get_valid_date_input("Start date", work_days_indices)

        confirm = input("\nRun calculation with these values? (y/n): ").strip().lower()
        if confirm != 'n': break

    # Logic: Effort = Quantity / Rate
    efforts = {
        'Physical (Lin Ft)': (lin / r_lin) if lin > 0 and r_lin > 0 else 0,
        'AMI Recordings': (ami / r_ami) if ami > 0 and r_ami > 0 else 0,
        'Digital Carriers': (car / r_car) if car > 0 and r_car > 0 else 0,
        'Digital (GB)': (gb / r_gb) if gb > 0 and r_gb > 0 else 0
    }

    total_days = sum(efforts.values())
    if total_days == 0:
        print("\nNo workload entered.")
        return

    pp_stats, calendar_days = get_calendar_stats(total_days, staff, work_days_indices)
    end_date = get_completion_date(start_date, calendar_days, work_days_indices)
    
    # Final Report
    print("\n" + "="*55)
    print(f"ESTIMATED COMPLETION: {end_date.strftime('%A, %B %d, %Y')}")
    print("-" * 55)
    print(f"Total Effort:      {round(total_days, 2)} Working Days")
    print(f"Staff (FTE):       {staff:g}")
    print(f"Calendar Duration: {pp_stats[0]} Years, {pp_stats[1]} Months, {round(pp_stats[2], 1)} Days")
    print("="*55 + "\n")

    # Plotting the Results
    labels = [k for k, v in efforts.items() if v > 0]
    values = [v for v in efforts.values() if v > 0]

    if labels:
        plt.figure(figsize=(10, 6))
        colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853']
        bars = plt.bar(labels, values, color=colors[:len(labels)])
        plt.title(f'Effort Breakdown: {round(total_days, 1)} Total Working Days', fontsize=14)
        plt.ylabel('Days of Labor')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main_interactive()