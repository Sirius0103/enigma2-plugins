# -*- coding: UTF-8 -*-
#
# Converter - MSNWeather
# Developer - Sirius
# Version 1.0
# Homepage - http://www.gisclub.tv
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from Tools.Directories import fileExists, pathExists
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config, configfile
from Components.Console import Console as iConsole
from Components.Language import language
from time import localtime, strftime
from datetime import date
from os import environ
from Poll import Poll
import datetime, time
import gettext
import math
import os

weather_city = config.plugins.weathermsn.city.value # 'Moscow,Russia'
degreetype = config.plugins.weathermsn.degreetype.value # 'C'
windtype = config.plugins.weathermsn.windtype.value # 'ms'
weather_location = config.osd.language.value.replace('_', '-') # 'ru-RU'

if weather_location == 'en-EN':
	weather_location = 'en-US'

time_update = 20
time_update_ms = 3000

class MSNWeather2(Poll, Converter, object):

	VFD = 1
	DATE = 2
	SHORTDATE = 3
	DAY = 4
	JDAY = 5
	SHORTDAY = 6
	LOCATION = 7
	TIMEZONE = 8
	LATITUDE = 9
	LONGITUDE = 10
	SUNRISE = 11
	SUNSET = 12
	SOLSTICE = 13
	MOONPHASE = 14
	MOONLIGHT = 15
	MOONPICON = 16
	TEMP = 17
	PICON = 18
	SKYTEXT = 19
	FEELSLIKE = 20
	HUMIDITY = 21
	WIND = 22
	WINDSPEED = 23
	DATE0 = 30
	SHORTDATE0 = 31
	DAY0 = 32
	SHORTDAY0 = 33
	TEMP0 = 34
	LOWTEMP0 = 35
	HIGHTEMP0 = 36
	PICON0 = 37
	SKYTEXT0 = 38
	PRECIP0 = 39
	DATE1 = 40
	SHORTDATE1 = 41
	DAY1 = 42
	SHORTDAY1 = 43
	TEMP1 = 44
	LOWTEMP1 = 45
	HIGHTEMP1 = 46
	PICON1 = 47
	SKYTEXT1 = 48
	PRECIP1 = 49
	DATE2 = 50
	SHORTDATE2 = 51
	DAY2 = 52
	SHORTDAY2 = 53
	TEMP2 = 54
	LOWTEMP2 = 55
	HIGHTEMP2 = 56
	PICON2 = 57
	SKYTEXT2 = 58
	PRECIP2 = 59
	DATE3 = 60
	SHORTDATE3 = 61
	DAY3 = 62
	SHORTDAY3 = 63
	TEMP3 = 64
	LOWTEMP3 = 65
	HIGHTEMP3 = 66
	PICOrad = 67
	SKYTEXT3 = 68
	PRECIP3 = 69
	DATE4 = 70
	SHORTDATE4 = 71
	DAY4 = 72
	SHORTDAY4 = 73
	TEMP4 = 74
	LOWTEMP4 = 75
	HIGHTEMP4 = 76
	PICON4 = 77
	SKYTEXT4 = 78
	PRECIP4 = 79

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		if type == "Vfd":
			self.type = self.VFD
		elif type == "Date":
			self.type = self.DATE
		elif type == "Shortdate":
			self.type = self.SHORTDATE
		elif type == "Day":
			self.type = self.DAY
		elif type == "Julianday":
			self.type = self.JDAY
		elif type == "Shortday":
			self.type = self.SHORTDAY
		elif type == "Location":
			self.type = self.LOCATION
		elif type == "Timezone":
			self.type = self.TIMEZONE
		elif type == "Latitude":
			self.type = self.LATITUDE
		elif type == "Longitude":
			self.type = self.LONGITUDE
		elif type == "Sunrise":
			self.type = self.SUNRISE
		elif type == "Sunset":
			self.type = self.SUNSET
		elif type == "Solstice":
			self.type = self.SOLSTICE
		elif type == "Moonphase":
			self.type = self.MOONPHASE
		elif type == "Moonlight":
			self.type = self.MOONLIGHT
		elif type == "PiconMoon":
			self.type = self.MOONPICON
		elif type == "Temp":
			self.type = self.TEMP
		elif type == "Picon":
			self.type = self.PICON
		elif type == "Skytext":
			self.type = self.SKYTEXT
		elif type == "Feelslike":
			self.type = self.FEELSLIKE
		elif type == "Humidity":
			self.type = self.HUMIDITY
		elif type == "Wind":
			self.type = self.WIND
		elif type == "Windspeed":
			self.type = self.WINDSPEED
