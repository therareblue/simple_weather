import pytz
from timezonefinder import TimezoneFinder
import datetime
import time

import requests

app_id = "your_app_id" #your APP ID from openweathermap.org. It's free, just register.

#--------------------- BASIC FUNCTIONS --------------------
def show(msg):
    if isinstance(msg, tuple):
        for m in msg:
            print(m)
    else:
        print(msg)

def ask(qst="Answer [or type \"x\" to exit] >>"):
    a = input(qst)
    return a

#------------------- LOCATION PREPARE ---------------------
def get_coordinates(city_name):
    api_link = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={app_id}"
    get_response = requests.get(api_link).json()

    if not get_response:
        raise Exception('City you entered is invalid!')
    else:
        # Get the latitude, longitude and country of a city
        latitude = get_response[0]['lat']
        longitude = get_response[0]['lon']
        real_name = get_response[0]['name']
        country = get_response[0]['country']

        # Get time zone for that coordinates
        tf = TimezoneFinder()
        tzn = pytz.timezone(tf.timezone_at(lng=longitude, lat=latitude))

        return latitude, longitude, real_name, country, tzn

def timestamp_to_friendly_time(tmstamp, timezone=None): #get time with TODAY/TOMORROW / Weekday stamp
    if timezone:
        dt = datetime.datetime.fromtimestamp(tmstamp, timezone)
        dt_now = datetime.datetime.now(timezone)
    else:
        dt = datetime.datetime.fromtimestamp(tmstamp)
        dt_now = datetime.datetime.now()

    wk_day = datetime.datetime.weekday(dt)
    #hr = datetime.datetime.hour(dt)
    hr = int(datetime.datetime.strftime(dt, '%I'))
    mnt = datetime.datetime.strftime(dt, '%M')
    am_pm = datetime.datetime.strftime(dt, "%p") #get AM / PM sign

    wk_decode = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    #noon_dec = {"morning": 8, "noon": 12, "lunch": 12, "afternoon": 16, "evening": 20}

    days = int(datetime.datetime.strftime(dt, '%j')) #return day of the year 0-365

    days_now = int(datetime.datetime.strftime(dt_now, '%j'))
    if days == days_now:
        day_name_decode = 'today'
    elif abs(days - days_now) == 1:
        day_name_decode = 'tomorrow'
    else:
        day_name_decode = wk_decode[wk_day]

    return {'weekday': day_name_decode, 'hours': hr, 'minutes': mnt, 'am_pm': am_pm}

#---------------------- GET WEATHER -----------------------
def wind_decode(w_speed, w_deg):
    w_dir = None #, comming from North.
    description = None

    if w_deg > 349 and w_deg <= 360 or w_deg >= 0 and w_deg <= 11: w_dir = 'North'
    elif w_deg > 11 and w_deg <= 34: w_dir = 'North North East'
    elif w_deg > 34 and w_deg <= 56: w_dir = 'North East'
    elif w_deg > 56 and w_deg <= 79: w_dir = 'East North East'
    elif w_deg > 79 and w_deg <= 101: w_dir = 'East'
    elif w_deg > 101 and w_deg <= 124: w_dir = 'East South East'
    elif w_deg > 124 and w_deg <= 146: w_dir = 'South East'
    elif w_deg > 146 and w_deg <= 170: w_dir = 'South South East'
    elif w_deg > 170 and w_deg <= 191: w_dir = 'South'
    elif w_deg > 191 and w_deg <= 214: w_dir = 'South South West'
    elif w_deg > 214 and w_deg <= 236: w_dir = 'South West'
    elif w_deg > 236 and w_deg <= 259: w_dir = 'West South West'
    elif w_deg > 259 and w_deg <= 281: w_dir = 'West'
    elif w_deg > 281 and w_deg <= 304: w_dir = 'West North West'
    elif w_deg > 304 and w_deg <= 326: w_dir = 'North West'
    elif w_deg > 326 and w_deg <= 349: w_dir = 'North North West'

    if w_speed == 0: description = "no wind"
    elif w_speed > 0 and w_speed <= 5: description = f"light breeze coming from {w_dir}"
    elif w_speed > 5 and w_speed <= 10: description = f"moderate wind coming from {w_dir}"
    elif w_speed > 10 and w_speed <= 20: description = f"strong wind coming from {w_dir}"
    elif w_speed > 20: description = f"storm wind coming from {w_dir}"

    return description


