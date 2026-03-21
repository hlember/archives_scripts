"”"uses holidays module to list holidays for a specific year.
year is hard coded and needs to be revised. 
also works for other countries' holidays"""

import holidays
us_holidays = holidays.US(years=2015) # revise for specific year

for date, name in sorted(us_holidays.items()):
    print(f"{date}: {name}")