#	today	#
		elif type == "Date0":
			self.type = self.DATE0
		elif type == "Shortdate0":
			self.type = self.SHORTDATE0
		elif type == "Day0":
			self.type = self.DAY0
		elif type == "Shortday0":
			self.type = self.SHORTDAY0
		elif type == "Temp0":
			self.type = self.TEMP0
		elif type == "Lowtemp0":
			self.type = self.LOWTEMP0
		elif type == "Hightemp0":
			self.type = self.HIGHTEMP0
		elif type == "Picon0":
			self.type = self.PICON0
		elif type == "Skytext0":
			self.type = self.SKYTEXT0
		elif type == "Precip0":
			self.type = self.PRECIP0
#	day 1	#
		elif type == "Date1":
			self.type = self.DATE1
		elif type == "Shortdate1":
			self.type = self.SHORTDATE1
		elif type == "Day1":
			self.type = self.DAY1
		elif type == "Shortday1":
			self.type = self.SHORTDAY1
		elif type == "Temp1":
			self.type = self.TEMP1
		elif type == "Lowtemp1":
			self.type = self.LOWTEMP1
		elif type == "Hightemp1":
			self.type = self.HIGHTEMP1
		elif type == "Picon1":
			self.type = self.PICON1
		elif type == "Skytext1":
			self.type = self.SKYTEXT1
		elif type == "Precip1":
			self.type = self.PRECIP1
#	day 2	#
		elif type == "Date2":
			self.type = self.DATE2
		elif type == "Shortdate2":
			self.type = self.SHORTDATE2
		elif type == "Day2":
			self.type = self.DAY2
		elif type == "Shortday2":
			self.type = self.SHORTDAY2
		elif type == "Temp2":
			self.type = self.TEMP2
		elif type == "Lowtemp2":
			self.type = self.LOWTEMP2
		elif type == "Hightemp2":
			self.type = self.HIGHTEMP2
		elif type == "Picon2":
			self.type = self.PICON2
		elif type == "Skytext2":
			self.type = self.SKYTEXT2
		elif type == "Precip2":
			self.type = self.PRECIP2
#	day 3	#
		elif type == "Date3":
			self.type = self.DATE3
		elif type == "Shortdate3":
			self.type = self.SHORTDATE3
		elif type == "Day3":
			self.type = self.DAY3
		elif type == "Shortday3":
			self.type = self.SHORTDAY3
		elif type == "Temp3":
			self.type = self.TEMP3
		elif type == "Lowtemp3":
			self.type = self.LOWTEMP3
		elif type == "Hightemp3":
			self.type = self.HIGHTEMP3
		elif type == "Picorad":
			self.type = self.PICOrad
		elif type == "Skytext3":
			self.type = self.SKYTEXT3
		elif type == "Precip3":
			self.type = self.PRECIP3