def search_for_event_hourly(hourly_list, timezone, current, search_from, search_to,
                            search_for=False):  # already started se zasicha ot current_weather. Taka she znae da tarsi po drug nachin
    if search_to == 0 or search_to > len(
            hourly_list) - 1:  # ako tyrseniq period nadvishava chasovata prognoza, se tarsi do kraq na chasovata prognoza
        search_to = len(hourly_list) - 1
    else:
        search_to = search_from + search_to  # search_to  --- e broi zapisi koito da se tarsqt. za da stane rendj, trqbwa da se sabere sas search_from
    # print(f"FROM: {search_from}; TO: {search_to}")
    event_descr = ""
    event_descr_1 = ""
    now_is0 = ""
    now_is = ""
    search_flag = False
    what_expected_to_stop = ""
    if current['main'] in ['Rain', 'Thunderstorm', 'Drizzle', 'Tornado', 'Snow']:
        if search_for:
            if current['main'] in search_for and search_from == 0: search_flag = True
        now_is0 = f"There is {current['description']} outside already."
        what_expected_to_stop = current['main']
        # it will rain all day / it is expected to stop at ..... today / tomorrow
        stop_time = 0
        stop_time0 = 0
        i = 0
        will_change_flag = False
        for elem in hourly_list:
            if elem['weather'][0]['main'] in ['Rain', 'Thunderstorm', 'Drizzle', 'Tornado', 'Snow']:
                if elem['weather'][0]['main'] != current['main']:
                    if not will_change_flag:
                        change_time = timestamp_to_friendly_time(elem['dt'], timezone)
                        change_day = ''
                        if change_time['weekday'] == 'today':
                            change_day = ''
                        elif change_time['weekday'] == 'tomorrow':
                            change_day = ' tomorrow'
                        else:
                            change_day = f"on {change_time['weekday']}"
                        now_is += f" It may change to {elem['weather'][0]['description']} around {change_time['hours']}{change_time['am_pm']}{change_day}. "
                        what_expected_to_stop = elem['weather'][0]['main']
                        will_change_flag = True
                i = 0
                stop_time0 = 0
            else:
                if i == 0: stop_time0 = elem['dt']
                i += 1  # ako imame 3 poredni chasa spral dajd, spirame
                if i >= 3:
                    # stop_time = elem['dt']
                    stop_time = stop_time0
                    break
        if stop_time == 0:
            if will_change_flag:
                now_is += "and it won't stop in the next 48 hours."
            else:
                now_is += "It won't stop in the next 48 hours."
        else:
            friendly_time = timestamp_to_friendly_time(stop_time, timezone)
            if friendly_time['weekday'] in "today tomorrow":
                now_is += f"The {what_expected_to_stop} is expected to stop at {friendly_time['hours']}{friendly_time['am_pm']} {friendly_time['weekday']}."
            else:
                now_is += f"The {what_expected_to_stop} is expected to stop on {friendly_time['weekday']} arount {friendly_time['hours']}{friendly_time['am_pm']}."

    else:  # ako ne vali v momenta,
        now_is = ""

    # check for speciffic search... / initializing:
    if search_for and not search_flag:
        event_descr_1 = "No."

        for index in range(search_from, search_to):
            l_main = hourly_list[index]['weather'][0]['main']
            l_descr = hourly_list[index]['weather'][0]['description'].lower()
            start_time_dic = timestamp_to_friendly_time(hourly_list[index]['dt'], timezone)
            if start_time_dic['weekday'] in "today tomorrow":  # samo smenq izkazvaneto, kato dobavq "ON wenesday"
                when_start = f"{start_time_dic['hours']}{start_time_dic['am_pm']} {start_time_dic['weekday']}"
            else:
                when_start = f"{start_time_dic['hours']}{start_time_dic['am_pm']} on {start_time_dic['weekday']}"
            if l_main == 'Rain' and l_main.lower() in search_for:
                if l_descr == "light rain":
                    event_descr_1 = f"Yes. There is a chance of light rain at {when_start}, about {round(hourly_list[index]['rain']['1h'], 1)}mm for one hour."
                    break
                elif l_descr == "shower rain":
                    event_descr_1 = f"Yes. Expected showers at {when_start}, about {round(hourly_list[index]['rain']['1h'], 1)}mm for one hour."
                    break
                elif l_descr in ["moderate rain", "freezing rain", "light intensity" "shower rain"]:
                    event_descr_1 = f"Yes. There is a chance of rain at {when_start}, about {round(hourly_list[index]['rain']['1h'], 1)}mm for one hour."
                    break
                elif l_descr in ["heavy intensity rain", "very heavy rain", "extreme rain", "heavy intensity rain"]:
                    event_descr_1 = f"Yes. Heavy rain is expected at {when_start}, about {round(hourly_list[index]['rain']['1h'], 1)}mm for one hour. Be aware!"
                    break
                elif l_descr in ["heavy intensity shower rain", "ragged shower rain"]:
                    event_descr_1 = f"Yes. There is warning of heavy showers coming at {when_start}, about {round(hourly_list[index]['rain']['1h'], 1)}mm for one hour."
                    break
                else:
                    event_descr_1 = f"Yes. There is a chance of rain at {when_start}, about {round(hourly_list[index]['rain']['1h'], 1)}mm for one hour."
                    break
            elif l_main == 'Thunderstorm' and l_main.lower() in search_for:
                if l_descr == "thunderstorm":
                    event_descr_1 = f"There is a chance of thunderstorm at {when_start}."
                    break
                elif l_descr in ["thunderstorm with heavy rain", "heavy thunderstorm",
                                 "thunderstorm with heavy drizzle"]:
                    event_descr_1 = f"Yes. Heavy thunderstorm expected at {when_start}. Be aware!"
                    break
                elif l_descr == "ragged thunderstorm":
                    event_descr = f"There is a warning of ragged thunderstorm at {when_start}. Be careful!"
                    break
                else:
                    event_descr_1 = f"There is a chance of thunderstorm at {when_start}."
                    break
            elif l_main == 'Drizzle' and l_main.lower() in search_for:
                event_descr_1 = f"Yes. Drizzle expected at {when_start}."
                break
            elif l_main == 'Tornado' and l_main.lower() in search_for:
                event_descr_1 = f"There is a warning of tornado around {when_start}. Be careful!"
                break
            elif l_main == 'Snow' and l_main.lower() in search_for:
                if l_descr == "heavy shower snow" or l_descr == "heavy snow" or l_descr == "shower snow" or l_descr == "shower sleet":
                    event_descr_1 = f"Yes. A heavy snow is expected at {when_start}, about {round(hourly_list[index]['snow']['1h'], 1)}mm for one hour."
                    break
                elif l_descr == "rain and snow" or l_descr == "light rain and snow":
                    event_descr_1 = f"There is a chance of rain and snow mixed, at {when_start}, about {round(hourly_list[index]['snow']['1h'] + hourly_list[index]['rain']['1h'], 1)}mm for one hour."
                    break
                else:
                    event_descr_1 = f"Yes. A snow is expected at {when_start}, about {round(hourly_list[index]['snow']['1h'], 1)}mm for one hour."
                    break

    if event_descr_1 == "" or event_descr_1 == "No.":
        if search_from == 0:
            event_descr = "Nothing expected in the next few hours."
        else:
            event_descr = "Nothing is expected for this time."
        # if there is event found, nothing expected became the name of event.
        for index in range(search_from, len(hourly_list) - 1):
            l_main = hourly_list[index]['weather'][0]['main']
            l_descr = hourly_list[index]['weather'][0]['description'].lower()
            start_time_dic = timestamp_to_friendly_time(hourly_list[index]['dt'], timezone)
            if start_time_dic['weekday'] in "today tomorrow":
                when_start = f"{start_time_dic['hours']}{start_time_dic['am_pm']} {start_time_dic['weekday']}"
            else:
                when_start = f"{start_time_dic['hours']}{start_time_dic['am_pm']} on {start_time_dic['weekday']}"

            if l_main == 'Rain':
                if l_descr == "light rain":
                    event_descr = f"There is a chance of light rain at {when_start}."
                    break
                elif l_descr == "shower rain":
                    event_descr = f"Expected showers at {when_start}."
                    break
                elif l_descr in ["moderate rain", "freezing rain", "light intensity" "shower rain"]:
                    event_descr = f"There is a chance of rain at {when_start}."
                    break
                elif l_descr in ["heavy intensity rain", "very heavy rain", "extreme rain", "heavy intensity rain"]:
                    event_descr = f"Heavy rain is expected at {when_start}. Be aware!"
                    break
                elif l_descr in ["heavy intensity shower rain", "ragged shower rain"]:
                    event_descr = f"Heavy showers expected at {when_start}"
                    break
                else:
                    event_descr = f"There is a chance of rain at {when_start}"
                    break
            elif l_main == 'Thunderstorm':
                if l_descr == "thunderstorm":
                    event_descr = f"There is a chance of thunderstorm at {when_start}."
                    break
                elif l_descr in ["thunderstorm with heavy rain", "heavy thunderstorm",
                                 "thunderstorm with heavy drizzle"]:
                    event_descr = f"Heavy thunderstorm expected at {when_start}. Be aware!"
                    break
                elif l_descr == "ragged thunderstorm":
                    event_descr = f"There is a warning of ragged thunderstorm at {when_start}. Be careful!"
                    break
                else:
                    event_descr = f"There is a chance of thunderstorm at {when_start}."
                    break
            elif l_main == 'Drizzle':
                event_descr = f"There is a chance of drizzle at {when_start}."
                break
            elif l_main == 'Tornado':
                event_descr = f"There is a warning of tornado around {when_start}. Be careful!"
                break
            elif l_main == 'Snow':
                if l_descr == "heavy shower snow" or l_descr == "heavy snow" or l_descr == "shower snow" or l_descr == "shower sleet":
                    event_descr = f"A heavy snow expected at {when_start}."
                    break
                elif l_descr == "rain and snow" or l_descr == "light rain and snow":
                    event_descr = f"There is a chance of rain and snow mixed, at {when_start}."
                    break
                else:
                    event_descr = f"A snow is expected at {when_start}."
                    break
    # print (f"-------->>Now: {now_is}; 1: {event_descr_1}; ed: {event_descr}")
    if not now_is and event_descr_1 == "No." and 'Nothing' not in event_descr:
        out_stamp = f"{event_descr_1} But {event_descr}"
    elif not now_is and not search_for:
        out_stamp = event_descr
    elif not now_is:
        out_stamp = f"{event_descr_1} {event_descr}"
    elif now_is and search_from == 0 and event_descr_1 == "No.":
        out_stamp = f"{event_descr_1} But {now_is0} {now_is}"
    elif now_is and search_from == 0 and not search_for:
        out_stamp = now_is
    elif now_is and search_from == 0 and search_for:
        out_stamp = f"{now_is0} {now_is}"
    elif now_is and search_from != 0 and search_for and event_descr_1 == "No." and 'Nothing' not in event_descr:
        out_stamp = f"{event_descr_1} But {event_descr}"
    elif now_is and search_from != 0 and search_for and event_descr_1 and event_descr_1 != "No.":
        out_stamp = event_descr_1
    elif now_is and search_from != 0 and search_for and event_descr_1 == "No." and 'Nothing' in event_descr:
        out_stamp = f"{event_descr_1} {event_descr}"
    else:
        out_stamp = ""

    return out_stamp

