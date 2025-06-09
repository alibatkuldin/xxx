from dateutil.parser import isoparse
from collections import defaultdict
from datetime import datetime
import json
import phonenumbers
from phonenumbers import geocoder

def filter_data(data, filters):
    if not filters:
        return data
    start_time = isoparse(filters.get("start_time")) if filters.get("start_time") else None
    end_time = isoparse(filters.get("end_time")) if filters.get("end_time") else None

    filtered_data = [
        val for val in data
        if (
            (filters.get("phone_number") is None or val.get("number") == filters.get("phone_number")) and
            (filters.get("type") is None or val.get("type") == filters.get("type")) and
            (filters.get("app") is None or val.get("app") == filters.get("app")) and
            (start_time is None or isoparse(val.get("timestamp")) >= start_time) and
            (end_time is None or isoparse(val.get("timestamp")) <= end_time)
        )
    ]

    return filtered_data
def statistics_generator(data, filters = None):
    result = {}
    filtered_data = filter_data(data, filters)
    incom_outgo_calls = get_incoming_outgoing_calls(filtered_data)
    call_duration_statistics = get_call_duration_statistics(filtered_data, incom_outgo_calls[0], incom_outgo_calls[1])
    call_apps = get_call_apps(filtered_data)
    key_contacts = get_key_contacts(filtered_data)
    activity_periods = get_most_active_periods(filtered_data)
    country_activity = get_key_countries(filtered_data)
    city_activity = get_key_cities(filtered_data)

    result["incoming"] = incom_outgo_calls[0]
    result["outgoing"] = incom_outgo_calls[1]
    result["call_duration"] = call_duration_statistics
    result["call_apps"] = call_apps
    result["key_contacts"] = key_contacts
    result["activity_periods"] = activity_periods
    result["country_activity"] = country_activity
    result["city_activity"] = city_activity
    return result

def get_incoming_outgoing_calls(data):
    incoming = 0
    outgoing = 0

    for val in data:
        if val.get("type") == "incoming":
            incoming += 1
        elif val.get("type") == "outgoing":
            outgoing += 1
    return (incoming, outgoing)

def get_call_duration_statistics(data, incoming_calls=1, outgoing_calls=1):
    if not data:
        return {
            'total_calls': {
                'amount': 0,
                'average_duration': 0,
                'max_duration': 0,
                'min_duration': 0
            },
            'incoming_calls': {
                'amount': 0,
                'average_duration': 0,
                'max_duration': 0,
                'min_duration': 0
            },
            'outgoing_calls': {
                'amount': 0,
                'average_duration': 0,
                'max_duration': 0,
                'min_duration': 0
            }
        }

    total_calls = len(data)
    average_duration = 0
    max_duration = float('-inf')
    min_duration = float('inf')

    income_average_duration = 0
    max_income_duration = float('-inf')
    min_income_duration = float('inf')

    outgoing_average_duration = 0
    max_outgoing_duration = float('-inf')
    min_outgoing_duration = float('inf')

    for val in data:
        duration = val.get("duration", 0)
        average_duration += duration

        if duration > max_duration:
            max_duration = duration
        if duration < min_duration:
            min_duration = duration

        if val.get("type") == "incoming":
            income_average_duration += duration
            if duration > max_income_duration:
                max_income_duration = duration
            if duration < min_income_duration:
                min_income_duration = duration
        elif val.get("type") == "outgoing":
            outgoing_average_duration += duration
            if duration > max_outgoing_duration:
                max_outgoing_duration = duration
            if duration < min_outgoing_duration:
                min_outgoing_duration = duration

    average_duration /= total_calls
    
    income_average_duration = income_average_duration / incoming_calls if incoming_calls else 0
    outgoing_average_duration = outgoing_average_duration / outgoing_calls if outgoing_calls else 0

    min_duration = min_duration if min_duration != float('inf') else 0
    min_income_duration = min_income_duration if min_income_duration != float('inf') else 0
    min_outgoing_duration = min_outgoing_duration if min_outgoing_duration != float('inf') else 0

    result = {
        'total_calls': {
            'amount': total_calls,
            'average_duration': round(average_duration, 1),
            'max_duration': max_duration,
            'min_duration': min_duration
        },
        'incoming_calls': {
            'amount': incoming_calls,
            'average_duration': round(income_average_duration, 1),
            'max_duration': max_income_duration,
            'min_duration': min_income_duration
        },
        'outgoing_calls': {
            'amount': outgoing_calls,
            'average_duration': round(outgoing_average_duration, 1),
            'max_duration': max_outgoing_duration,
            'min_duration': min_outgoing_duration
        }
    }

    return result