#	day 4	#
		elif type == "Date4":
			self.type = self.DATE4
		elif type == "Shortdate4":
			self.type = self.SHORTDATE4
		elif type == "Day4":
			self.type = self.DAY4
		elif type == "Shortday4":
			self.type = self.SHORTDAY4
		elif type == "Temp4":
			self.type = self.TEMP4
		elif type == "Lowtemp4":
			self.type = self.LOWTEMP4
		elif type == "Hightemp4":
			self.type = self.HIGHTEMP4
		elif type == "Picon4":
			self.type = self.PICON4
		elif type == "Skytext4":
			self.type = self.SKYTEXT4
		elif type == "Precip4":
			self.type = self.PRECIP4

		self.iConsole = iConsole()
		self.poll_interval = time_update_ms
		self.poll_enabled = True

	def control_xml(self, result, retval, extra_args):
		if retval is not 0:
			self.write_none()

	def write_none(self):
		with open("/tmp/weathermsn2.xml", "w") as noneweather:
			noneweather.write("None")
		noneweather.close()

	def get_xmlfile(self):
		self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' -O /tmp/weathermsn2.xml" % (degreetype, weather_location, weather_city), self.control_xml)

	@cached
	def getText(self):
		year = float(strftime('%Y'))
		month = float(strftime('%m'))
		day = float(strftime('%d'))
		hour = float(strftime('%H'))
		min = float(strftime('%M'))
		sec = float(strftime('%S'))
		info, weze = 'n/a', ''
		msnweather = {'Vfd':'', 'Date':'', 'Shortdate':'', 'Day':'', 'Shortday':'',\
			'Location':'', 'Timezone':'', 'Latitude':'', 'Longitude':'',\
			'Julianday':'', 'Sunrise':'', 'Sunset':'', 'Solstice':'', 'Moonphase':'', 'Moonlight':'', 'PiconMoon':'99',\
			'Temp':'', 'Picon':'', 'Skytext':'', 'Feelslike':'', 'Humidity':'', 'Wind':'', 'Windspeed':'',\
			'Date0':'', 'Shortdate0':'', 'Day0':'', 'Shortday0':'', 'Temp0':'', 'Lowtemp0':'', 'Hightemp0':'', 'Picon0':'', 'Skytext0':'', 'Precip0':'',\
			'Date1':'', 'Shortdate1':'', 'Day1':'', 'Shortday1':'', 'Temp1':'', 'Lowtemp1':'', 'Hightemp1':'', 'Picon1':'', 'Skytext1':'', 'Precip1':'',\
			'Date2':'', 'Shortdate2':'', 'Day2':'', 'Shortday2':'', 'Temp2':'', 'Lowtemp2':'', 'Hightemp2':'', 'Picon2':'', 'Skytext2':'', 'Precip2':'',\
			'Date3':'', 'Shortdate3':'', 'Day3':'', 'Shortday3':'', 'Temp3':'', 'Lowtemp3':'', 'Hightemp3':'', 'Picorad':'', 'Skytext3':'', 'Precip3':'',\
			'Date4':'', 'Shortdate4':'', 'Day4':'', 'Shortday4':'', 'Temp4':'', 'Lowtemp4':'', 'Hightemp4':'', 'Picon4':'', 'Skytext4':'', 'Precip4':'',\
			}
		low0weather, hi0weather, low1weather, hi1weather, low2weather, hi2weather, low3weather, hi3weather, low4weather, hi4weather = '', '', '', '', '', '', '', '', '', ''
		timezone, latitude, longitude = '', '', ''
		if fileExists("/tmp/weathermsn2.xml"):
			if int((time.time() - os.stat("/tmp/weathermsn2.xml").st_mtime)/60) >= time_update:
				self.get_xmlfile()
		else:
			self.get_xmlfile()
		if not fileExists("/tmp/weathermsn2.xml"):
			self.write_none()
			return info
		if fileExists("/tmp/weathermsn2.xml") and open("/tmp/weathermsn2.xml").read() is 'None':
			return info
		for line in open("/tmp/weathermsn2.xml"):
			try:
				if "<weather" in line:
					msnweather['Location'] = line.split('weatherlocationname')[1].split('"')[1].split(',')[0]
					if not line.split('timezone')[1].split('"')[1][0] is '0':
						msnweather['Timezone'] = '+' + line.split('timezone')[1].split('"')[1] + ' h'
					else:
						msnweather['Timezone'] = line.split('timezone')[1].split('"')[1] + ' h'
					timezone = '%s' % (float(line.split('timezone')[1].split('"')[1]) - 1)
					msnweather['Latitude'] = line.split(' lat')[1].split('"')[1]
					msnweather['Longitude'] = line.split(' long')[1].split('"')[1]
					latitude = '%s' %  line.split(' lat')[1].split('"')[1].replace(',', '.')
					longitude = '%s' %  line.split(' long')[1].split('"')[1].replace(',', '.')
				if "<current" in line:
					if not line.split('temperature')[1].split('"')[1][0] is '-' and not line.split('temperature')[1].split('"')[1][0] is '0':
						msnweather['Temp'] = '+' + line.split('temperature')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					else:
						msnweather['Temp'] = line.split('temperature')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					if not line.split('feelslike')[1].split('"')[1][0] is '-' and not line.split('feelslike')[1].split('"')[1][0] is '0':
						msnweather['Feelslike'] = '+' + line.split('feelslike')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					else:
						msnweather['Feelslike'] = line.split('feelslike')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					msnweather['Picon'] = line.split('skycode')[1].split('"')[1]
					msnweather['Skytext'] = line.split('skytext')[1].split('"')[1]
					msnweather['Humidity'] = line.split('humidity')[1].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
					try:
						msnweather['Wind'] = line.split('winddisplay')[1].split('"')[1].split(' ')[2]
					except:
						pass
			# m/s
					if windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = '%s m/s' % line.split('windspeed')[1].split('"')[1].split(' ')[0]
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = '%.01f m/s' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.28)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = '%.01f m/s' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.45)
			# ft/s
					elif windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed']= '%.01f ft/s' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 3.28)
					elif windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed']= '%.01f ft/s' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.91)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = '%.01f ft/s' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.47)
			# mp/h
					elif windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = '%.01f mp/h' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 2.24)
					elif windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = '%.01f mp/h' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.62)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = '%s mp/h' % line.split('windspeed')[1].split('"')[1].split(' ')[0]
			# knots
					elif windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = '%.01f knots' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.94)
					elif windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = '%.01f knots' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.54)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = '%.01f knots' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.87)
			# km/h
					elif windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = '%.01f km/h' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 3.6)
					elif windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = '%s km/h' % line.split('windspeed')[1].split('"')[1].split(' ')[0]
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = '%.01f km/h' % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.61)
					msnweather['Date'] = line.split('date')[1].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[1].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[1].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate'] = line.split('shortday')[1].split('"')[1] + ' ' + line.split('date')[1].split('"')[1].split('-')[2].strip()
					msnweather['Day'] = line.split(' day')[1].split('"')[1]
					msnweather['Shortday'] = line.split('shortday')[1].split('"')[1]
