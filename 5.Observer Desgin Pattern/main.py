from observer import Observer
from tv import Tvdisplay
from weather_station import WeatherStation
from mobile import Mobile_display

ws = WeatherStation()
tv = Tvdisplay()
mobile = Mobile_display()

ws.add_obeserver(tv)
ws.add_obeserver(mobile)
ws.update_temp(30)