def get_call_apps(data):
    app_calls = defaultdict(lambda: {"incoming": 0, "outgoing": 0})
    
    for val in data:
        app = val.get("app")
        call_type = val.get("type")
        if app and call_type:
            if call_type in ["incoming", "outgoing"]:
                app_calls[app][call_type] += 1

    app_calls = dict(app_calls)
    return app_calls

def get_key_contacts(data):
    contact_calls = defaultdict(int)

    for val in data:
        phone_number = val.get("number")
        if phone_number:
            cc_key = phone_number + ' ' + val.get("name")
            contact_calls[cc_key] += 1

    sorted_contacts = dict(sorted(contact_calls.items(), key=lambda x: x[1], reverse=True))
    return sorted_contacts


def get_most_active_periods(data):
    time_periods = {
        'morning_calls': (6, 12),       # 6 AM to 12 PM
        'afternoon_calls': (12, 18),    # 12 PM to 6 PM
        'evening_calls': (18, 24),      # 6 PM to 12 AM
        'night_calls': (0, 6)           # 12 AM to 6 AM
    }

    activity_counts = defaultdict(lambda: defaultdict(int))

    for val in data:
        timestamp = isoparse(val.get("timestamp"))
        if timestamp:
            call_time = timestamp
            day = call_time.date()
            hour = call_time.hour

            for period, (start_hour, end_hour) in time_periods.items():
                if start_hour <= hour < end_hour or (start_hour == 0 and hour < end_hour):
                    activity_counts[str(day)][period] += 1
                    break

    activity_counts = {
        day: {
            **periods,
            'total_calls': sum(periods.values())
        }
        for day, periods in activity_counts.items()
    }

    sorted_activity = dict(sorted(activity_counts.items(), key=lambda x: sum(x[1].values()), reverse=True))
    return sorted_activity

def get_key_countries(data):
    with open('country_codes.json', 'r', encoding='utf-8') as file:
        countries = json.load(file)

    country_code_map = {}
    for country, codes in countries.items():
        for code in codes:
            country_code_map[code] = country

    country_call_counts = defaultdict(int)
    for call in data:
        number = call['number']
        matched_country = None
        for code in sorted(country_code_map.keys(), key=len, reverse=True):
            if number.startswith(code):
                matched_country = country_code_map[code]
                break
        if matched_country:
            country_call_counts[matched_country] += 1
        else:
            country_call_counts['Unknown'] += 1
    return country_call_counts

def get_key_cities(data):
    with open('city_codes.json', 'r', encoding='utf-8') as file:
        cities = json.load(file)

    city_code_map = {}
    for city in cities.items():
        city_code_map[city[1]] = city[0]
    
    city_call_counts = defaultdict(int)
    for call in data:
        if call['app'] != "unknown": continue
        if call['number'].startswith('+7'):
            number=call['number'][2:]
        elif call['number'].startswith('8'):
            number=call['number'][1:]
        else: continue
        matched_city = None
        for code in sorted(city_code_map.keys(), key=len, reverse=True):
            if number.startswith(code):
                matched_city = city_code_map[code]
                break
        if matched_city:
            city_call_counts[matched_city] += 1
        else:
            city_call_counts['mobile_call'] += 1
    return city_call_counts