import time, request




class WeatherEntry():
    
    
    def __init__(self, timezoneOffset, entry):
        self.entry = entry
        self.timezoneOffset = timezoneOffset


    def formatTime(self, tm):
        (year, day, month, hour, minute, second, weekday, yearday) = time.gmtime(tm)
        format = '{hour:02d}:{minute:02d}'
        return format.format(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
    
    def date(self):
        return self.entry['dt'] + self.timezoneOffset

    def sunrise(self):
        return self.formatTime(self.entry['sunrise'] + self.timezoneOffset)

    def sunset(self):
        return self.formatTime(self.entry['sunset'] + self.timezoneOffset)

    def temperature(self):
        return int(round(self.entry['temp'], 0))
    
    def minTemperature(self):
        return int(round(self.entry['temp']['min']))
        
    def maxTemperature(self):
        return int(round(self.entry['temp']['max']))

    def weatherDescription(self):
        return self.entry['weather'][0]['description']


class OpenWeatherMap():
    
    def __init__(self, appid, lat, long):
        self.timezoneOffset = None
        self.appid = appid
        self.lat = lat
        self.long = long
        
    
    def fetch(self):
        
        
        params = {
            'url': 'http://api.openweathermap.org/data/2.5/onecall',
            'appid': self.appid,
            'lat': self.lat,
            'lon': self.long,
            'units': 'metric',
            'lang': 'sv'
        }
        
        url = '{url}?exclude=minutely,hourly&appid={appid}&lat={lat}&lon={lon}&lang={lang}&units={units}'
        url = url.format(url = params['url'], appid = params['appid'], lat = params['lat'], lon = params['lon'], units = params['units'], lang = params['lang'])
        
        response = request.get(url)
        response = response.json()

        self.timezoneOffset = int(response['timezone_offset'])
        
        self.daily = []
        
        for index in range(8):
            self.daily.append(WeatherEntry(self.timezoneOffset, response['daily'][index]))

        self.response = response
        self.current  = WeatherEntry(self.timezoneOffset, response['current'])
        self.today    = self.daily[0]
        self.tomorrow = self.daily[1]
        


if __name__ == '__main__':

    class App():
        
        
        def __init__(self):
         
            
            from wifi import WiFi
            from secrets import WIFI_SSID, WIFI_PASSWORD
            from mqtt import MQTTClient
            
            from secrets import MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD, MQTT_TOPIC, MQTT_PORT
            
            self.mqtt = MQTTClient(client_id = 'MEG', server = MQTT_HOST, user = MQTT_USERNAME, password = MQTT_PASSWORD, port = MQTT_PORT, keepalive = 60)

            wifi = WiFi()
            wifi.connect(ssid = WIFI_SSID, password = WIFI_PASSWORD)


        def fetchWeather(self):
            from secrets import OPEN_WEATHER_APPID
            
            weather = OpenWeatherMap(OPEN_WEATHER_APPID, lat = 55.71, long = 13.19)
            
            weather.fetch()

            text = 'Just nu {A} och {B}°'
            text = text.format(A = weather.current.weatherDescription(), B = weather.current.temperature())
            yield text

            text = 'Soluppgång {A} - solnedgång {B}'
            text = text.format(A = weather.current.sunrise(), B = weather.current.sunset())
            yield text

            text = 'I morgon {A} och {B}° ({C}°)'
            text = text.format(A = weather.daily[1].weatherDescription(), B = weather.daily[1].maxTemperature(), C = weather.daily[1].minTemperature())
            yield text

            text = 'I övermorgon {A} och {B}° ({C}°)'
            text = text.format(A = weather.daily[2].weatherDescription(), B = weather.daily[2].maxTemperature(), C = weather.daily[2].minTemperature())
            yield text
            
            
            
        def run(self):
            for text in self.fetchWeather():
                
                self.mqtt.connect()
                self.mqtt.publish(topic = 'Matrix/64x32', msg = text.encode('utf-16'), retain = True)
                self.mqtt.disconnect()
                print(text)
        


    App().run()

