# -*- coding: UTF-8 -*-
#
# Converter - MSNWeather
# Developer - Sirius
# Version 1.1
# Homepage - http://www.gisclub.tv
#
# Jean Meeus - Astronomical Algorithms
# David Vallado - Fundamentals of Astrodynamics and Applications
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

time_update = 30
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
	MOONRISE = 14
	MOONSET = 15
	MOONDIST = 16
	MOONPHASE = 17
	MOONLIGHT = 18
	MOONPICON = 19
	TEMP = 20
	PICON = 21
	SKYTEXT = 22
	FEELSLIKE = 23
	HUMIDITY = 24
	WIND = 25
	WINDSPEED = 26
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
	PICON3 = 67
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
		elif type == "Moonrise":
			self.type = self.MOONRISE
		elif type == "Moonset":
			self.type = self.MOONSET
		elif type == "Moondist":
			self.type = self.MOONDIST
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
# День 0
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
# День 1
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
# День 2
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
# День 3
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
		elif type == "Picon3":
			self.type = self.PICON3
		elif type == "Skytext3":
			self.type = self.SKYTEXT3
		elif type == "Precip3":
			self.type = self.PRECIP3
# День 4
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
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/plugin.pyo"):
			self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' -O /tmp/weathermsn2.xml" % (degreetype, weather_location, weather_city), self.control_xml)
		else:
			pass

	@cached
	def getText(self):
		year = float(strftime('%Y'))
		month = float(strftime('%m'))
		day = float(strftime('%d'))
		hour = float(strftime('%H'))
		min = float(strftime('%M'))
		sec = float(strftime('%S'))
		info, weze = 'n/a', ''
		msnweather = {'Vfd':'', 'Date':'', 'Shortdate':'', 'Day':'', 'Shortday':'','Location':'', 'Timezone':'', 'Latitude':'', 'Longitude':'',\
			'Julianday':'', 'Sunrise':'', 'Sunset':'', 'Solstice':'', 'Moonrise':'', 'Moonset':'', 'Moondist':'', 'Moonphase':'', 'Moonlight':'', 'PiconMoon':'99',\
			'Temp':'', 'Picon':'', 'Skytext':'', 'Feelslike':'', 'Humidity':'', 'Wind':'', 'Windspeed':'',\
			'Date0':'', 'Shortdate0':'', 'Day0':'', 'Shortday0':'', 'Temp0':'', 'Lowtemp0':'', 'Hightemp0':'', 'Picon0':'', 'Skytext0':'', 'Precip0':'',\
			'Date1':'', 'Shortdate1':'', 'Day1':'', 'Shortday1':'', 'Temp1':'', 'Lowtemp1':'', 'Hightemp1':'', 'Picon1':'', 'Skytext1':'', 'Precip1':'',\
			'Date2':'', 'Shortdate2':'', 'Day2':'', 'Shortday2':'', 'Temp2':'', 'Lowtemp2':'', 'Hightemp2':'', 'Picon2':'', 'Skytext2':'', 'Precip2':'',\
			'Date3':'', 'Shortdate3':'', 'Day3':'', 'Shortday3':'', 'Temp3':'', 'Lowtemp3':'', 'Hightemp3':'', 'Picon3':'', 'Skytext3':'', 'Precip3':'',\
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
						msnweather['Windspeed'] = _('%s m/s') % line.split('windspeed')[1].split('"')[1].split(' ')[0]
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = _('%.01f m/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.28)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = _('%.01f m/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.45)
# ft/s
					elif windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed']= _('%.01f ft/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 3.28)
					elif windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed']= _('%.01f ft/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.91)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = _('%.01f ft/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.47)
# mp/h
					elif windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = _('%.01f mp/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 2.24)
					elif windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = _('%.01f mp/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.62)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = _('%s mp/h') % line.split('windspeed')[1].split('"')[1].split(' ')[0]
# knots
					elif windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = _('%.01f knots') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.94)
					elif windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = _('%.01f knots') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.54)
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = _('%.01f knots') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.87)
# km/h
					elif windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						msnweather['Windspeed'] = _('%.01f km/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 3.6)
					elif windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						msnweather['Windspeed'] = _('%s km/h') % line.split('windspeed')[1].split('"')[1].split(' ')[0]
					elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						msnweather['Windspeed'] = _('%.01f km/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.61)
					msnweather['Date'] = line.split('date')[1].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[1].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[1].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate'] = line.split('shortday')[1].split('"')[1] + ' ' + line.split('date')[1].split('"')[1].split('-')[2].strip()
					msnweather['Day'] = line.split(' day')[1].split('"')[1]
					msnweather['Shortday'] = line.split('shortday')[1].split('"')[1]
# День 0
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
# День 1
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
# День 2
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
# День 3
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
					msnweather['Picon3'] = line.split('skycodeday')[4].split('"')[1]
					msnweather['Date3'] = line.split('date')[5].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[0].strip()
					msnweather['Shortdate3'] = line.split('shortday')[5].split('"')[1] + ' ' + line.split('date')[5].split('"')[1].split('-')[2].strip()
					msnweather['Day3'] = line.split(' day')[5].split('"')[1]
					msnweather['Shortday3'] = line.split('shortday')[5].split('"')[1]
					msnweather['Skytext3'] = line.split('skytextday')[4].split('"')[1]
					msnweather['Precip3'] = line.split('precip')[4].split('"')[1] + ' %s' % unichr(37).encode("latin-1")
# День 4
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
		PI = 3.14159265359
		DEG2RAD = PI / 180
		RAD2DEG = 180 / PI
		try:
			long = float(longitude)
			lat = float(latitude)
			zone = float(timezone)
		except:
			long = lat = zone = 0
		UT = hour - zone + min / 60 + sec / 3600 - 13
# Юлианская дата
		A = (14 - month) / 12
		M = month + 12 * A - 3
		Y = year + 4800 - A
		JDN = day + int((153 * M + 2) / 5) + int(365 * Y) + int(Y / 4) - int(Y / 100) + int(Y / 400) - 32045
		JD = JDN + UT / 24
# Орбита Земли
		T = (JD - 2451545) / 36525
		LS = 280.46646 + 36000.76983 * T + 0.0003032 * T * T # ср долгота солнца
		MS = 357.52911 + 35999.05029 * T - 0.0001537 * T * T # ср аномалия солнца
		CS = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(MS * DEG2RAD) + (0.019993 - 0.000101 * T) * math.sin(2 * MS * DEG2RAD) + 0.000289 * math.sin(3 * MS * DEG2RAD) # уравнение центра солнца

		LAMBDA = 125.04 - 1934.136 * T
		if LAMBDA < 0:
			LAMBDA = LAMBDA + 360

		SLong = LS + CS - 0.00569 - 0.00478 * math.sin(LAMBDA * DEG2RAD) # истинная долгота солнца
		OES = 23.439291 - 0.0130042 * T # наклон эклиптики земли
		DEC = math.asin(math.sin(OES * DEG2RAD) * math.sin(SLong * DEG2RAD)) * RAD2DEG # склонение солнца
		ALFA = (7.7 * math.sin((LS + 78) * DEG2RAD) - 9.5 * math.sin(2 * LS * DEG2RAD)) / 60
		BETA = math.acos((-0.014485 - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG

		SSS = ALFA + zone + (195 - long) / 15
# Время восхода/захода
		SCh = int(SSS)
		SCm = int(round((SSS - SCh) * 60))
		SRh = int(SSS - BETA / 15)
		SRm = int(round(((SSS - BETA / 15) - SRh) * 60))
		SSh = int(SSS + BETA / 15)
		SSm = int(round(((SSS + BETA / 15) - SSh) * 60))
		if SCm == 60:
			SCm = 0
			SCh = SCh + 1
		if SCm < 10:
			SC = '0'
		else:
			SC = ''
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
		try:
			msnweather['Julianday'] = '%s' % JD
			msnweather['Sunrise'] = '%s%s%s%s' % (SRh, unichr(58).encode("latin-1"), SR, SRm)
			msnweather['Sunset'] = '%s%s%s%s' % (SSh, unichr(58).encode("latin-1"), SS, SSm)
			msnweather['Solstice'] = '%s%s%s%s' % (SCh, unichr(58).encode("latin-1"), SC, SCm)
		except:
			msnweather['Julianday'] = msnweather['Sunrise'] = msnweather['Sunset'] = msnweather['Solstice'] = 'n/a'
# Орбита Луны
		T = (JD - 2451545) / 36525
		LM = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T * T * T / 538841 - T * T * T * T / 65194000 # ср долгота луны
		FM = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T - T * T * T / 3526000 + T * T * T * T / 863310000 # ср растояние луны
		DM = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср удлинение луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		IM = 180 - DM - 6.289 * math.sin(MM * DEG2RAD) + 2.100 * math.sin(MS * DEG2RAD) - 1.274 * math.sin((2 * DM - MM) * DEG2RAD) - 0.658 * math.sin(2 * DM * DEG2RAD) - 0.214 * math.sin(2 * MM * DEG2RAD) - 0.114 * math.sin(DM * DEG2RAD)
		pha1 = (1 + math.cos(IM * DEG2RAD)) / 2

		ER = 1 + 0.0545 * math.cos(MM * DEG2RAD) + 0.0100 * math.cos((2 * DM - MM) * DEG2RAD) + 0.0082 * math.cos(2 * DM * DEG2RAD) + 0.0030 * math.cos(2 * MM * DEG2RAD) + 0.0009 * math.cos((2 * DM + MM) * DEG2RAD) + 0.0006 * math.cos((2 * DM - MS) * DEG2RAD) + 0.0004 * math.cos((2 * DM - MS - MM) * DEG2RAD) - 0.0003 * math.cos((MS - MM) * DEG2RAD)
		EL = 6.289 * math.sin(MM * DEG2RAD) + 1.274 * math.sin((2 * DM - MM) * DEG2RAD) + 0.658 * math.sin(2 * DM * DEG2RAD) + 0.214 * math.sin(2 * MM * DEG2RAD) - 0.186 * math.sin(MS * DEG2RAD) - 0.114 * math.sin(2 * FM * DEG2RAD) + 0.059 * math.sin((2 * DM - 2 * MM) * DEG2RAD) + 0.057 * math.sin((2 * DM - MS - MM) * DEG2RAD) + 0.053 * math.sin((2 * DM + MM) * DEG2RAD) + 0.046 * math.sin((2 * DM - MS) * DEG2RAD) - 0.041 * math.sin((MS - MM) * DEG2RAD) - 0.035 * math.sin(DM * DEG2RAD) - 0.030 * math.sin((MS + MM) * DEG2RAD)
		EB = 5.128 * math.sin(FM * DEG2RAD) + 0.281 * math.sin((MM + FM) * DEG2RAD) + 0.278 * math.sin((MM - FM) * DEG2RAD) + 0.173 * math.sin((2 * DM - FM) * DEG2RAD) + 0.055 * math.sin((2 * DM - MM + FM) * DEG2RAD) + 0.046 * math.sin((2 * DM - MM - FM) * DEG2RAD) + 0.033 * math.sin((2 * DM + FM) * DEG2RAD) + 0.017 * math.sin((2 * MM + FM) * DEG2RAD) + 0.009 * math.sin((2 * DM + MM - FM) * DEG2RAD) + 0.009 * math.sin((2 * MM - FM) * DEG2RAD)

		T = (JD + 0.5 / 24 - 2451545) / 36525
		DM = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср удлинение луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		IM = 180 - DM - 6.289 * math.sin(MM * DEG2RAD) + 2.100 * math.sin(MS * DEG2RAD) - 1.274 * math.sin((2 * DM - MM) * DEG2RAD) - 0.658 * math.sin(2 * DM * DEG2RAD) - 0.214 * math.sin(2 * MM * DEG2RAD) - 0.114 * math.sin(DM * DEG2RAD)
		pha2 = (1 + math.cos(IM * DEG2RAD)) / 2

		if pha2 - pha1 < 0:
			trend = -1
		else:
			trend = 1

		LAMBDA = 125.04452 - 1934.13261 * T + 0.00220708 * T * T
		if LAMBDA < 0:
			LAMBDA = LAMBDA + 360

		EPS1 = 23.439291 - 0.0130042 * T - 0.000000164 * T * T + 0.000000504 * T * T * T
		EPS2 = 0.002555 * math.cos(LAMBDA) + 0.000158 * math.cos(2 * LS) + 0.000028 * math.cos(2 * LM) - 0.000025 * math.cos(2 * LAMBDA)
		OEM = EPS1 + EPS2 # наклон эклиптики луны
		Mdist = int(384404 / ER) # расстояние до луны км
		MLat = EB # - широта луны
		MLong = LM + EL # - долгота луны
		RA = math.atan2((math.sin(MLong * DEG2RAD) * math.cos(OEM * DEG2RAD) - math.tan(MLat * DEG2RAD) * math.sin(OEM * DEG2RAD)) , math.cos(MLong * DEG2RAD)) * RAD2DEG # прямое восхождение луны
		DEC = math.asin(math.sin(MLat * DEG2RAD) * math.cos(OEM * DEG2RAD) + math.cos(MLat * DEG2RAD) * math.sin(OEM * DEG2RAD) * math.sin(MLong * DEG2RAD)) * RAD2DEG # склонение луны
		BETA = math.acos((0.002094 - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG

		SMR = RA - BETA + 180 + long
		if SMR < 0:
			SMR = SMR + 360
		elif SMR >= 360:
			SMR = SMR - 360
		SMS = RA + BETA + 180 + long
		if SMS < 0:
			SMS = SMS + 360
		elif SMS >= 360:
			SMS = SMS - 360
# Время восхода/захода
		MRh = int(SMR / 15)
		MRm = int(round(((SMR / 15) - MRh) * 60))
		MSh = int(SMS / 15)
		MSm = int(round(((SMS / 15) - MSh) * 60))
		if MRm == 60:
			MRm = 0
			MRh = MRh + 1
		if MRm < 10:
			MR = '0'
		else:
			MR = ''
		if MSm == 60:
			MSm = 0
			MSh = MSh + 1
		if MSm < 10:
			MS = '0'
		else:
			MS = ''
# Фазы Луны
		light = 100 * pha1
		light = round(light, 1)
		if light >= 0 and light < 5:
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
		elif light > 95 and light <= 100:
			pic = '100'
			phase = _('Full moon')
			if trend == -1:
				pic = '100'
				phase = _('Full moon')
		try:
			msnweather['Moondist'] = _('%s km') % Mdist
			msnweather['Moonrise'] = '%s%s%s%s' % (MRh, unichr(58).encode("latin-1"), MR, MRm)
			msnweather['Moonset'] = '%s%s%s%s' % (MSh, unichr(58).encode("latin-1"), MS, MSm)
			msnweather['Moonphase'] = '%s' % phase
			msnweather['Moonlight'] = '%s %s' % (light, unichr(37).encode("latin-1"))
			msnweather['PiconMoon'] = '%s' % pic
		except:
			msnweather['Moondist'] = msnweather['Moonrise'] = msnweather['Moonset'] = msnweather['Moonphase'] = msnweather['Moonlight'] = 'n/a'
			msnweather['PiconMoon'] = '1'
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
		if self.type is self.MOONRISE:
			info = msnweather['Moonrise']
		if self.type is self.MOONSET:
			info = msnweather['Moonset']
		if self.type is self.MOONDIST:
			info = msnweather['Moondist']
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
# День 0
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
# День 1
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
# День 2
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
# День 3
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
		if self.type is self.PICON3:
			info = msnweather['Picon3']
		if self.type is self.SKYTEXT3:
			info = msnweather['Skytext3']
		if self.type is self.PRECIP3:
			info = msnweather['Precip3']
# День 4
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