#	today	#
				if "<forecast" in line:
					if not line.split('low')[1].split('"')[1][0] is '-' and not line.split('low')[1].split('"')[1][0] is '0':
						low0weather = '+' + line.split('low')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp0'] = '%s%s' % (low0weather, degreetype)
					else:
						low0weather = line.split('low')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp0'] = '%s%s' % (low0weather, degreetype)
					if not line.split('high')[1].split('"')[1][0] is '-' and not line.split('high')[1].split('"')[1][0] is '0':
						hi0weather = '+' + line.split('high')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp0'] = '%s%s' % (hi0weather, degreetype)
					else:
						hi0weather = line.split('high')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp0'] = '%s%s' % (hi0weather, degreetype)
					msnweather['Temp0'] = '%s / %s' % (hi0weather, low0weather)
					msnweather['Picon0'] = line.split('skycodeday')[1].split('"')[1]
					msnweather['Date0'] = line.split('date')[2].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate0'] = line.split('shortday')[2].split('"')[1] + ' ' + line.split('date')[2].split('"')[1].split('-')[2].strip()
					msnweather['Day0'] = line.split(' day')[2].split('"')[1]
					msnweather['Shortday0'] = line.split('shortday')[2].split('"')[1]
					msnweather['Skytext0'] = line.split('skytextday')[1].split('"')[1]
					msnweather['Precip0'] = line.split('precip')[1].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
#	day 1	#
				if "<forecast" in line:
					if not line.split('low')[2].split('"')[1][0] is '-' and not line.split('low')[2].split('"')[1][0] is '0':
						low1weather = '+' + line.split('low')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp1'] = '%s%s' % (low1weather, degreetype)
					else:
						low1weather = line.split('low')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp1'] = '%s%s' % (low1weather, degreetype)
					if not line.split('high')[2].split('"')[1][0] is '-' and not line.split('high')[2].split('"')[1][0] is '0':
						hi1weather = '+' + line.split('high')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp1'] = '%s%s' % (hi1weather, degreetype)
					else:
						hi1weather = line.split('high')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp1'] = '%s%s' % (hi1weather, degreetype)
					msnweather['Temp1'] = '%s / %s' % (hi1weather, low1weather)
					msnweather['Picon1'] = line.split('skycodeday')[2].split('"')[1]
					msnweather['Date1'] = line.split('date')[3].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate1'] = line.split('shortday')[3].split('"')[1] + ' ' + line.split('date')[3].split('"')[1].split('-')[2].strip()
					msnweather['Day1'] = line.split(' day')[3].split('"')[1]
					msnweather['Shortday1'] = line.split('shortday')[3].split('"')[1]
					msnweather['Skytext1'] = line.split('skytextday')[2].split('"')[1]
					msnweather['Precip1'] = line.split('precip')[2].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
