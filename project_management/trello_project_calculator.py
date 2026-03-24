"""script that reads trello duration field, start date, and days of week, and
   calculates end dates, and updates the card
   if there's nothing in the workdays field, the script calculates as if there are 5 days"""

import requests
import datetime
import holidays

"""replace section below with trello credetials
append .json to find identifer numbers and search for needed field """

API_KEY = 'API KEY' 
TOKEN = 'API TOKEN'
BOARD_ID = 'Board ID'
DURATION_FIELD_ID = 'Duration ID' # create custon field for project duration
WORKDAYS_FIELD_ID = 'Workdays ID' # create custon field for days of week

# US holiday calendar
holiday_calendar = holidays.US(years=range(datetime.datetime.now().year, datetime.datetime.now().year + 5))

def parse_trello_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    except Exception:
        return None

""""use weekday abbreviations in workdays field in trello"""
def parse_allowed_weekdays(days_str):
    day_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
    return sorted([day_map[d.strip().lower()[:3]] for d in days_str.split(',') if d.strip().lower()[:3] in day_map])

def calculate_end_date(start_date, duration_days, allowed_weekdays):
    current_date = start_date
    working_days_counted = 0

    while working_days_counted < duration_days:
        if current_date.weekday() in allowed_weekdays and current_date not in holiday_calendar:
            working_days_counted += 1
        if working_days_counted == duration_days:
            break
        current_date += datetime.timedelta(days=1)

    return current_date

# Get all cards from the board
cards_url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
cards_params = {
    'key': API_KEY,
    'token': TOKEN,
    'fields': 'name,start'
}
cards_response = requests.get(cards_url, params=cards_params)
cards = cards_response.json()
print(f'Found {len(cards)} cards on board')

# Process each card
for card in cards:
    card_id = card['id']
    name = card['name']
    start_date_str = card.get('start')

    if not start_date_str:
        print(f" Skipping card '{name}': No start date")
        continue

    start_date = parse_trello_date(start_date_str)
    if not start_date:
        print(f" Skipping card '{name}': Invalid start date format")
        continue

    original_start = start_date
    while start_date.weekday() >= 5 or start_date in holiday_calendar:
        start_date += datetime.timedelta(days=1)
    if original_start != start_date:
        print(f" Adjusted start date for '{name}' → {start_date}")

    # Get custom field values
    cf_url = f"https://api.trello.com/1/cards/{card_id}/customFieldItems"
    cf_params = {'key': API_KEY, 'token': TOKEN}
    cf_response = requests.get(cf_url, params=cf_params)
    cf_items = cf_response.json()

    duration_days = None
    allowed_weekdays = list(range(5))  # Default: Mon–Fri

    for item in cf_items:
        if item['idCustomField'] == DURATION_FIELD_ID:
            duration_days = int(float(item['value']['number']))
        elif item['idCustomField'] == WORKDAYS_FIELD_ID:
            days_text = item.get('value', {}).get('text', '')
            if days_text:
                allowed_weekdays = parse_allowed_weekdays(days_text)

    if duration_days is None:
        print(f" Skipping card '{name}': No duration field")
        continue

    end_date = calculate_end_date(start_date, duration_days, allowed_weekdays)
    iso_end_date = end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    update_url = f"https://api.trello.com/1/cards/{card_id}"
    update_params = {
        'key': API_KEY,
        'token': TOKEN,
        'due': iso_end_date
    }
    update_response = requests.put(update_url, params=update_params)

    if update_response.status_code == 200:
        print(f" Updated '{name}' → Due: {end_date.strftime('%m/%d/%Y')}")
    else:
        print(f" Failed to update '{name}': {update_response.text}")
