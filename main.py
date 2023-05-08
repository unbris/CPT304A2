import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import pycountry
import requests
from geopy.geocoders import Nominatim


import webbrowser
# Function to search
# for country codes
weather_code = {
    0: 'clear sky',
    1: 'mainly clear', 2: 'partly cloudy', 3: 'overcast',
    45: 'fog', 48: 'depositing rime fog',
    51: 'light drizzle', 53: 'moderate drizzle', 55: 'dense drizzle',
    56: 'light freezing drizzle', 57: 'dense freezing drizzle',
    61: 'slight rain', 63: 'moderate rain', 65: 'heavy rain',
    66: 'light freezing rain', 67: 'dense freezing rain',
    71: 'slight snow fall', 73: 'moderate snow fall', 75: "heavy snow fall",
    77: 'snow grains',
    80: 'slight rain showers', 81: 'moderate rain showers', 82: 'violent rain showers',
    85: 'slight snow shower', 86: 'heavy snow showers',
    95: 'thunderstorm',
    96: 'thunderstorm with slight hail', 99: 'thunderstorm with heavy hail',
}

def open_hotel_search():
    if holiday_list.curselection():
        selected_date = holiday_list.get(holiday_list.curselection())
        date = selected_date.split(" - ")[0]
        city = city_entry.get()
        search_query = f"{city} hotels {date}"
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        webbrowser.open(url)
    else:
        weather_text.set("Please select a date from the list.")

def search_country_codes(query):
    countries = [
        country.alpha_2 for country in pycountry.countries.search_fuzzy(query)]
    return countries

# Function to get public holidays


def get_public_holidays(country_code):
    url = f'https://date.nager.at/api/v3/publicholidays/2023/{country_code}'
    response = requests.get(url)
    holidays = response.json()
    return holidays

# Function to handle the country search button click


def on_country_search_button_click():
    query = country_entry.get()
    country_codes = search_country_codes(query)
    country_code_combobox['values'] = country_codes
    country_code_combobox.current(0)

# Function to handle country code selection


def on_country_code_selected(event):
    country_code = country_code_combobox.get()
    holidays = get_public_holidays(country_code)
    filtered_holidays = filter_holidays_within_16_days(holidays)
    holiday_list.delete(0, tk.END)
    for holiday in filtered_holidays:
        holiday_list.insert(
            tk.END, f"{holiday['date']} - {holiday['name']} ({holiday['localName']})")

# Function to get longitude and latitude


def filter_holidays_within_16_days(holidays):
    today = datetime.today()
    next_16_days = today + timedelta(days=16)
    filtered_holidays = [
        holiday for holiday in holidays
        if today <= datetime.strptime(holiday['date'], '%Y-%m-%d') <= next_16_days
    ]
    return filtered_holidays


def get_longitude_latitude(city_name):
    if city_name == "suzhou":
        return 120.60, 31.30
    geolocator = Nominatim(user_agent="holiday_weather_app")
    location = geolocator.geocode(city_name)
    return location.longitude, location.latitude

# Function to check the weather
def get_weather(latitude, longitude, date, end_date):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=weathercode,temperature_2m_max,temperature_2m_min&forecast_days=1&start_date={date}&end_date={end_date}&timezone=Asia%2FSingapore"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data


# Function to handle the check weather button click
def plot_weather_data(weather_data):
    time = [datetime.strptime(t, "%Y-%m-%dT%H:%M")
            for t in weather_data['hourly']['time']]
    temperature = weather_data['hourly']['temperature_2m']

    fig, ax = plt.subplots()
    ax.plot(time, temperature, marker='o', linestyle='-')

    ax.set(xlabel='Time', ylabel='Temperature (°C)',
           title='Temperature Forecast')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.show()


def on_check_weather_button_click():
    if holiday_list.curselection():
        selected_date = holiday_list.get(holiday_list.curselection())
        date = selected_date.split(" - ")[0]
        city = city_entry.get()
        longitude, latitude = get_longitude_latitude(city)
        weather_data = get_weather(latitude, longitude, date, date)
        # plot_weather_data(weather_data)
        s = weather_data
        weather_text.set(f"""
Weather on {s['daily']['time'][0]} in {city}:
Weather: {weather_code[s['daily']['weathercode'][0]]}
Max temperature: {s['daily']['temperature_2m_max'][0]}
Min temperature: {s['daily']['temperature_2m_min'][0]}
""")
    else:
        weather_text.set("Please select a date from the list.")


# Function to get hotel information


def get_hotel_info(city_name):
    # Add your implementation here
    pass


# Create the main window
root = tk.Tk()
root.title("Holiday and Weather App")

# Create input elements
country_label = ttk.Label(root, text="Country:")
country_label.grid(column=0, row=0, sticky=tk.W)
country_entry = ttk.Entry(root)
country_entry.grid(column=1, row=0)
country_search_button = ttk.Button(
    root, text="Search", command=on_country_search_button_click)
country_search_button.grid(column=2, row=0)

country_code_label = ttk.Label(root, text="Country Code:")
country_code_label.grid(column=0, row=1, sticky=tk.W)
country_code_combobox = ttk.Combobox(root)
country_code_combobox.grid(column=1, row=1)
country_code_combobox.bind("<<ComboboxSelected>>", on_country_code_selected)

# Add city input elements
city_label = ttk.Label(root, text="City:")
city_label.grid(column=0, row=2, sticky=tk.W)
city_entry = ttk.Entry(root)
city_entry.grid(column=1, row=2)

# Add holiday list
holiday_label = ttk.Label(root, text="Holidays:")
holiday_label.grid(column=0, row=3, sticky=tk.W)
holiday_list = tk.Listbox(root)
holiday_list.grid(column=1, row=3, rowspan=4)

# Add check weather button
check_weather_button = ttk.Button(
    root, text="Check Weather", command=on_check_weather_button_click)
check_weather_button.grid(column=2, row=2)

# Add weather display
weather_label = ttk.Label(root, text="Weather:")
weather_label.grid(column=0, row=7, sticky=tk.W)
weather_text = tk.StringVar()
weather_display = ttk.Label(root, textvariable=weather_text)
weather_display.grid(column=1, row=7, sticky=tk.W)
hotel_search_button = ttk.Button(root, text="Search Hotels", command=open_hotel_search)
hotel_search_button.grid(column=2, row=3)

# Start the GUI event loop
root.mainloop()