#	day 2	#
				if "<forecast" in line:
					if not line.split('low')[3].split('"')[1][0] is '-' and not line.split('low')[3].split('"')[1][0] is '0':
						low2weather = '+' + line.split('low')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp2'] = '%s%s' % (low2weather, degreetype)
					else:
						low2weather = line.split('low')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp2'] = '%s%s' % (low2weather, degreetype)
					if not line.split('high')[3].split('"')[1][0] is '-' and not line.split('high')[3].split('"')[1][0] is '0':
						hi2weather = '+' + line.split('high')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp2'] = '%s%s' % (hi2weather, degreetype)
					else:
						hi2weather = line.split('high')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp2'] = '%s%s' % (hi2weather, degreetype)
					msnweather['Temp2'] = '%s / %s' % (hi2weather, low2weather)
					msnweather['Picon2'] = line.split('skycodeday')[3].split('"')[1]
					msnweather['Date2'] = line.split('date')[4].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate2'] = line.split('shortday')[4].split('"')[1] + ' ' + line.split('date')[4].split('"')[1].split('-')[2].strip()
					msnweather['Day2'] = line.split(' day')[4].split('"')[1]
					msnweather['Shortday2'] = line.split('shortday')[4].split('"')[1]
					msnweather['Skytext2'] = line.split('skytextday')[3].split('"')[1]
					msnweather['Precip2'] = line.split('precip')[3].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
#	day 3	#
				if "<forecast" in line:
					if not line.split('low')[4].split('"')[1][0] is '-' and not line.split('low')[4].split('"')[1][0] is '0':
						low3weather = '+' + line.split('low')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp3'] = '%s%s' % (low3weather, degreetype)
					else:
						low3weather = line.split('low')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp3'] = '%s%s' % (low3weather, degreetype)
					if not line.split('high')[4].split('"')[1][0] is '-' and not line.split('high')[4].split('"')[1][0] is '0':
						hi3weather = '+' + line.split('high')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp3'] = '%s%s' % (hi3weather, degreetype)
					else:
						hi3weather = line.split('high')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp3'] = '%s%s' % (hi3weather, degreetype)
					msnweather['Temp3'] = '%s / %s' % (hi3weather, low3weather)
					msnweather['Picorad'] = line.split('skycodeday')[4].split('"')[1]
					msnweather['Date3'] = line.split('date')[5].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate3'] = line.split('shortday')[5].split('"')[1] + ' ' + line.split('date')[5].split('"')[1].split('-')[2].strip()
					msnweather['Day3'] = line.split(' day')[5].split('"')[1]
					msnweather['Shortday3'] = line.split('shortday')[5].split('"')[1]
					msnweather['Skytext3'] = line.split('skytextday')[4].split('"')[1]
					msnweather['Precip3'] = line.split('precip')[4].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
#	day 4	#
				if "<forecast" in line:
					if not line.split('low')[5].split('"')[1][0] is '-' and not line.split('low')[5].split('"')[1][0] is '0':
						low4weather = '+' + line.split('low')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp4'] = '%s%s' % (low4weather, degreetype)
					else:
						low4weather = line.split('low')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Lowtemp4'] = '%s%s' % (low4weather, degreetype)
					if not line.split('high')[5].split('"')[1][0] is '-' and not line.split('high')[5].split('"')[1][0] is '0':
						hi4weather = '+' + line.split('high')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp4'] = '%s%s' % (hi4weather, degreetype)
					else:
						hi4weather = line.split('high')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						msnweather['Hightemp4'] = '%s%s' % (hi4weather, degreetype)
					msnweather['Temp4'] = '%s / %s' % (hi4weather, low4weather)
					msnweather['Picon4'] = line.split('skycodeday')[5].split('"')[1]
					msnweather['Date4'] = line.split('date')[6].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate4'] = line.split('shortday')[6].split('"')[1] + ' ' + line.split('date')[6].split('"')[1].split('-')[2].strip()
					msnweather['Day4'] = line.split(' day')[6].split('"')[1]
					msnweather['Shortday4'] = line.split('shortday')[6].split('"')[1]
					msnweather['Skytext4'] = line.split('skytextday')[5].split('"')[1]
					msnweather['Precip4'] = line.split('precip')[5].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
			except:
				pass
#
		pi = 3.1415926535
		rad = pi / 180
		try:
			long = float(longitude)
			lat = float(latitude)
			zone = float(timezone)
		except:
			long = lat = zone = 0
#	julian day
		A = (14 - month)/12
		M = month + 12 * A - 3
		Y = year + 4800 - A
		jday = day + int((153 * M + 2) / 5) + int(365 * Y) + int(Y / 4) - int(Y / 100) + int(Y / 400) - 32045.6 + hour / 24 + min / 1440 + sec / 86400
		msnweather['Julianday'] = '%s' % jday