def get_weather(latitude, longitude):
    api_link1 = f"https://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&appid={app_id}&units=metric&exclude=minutely"
    api_link2 = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={app_id}"

    weather = requests.get(api_link1).json()
    pollution = requests.get(api_link2).json()

    if 'cod' in weather or 'cod' in pollution:
        raise Exception("Coordinates you've entered are invalid!")
    else:
        return weather, pollution

def whats_the_weather(city_name):
    try:
        city_info = get_coordinates(city_name)
        weather, pollution = get_weather(city_info[0], city_info[1])

        show(f"City Information:")
        show(city_info)
        show(f"Current Weather:")

        time_now = weather['current']['dt']
        timezone = pytz.timezone(weather['timezone'])
        friendly_time_now = timestamp_to_friendly_time(time_now, timezone)
        local_stamp = f"{friendly_time_now['hours']}:{friendly_time_now['minutes']}{friendly_time_now['am_pm']}"

        weather_block = weather['current']

        #Get the Sunset info:
        sun_info = None
        if weather_block['dt'] > weather_block['sunset']:
            sun_info = "The Sun has set already."
        else:
            if weather_block['dt'] < weather_block['sunrise']:
                sunrise_dic = timestamp_to_friendly_time(weather['current']['sunrise'], timezone=timezone)
                sun_info = f"The Sun will rise at {sunrise_dic['hours']}:{sunrise_dic['minutes']}{sunrise_dic['am_pm']}."
            else:
                sunset_dic = timestamp_to_friendly_time(weather['current']['sunset'], timezone=timezone)
                sun_info = f"The Sun will set at {sunset_dic['hours']}:{sunset_dic['minutes']}{sunset_dic['am_pm']}."

        # Get the Wind info:
        wind_info = wind_decode(weather_block['wind_speed'], weather_block['wind_deg'])

        # Get Clouds info:
        if weather['current']['clouds'] < 10: clouds_stamp = "no clouds"
        else: clouds_stamp = f"{weather['current']['clouds']} percent cloud density"

        # Get Air quality:
        air_quality_decode = ["", "Air quality is very good.", "Air quality is fair.", "Air quality is not perfect.",
                              "Be aware of a poor air quality.",
                              "Air quality is Very bad. You should wear protective equipment."]

        # Get Visibility Warning:
        if weather['current']['visibility'] == 1:
            visib_warning = f"Visibility is {weather['current']['visibility']} meter, so be very careful on road."
        elif 1 < weather['current']['visibility'] <= 70:
            visib_warning = f"Visibility is {weather['current']['visibility']} meters, so be careful on road."
        elif 70 < weather['current']['visibility'] < 500:
            visib_warning = f"Visibility is {weather['current']['visibility']} meters."
        else:
            visib_warning = ""

        # Get the chance of event:
        event_descr = search_for_event_hourly(weather['hourly'], timezone, weather['current']['weather'][0], 0, 0)  # get the chance of event for the main forecast.

        #---- COMBINE ALL TOGETHER ---
        weather_info = f"The weather in {city_info[2]} is {round(weather['current']['temp'], 1)} degrees with {weather['current']['weather'][0]['description']} and {wind_info}. It feels like {round(weather['current']['feels_like'], 1)} degrees. Local time is {local_stamp}. {air_quality_decode[pollution['list'][0]['main']['aqi']]} {visib_warning} {event_descr} {sun_info}"

        show(weather_info)

    except Exception as e:
        show("I can't find information for this location.")
        show(e)


#--------------------- GET FORECAST -----------------------
#pass

#----------------------------------------------------------
#========================= MAIN ===========================
while True:
    answer = ask("Enter your town name [or type \"x\" to exit] > ")
    if answer == "x":
        break
    else:
        whats_the_weather(answer)

