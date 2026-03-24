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
    """Steps through calendar, only counting scheduled workdays."""
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
    """Allows user to select specific work days."""
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
    """Shows the default value in the prompt and uses it if input is empty."""
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
    """Ensures start date isn't a weekend or holiday."""
    us_holidays = holidays.US()
    days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
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
            day_name = days_map[target_date.weekday()]
            print(f"  ! {day_name} is not one of your scheduled work days.")
        elif target_date in us_holidays:
            print(f"  ! {target_date} is a holiday. Please choose a different start date.")
        else:
            return target_date

def main_interactive():
    HOURS_PER_DAY = 7.0  # Hardcoded hours, but can be revised

    while True:
        print("\n" + "="*55)
        print("      ARCHIVAL PROJECT PLANNER")
        print("="*55)
        print("Press Enter to accept the (Default) values.\n")

        # 1. Quantities
        print("--- STEP 1: COLLECTION EXTENT ---")
        lin = get_numeric_input("Linear feet of physical records", 0)
        ami = get_numeric_input("Number of AMI recordings", 0)
        car = get_numeric_input("Number of digital carriers", 0)
        gb  = get_numeric_input("Gigabytes of digital files", 0)

        # 2. Custom Rates
        print("\n--- STEP 2: PROCESSING RATES ---")
        r_lin = get_numeric_input("Linear feet processed per day", 1.0) if lin > 0 else 1.0
        r_ami = get_numeric_input("AMI recordings processed per day", 30.0) if ami > 0 else 30.0
        r_car = get_numeric_input("Digital carries per day", 1.0) if car > 0 else 1.0
        r_gb  = get_numeric_input("Gigabytes per day", 0.2) if gb > 0 else 0.2 #equivelent to 5 days per GB

        # 3. Project Settings
        print("\n--- STEP 3: WORK DAYS AND STAFFING ---")
        staff = get_numeric_input("Number of staff members (FTE)", 1.0)
        work_days_indices = get_work_days_input()
        start_date = get_valid_date_input("Start date", work_days_indices)

        # 4. Verification Step
        print("\n" + "-"*35)
        print("PLEASE REVIEW THE FOLLOWING:")
        if lin > 0: print(f" - Physical: {lin} ft at {r_lin} ft/day")
        if ami > 0: print(f" - AMI: {ami} recs at {r_ami} rec/day")
        if car > 0: print(f" - Carriers: {car} at {r_car} carrier/day")
        if gb  > 0: print(f" - Digital: {gb} GB at {r_gb} days/GB")
        
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        selected_days = [day_names[i] for i in work_days_indices]
        sched_str = ", ".join(selected_days)
        print(f" - Team: {staff} staff working {HOURS_PER_DAY} hrs/day on: {sched_str}")
        print(f" - Start Date: {start_date.strftime('%A, %B %d, %Y')}")
        print("-" * 35)
        
        confirm = input("Is this information correct? (y/n): ").strip().lower()
        if confirm == 'n':
            print("\nResetting... please re-enter the data.")
            continue
        break

    # Calculation Logic
    lin_effort = (lin / r_lin) if r_lin > 0 else 0
    ami_effort = (ami / r_ami) if r_ami > 0 else 0
    total_days = lin_effort + ami_effort + (car * r_car) + (gb * r_gb)

    if total_days == 0:
        print("\nNo workload entered. Calculation cancelled.")
        return

    total_stats, pp_stats, calendar_days = get_calendar_stats(total_days, staff, work_days_indices)
    end_date = get_completion_date(start_date, calendar_days, work_days_indices)
    
    # Staff Hour Calculation
    total_hours = total_days * HOURS_PER_DAY

    # Final Report
    print("\n" + "="*55)
    print(f"ESTIMATED COMPLETION: {end_date.strftime('%A, %B %d, %Y')}")
    print("-" * 55)
    print(f"Team Size:         {staff} Staff (FTE)")
    print(f"Schedule:          {sched_str} ({len(work_days_indices)} days/week at {HOURS_PER_DAY} hrs/day)")
    print(f"Total Effort:      {round(total_days, 2)} Working Days")
    print(f"Total Staff Hours: {round(total_hours, 1)} Hours")
    print(f"Calendar Duration: {pp_stats[0]} Years, {pp_stats[1]} Months, {round(pp_stats[2], 1)} Days")
    print("-" * 55)
    print("RATES USED FOR CALCULATION:")
    if lin > 0: print(f" - Physical: {r_lin} ft/day")
    if ami > 0: print(f" - AMI:      {r_ami} rec/day")
    if car > 0: print(f" - Carriers: {r_car} carrier/day")
    if gb  > 0: print(f" - Digital:  {r_gb} days/GB")
    print("="*55 + "\n")

if __name__ == "__main__":
    main_interactive()