#	sun
		if month <= 2:
			M = month + 12
			Y = year - 1
		else:
			M = month
			Y = year
		L1 = int(year / 100)
		L2 = int(365.25 * (Y + 4716)) + int(30.6001 * (M + 1)) + day + (2 - L1 + int(L1 / 4)) - 1524.5
		T = (L2 - 2451545) / 36525
		K1 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
		K2 = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
		N1 = K2 / 360
		O1 = (N1 - int(N1)) * 360
		K3 = (1.914602 - 0.004817 * T - 1.4e-05 * T * T) * math.sin(O1 * rad)
		K4 = (0.019993 - 0.000101 * T) * math.sin(2 * O1 * rad)
		K5 = 0.000289 * math.sin(3 * O1 * rad)
		N2 = K1 / 360
		O2 = (N2 - int(N2)) * 360
		N3 = 125.04 - 1934.136 * T
		if N3 < 0:
			N4 = N3 + 360
		else:
			N4 = N3
		N5 = O2 + K3 + K4 + K5 - 0.00569 - 0.00478 * math.sin(N4 * rad)
		K6 = 23.43930278 - 0.0130042 * T - 1.63e-07 * T * T
		N6 = math.sin(K6 * rad) * math.sin(N5 * rad)
		N7 = math.asin(N6) * 180 / pi
		K7 = (7.7 * math.sin((O2 + 78) * rad) - 9.5 * math.sin(2 * O2 * rad)) / 60
		O3 = math.cos(N7 * rad) * math.cos(lat * rad)
		N8 = -0.01483 - math.sin(N7 * rad) * math.sin(lat * rad)
		SRh = int((13 - long / 15 + K7 - (2 * (math.acos(N8 / O3) * 57.29577951) / 15) / 2) + zone)
		SRm = int(round(((13 - long / 15 + K7 - (2 * (math.acos(N8 / O3) * 57.29577951) / 15) / 2) + zone - SRh) * 60))
		SSh = int((13 - long / 15 + K7 + (2 * (math.acos(N8 / O3) * 57.29577951) / 15) / 2) + zone)
		SSm = int(round(((13 - long / 15 + K7 + (2 * (math.acos(N8 / O3) * 57.29577951) / 15) / 2) + zone - SSh) * 60))
		Sh = int((13 - long / 15 + K7) + zone)
		Sm = int(round(((13 - long / 15 + K7) + zone - Sh) * 60))
		if SRm == 60:
			SRm = 0
			SRh = SRh + 1
		if SRm < 10:
			SR = '0'
		else:
			SR = ''
		if SSm == 60:
			SSm = 0
			SSh = SSh + 1
		if SSm < 10:
			SS = '0'
		else:
			SS = ''
		if Sm == 60:
			Sm = 0
			Sh = Sh + 1
		if Sm < 10:
			S = '0'
		else:
			S = ''
		try:
			msnweather['Sunrise'] = '%s%s%s%s' % (SRh, unichr(58).encode("latin-1"), SR, SRm)
			msnweather['Sunset'] = '%s%s%s%s' % (SSh, unichr(58).encode("latin-1"), SS, SSm)
			msnweather['Solstice'] = '%s%s%s%s' % (Sh, unichr(58).encode("latin-1"), S, Sm)
		except:
			msnweather['Sunrise'] = msnweather['Sunset'] = msnweather['Solstice'] = 'n/a'
#	moon
		T = (jday - 2451545) / 36525
		K1 = 297.8502042 + 445267.1115168 * T - 0.00163 * T * T + T * T * T / 545868 - T * T * T * T / 113065000
		K2 = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000
		K3 = 134.9634114 + 477198.8676313 * T - 0.008997 * T * T + T * T * T / 69699 - T * T * T * T / 14712000
		K4 = 180 - K1 - 6.289 * math.sin(rad * K3) + 2.1 * math.sin(rad * K2) - 1.274 * math.sin(rad * (2 * K1 - K3)) - 0.658 * math.sin(rad * (2 * K1)) - 0.214 * math.sin(rad * (2 * K3)) - 0.11 * math.sin(rad * K1)
		pha1 = (1 + math.cos(rad * K4)) / 2
		T = (jday + 0.5 / 24 - 2451545) / 36525
		K1 = 297.8502042 + 445267.1115168 * T - 0.00163 * T * T + T * T * T / 545868 - T * T * T * T / 113065000
		K2 = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000
		K3 = 134.9634114 + 477198.8676313 * T - 0.008997 * T * T + T * T * T / 69699 - T * T * T * T / 14712000
		K4 = 180 - K1 - 6.289 * math.sin(rad * K3) + 2.1 * math.sin(rad * K2) - 1.274 * math.sin(rad * (2 * K1 - K3)) - 0.658 * math.sin(rad * (2 * K1)) - 0.214 * math.sin(rad * (2 * K3)) - 0.11 * math.sin(rad * K1)
		pha2 = (1 + math.cos(rad * K4)) / 2
		if pha2 - pha1 < 0:
			trend = -1
		else:
			trend = 1
		light = 100 * pha1
		light = round(light, 1)
		if light > 0 and light < 5:
			pic = '5'
			phase = _('New moon')
			if trend == -1:
				pic = '05'
				phase = _('New moon')
		elif light > 5 and light < 10:
			pic = '10'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '010'
				phase = _('Waning crescent')
		elif light > 10 and light < 15:
			pic = '15'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '015'
				phase = _('Waning crescent')
		elif light > 15 and light < 20:
			pic = '20'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '020'
				phase = _('Waning crescent')
		elif light > 20 and light < 25:
			pic = '25'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '025'
				phase = _('Waning crescent')
		elif light > 25 and light < 30:
			pic = '30'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '030'
				phase = _('Waning crescent')
		elif light > 30 and light < 35:
			pic = '35'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '035'
				phase = _('Waning crescent')
		elif light > 35 and light < 40:
			pic = '40'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '040'
				phase = _('Waning crescent')
		elif light > 40 and light < 45:
			pic = '45'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '045'
				phase = _('Waning crescent')
		elif light > 45 and light < 50:
			pic = '50'
			phase = _('First quarter')
			if trend == -1:
				pic = '050'
				phase = _('Last quarter')
		elif light > 50 and light < 55:
			pic = '55'
			phase = _('First quarter')
			if trend == -1:
				pic = '055'
				phase = _('Last quarter')
		elif light > 55 and light < 60:
			pic = '60'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '060'
				phase = _('Waning gibbous')
		elif light > 60 and light < 65:
			pic = '65'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '065'
				phase = _('Waning gibbous')
		elif light > 65 and light < 70:
			pic = '70'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '070'
				phase = _('Waning gibbous')
		elif light > 70 and light < 75:
			pic = '75'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '075'
				phase = _('Waning gibbous')
		elif light > 75 and light < 80:
			pic = '80'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '080'
				phase = _('Waning gibbous')
		elif light > 80 and light < 85:
			pic = '85'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '085'
				phase = _('Waning gibbous')
		elif light > 85 and light < 90:
			pic = '90'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '090'
				phase = _('Waning gibbous')
		elif light > 90 and light < 95:
			pic = '95'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '095'
				phase = _('Waning gibbous')
		elif light > 95 and light < 100:
			pic = '100'
			phase = _('Full moon')
			if trend == -1:
				pic = '100'
				phase = _('Full moon')
		else:
			msnweather['Moonphase'] = 'n/a'
			msnweather['PiconMoon'] = '99'
		try:
			msnweather['Moonphase'] = '%s' % phase
			msnweather['Moonlight'] = '%s %s' % (light, unichr(37).encode("latin-1"))
			msnweather['PiconMoon'] = '%s' % pic
		except:
			msnweather['Moonphase'] = msnweather['Moonlight'] = 'n/a'
			msnweather['PiconMoon'] = '99'
#
		if self.type is self.VFD:
			try:
				weze = msnweather['Skytext'].split(' ')[1]
			except:
				weze = msnweather['Skytext']
			info = msnweather['Temp'] + ' ' + weze
		if self.type is self.DATE:
			info = msnweather['Date']
		if self.type is self.SHORTDATE:
			info = msnweather['Shortdate']
		if self.type is self.DAY:
			info = msnweather['Day']
		if self.type is self.JDAY:
			info = msnweather['Julianday']
		if self.type is self.SHORTDAY:
			info = msnweather['Shortday']
		if self.type is self.LOCATION:
			info = msnweather['Location']
		if self.type is self.TIMEZONE:
			info = msnweather['Timezone']
		if self.type is self.LATITUDE:
			info = msnweather['Latitude']
		if self.type is self.LONGITUDE:
			info = msnweather['Longitude']
		if self.type is self.SUNRISE:
			info = msnweather['Sunrise']
		if self.type is self.SUNSET:
			info = msnweather['Sunset']
		if self.type is self.SOLSTICE:
			info = msnweather['Solstice']
		if self.type is self.MOONPHASE:
			info = msnweather['Moonphase']
		if self.type is self.MOONLIGHT:
			info = msnweather['Moonlight']
		if self.type is self.MOONPICON:
			info = msnweather['PiconMoon']
		if self.type is self.TEMP:
			info = msnweather['Temp']
		if self.type is self.PICON:
			info = msnweather['Picon']
		if self.type is self.SKYTEXT:
			info = msnweather['Skytext']
		if self.type is self.FEELSLIKE:
			info = msnweather['Feelslike']
		if self.type is self.HUMIDITY:
			info = msnweather['Humidity']
		if self.type is self.WIND:
			info = msnweather['Wind']
		if self.type is self.WINDSPEED:
			info = msnweather['Windspeed']
#	today	#
		if self.type is self.DATE0:
			info = msnweather['Date0']
		if self.type is self.SHORTDATE0:
			info = msnweather['Shortdate0']
		if self.type is self.DAY0:
			info = msnweather['Day0']
		if self.type is self.SHORTDAY0:
			info = msnweather['Shortday0']
		if self.type is self.TEMP0:
			info = msnweather['Temp0']
		if self.type is self.LOWTEMP0:
			info = msnweather['Lowtemp0']
		if self.type is self.HIGHTEMP0:
			info = msnweather['Hightemp0']
		if self.type is self.PICON0:
			info = msnweather['Picon0']
		if self.type is self.SKYTEXT0:
			info = msnweather['Skytext0']
		if self.type is self.PRECIP0:
			info = msnweather['Precip0']
#	day 1	#
		if self.type is self.DATE1:
			info = msnweather['Date1']
		if self.type is self.SHORTDATE1:
			info = msnweather['Shortdate1']
		if self.type is self.DAY1:
			info = msnweather['Day1']
		if self.type is self.SHORTDAY1:
			info = msnweather['Shortday1']
		if self.type is self.TEMP1:
			info = msnweather['Temp1']
		if self.type is self.LOWTEMP1:
			info = msnweather['Lowtemp1']
		if self.type is self.HIGHTEMP1:
			info = msnweather['Hightemp1']
		if self.type is self.PICON1:
			info = msnweather['Picon1']
		if self.type is self.SKYTEXT1:
			info = msnweather['Skytext1']
		if self.type is self.PRECIP1:
			info = msnweather['Precip1']
#	day 2	#
		if self.type is self.DATE2:
			info = msnweather['Date2']
		if self.type is self.SHORTDATE2:
			info = msnweather['Shortdate2']
		if self.type is self.DAY2:
			info = msnweather['Day2']
		if self.type is self.SHORTDAY2:
			info = msnweather['Shortday2']
		if self.type is self.TEMP2:
			info = msnweather['Temp2']
		if self.type is self.LOWTEMP2:
			info = msnweather['Lowtemp2']
		if self.type is self.HIGHTEMP2:
			info = msnweather['Hightemp2']
		if self.type is self.PICON2:
			info = msnweather['Picon2']
		if self.type is self.SKYTEXT2:
			info = msnweather['Skytext2']
		if self.type is self.PRECIP2:
			info = msnweather['Precip2']
#	day 3	#
		if self.type is self.DATE3:
			info = msnweather['Date3']
		if self.type is self.SHORTDATE3:
			info = msnweather['Shortdate3']
		if self.type is self.DAY3:
			info = msnweather['Day3']
		if self.type is self.SHORTDAY3:
			info = msnweather['Shortday3']
		if self.type is self.TEMP3:
			info = msnweather['Temp3']
		if self.type is self.LOWTEMP3:
			info = msnweather['Lowtemp3']
		if self.type is self.HIGHTEMP3:
			info = msnweather['Hightemp3']
		if self.type is self.PICOrad:
			info = msnweather['Picorad']
		if self.type is self.SKYTEXT3:
			info = msnweather['Skytext3']
		if self.type is self.PRECIP3:
			info = msnweather['Precip3']
#	day 4	#
		if self.type is self.DATE4:
			info = msnweather['Date4']
		if self.type is self.SHORTDATE4:
			info = msnweather['Shortdate4']
		if self.type is self.DAY4:
			info = msnweather['Day4']
		if self.type is self.SHORTDAY4:
			info = msnweather['Shortday4']
		if self.type is self.TEMP4:
			info = msnweather['Temp4']
		if self.type is self.LOWTEMP4:
			info = msnweather['Lowtemp4']
		if self.type is self.HIGHTEMP4:
			info = msnweather['Hightemp4']
		if self.type is self.PICON4:
			info = msnweather['Picon4']
		if self.type is self.SKYTEXT4:
			info = msnweather['Skytext4']
		if self.type is self.PRECIP4:
			info = msnweather['Precip4']
		return info
	text = property(getText)

	def changed(self, what):
		Converter.changed(self, (self.CHANGED_POLL,))
