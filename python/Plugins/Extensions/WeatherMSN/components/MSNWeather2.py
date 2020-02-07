# -*- coding: UTF-8 -*-
#
# Converter - MSNWeatherAstro
# Developer - Sirius
# Version 1.2
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
	SUNCULMINATION = 13
	MERCURYRISE = 14
	MERCURYSET = 15
	MERCURYAZIMUTH = 16
	VENUSRISE = 17
	VENUSSET = 18
	VENUSAZIMUTH = 19
	MARSRISE = 20
	MARSSET = 21
	MARSAZIMUTH = 22
	JUPITERRISE = 23
	JUPITERSET = 24
	JUPITERAZIMUTH = 25
	SATURNRISE = 26
	SATURNSET = 27
	SATURNAZIMUTH = 28
	URANUSRISE = 29
	URANUSSET = 30
	URANUSAZIMUTH = 31
	NEPTUNERISE = 32
	NEPTUNESET = 33
	NEPTUNEAZIMUTH = 34
	MOONRISE = 35
	MOONSET = 36
	MOONDIST = 37
	MOONAZIMUTH = 38
	MOONPHASE = 39
	MOONLIGHT = 40
	MOONPICON = 41
	TEMP = 50
	PICON = 51
	SKYTEXT = 52
	FEELSLIKE = 53
	HUMIDITY = 54
	WIND = 55
	WINDSPEED = 56
	DATE0 = 60
	SHORTDATE0 = 61
	DAY0 = 62
	SHORTDAY0 = 63
	TEMP0 = 64
	LOWTEMP0 = 65
	HIGHTEMP0 = 66
	PICON0 = 67
	SKYTEXT0 = 68
	PRECIP0 = 69
	DATE1 = 70
	SHORTDATE1 = 71
	DAY1 = 72
	SHORTDAY1 = 73
	TEMP1 = 74
	LOWTEMP1 = 75
	HIGHTEMP1 = 76
	PICON1 = 77
	SKYTEXT1 = 78
	PRECIP1 = 79
	DATE2 = 80
	SHORTDATE2 = 81
	DAY2 = 82
	SHORTDAY2 = 83
	TEMP2 = 84
	LOWTEMP2 = 85
	HIGHTEMP2 = 86
	PICON2 = 87
	SKYTEXT2 = 88
	PRECIP2 = 89
	DATE3 = 90
	SHORTDATE3 = 91
	DAY3 = 92
	SHORTDAY3 = 93
	TEMP3 = 94
	LOWTEMP3 = 95
	HIGHTEMP3 = 96
	PICON3 = 97
	SKYTEXT3 = 98
	PRECIP3 = 99
	DATE4 = 100
	SHORTDATE4 = 101
	DAY4 = 102
	SHORTDAY4 = 103
	TEMP4 = 104
	LOWTEMP4 = 105
	HIGHTEMP4 = 106
	PICON4 = 107
	SKYTEXT4 = 108
	PRECIP4 = 109

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
# Астро
		elif type == "Sunrise":
			self.type = self.SUNRISE
		elif type == "Sunset":
			self.type = self.SUNSET
		elif type == "Solstice":
			self.type = self.SUNCULMINATION
		elif type == "Mercuryrise":
			self.type = self.MERCURYRISE
		elif type == "Mercuryset":
			self.type = self.MERCURYSET
		elif type == "Mercuryazimuth":
			self.type = self.MERCURYAZIMUTH
		elif type == "Venusrise":
			self.type = self.VENUSRISE
		elif type == "Venusset":
			self.type = self.VENUSSET
		elif type == "Venusazimuth":
			self.type = self.VENUSAZIMUTH
		elif type == "Marsrise":
			self.type = self.MARSRISE
		elif type == "Marsset":
			self.type = self.MARSSET
		elif type == "Marsazimuth":
			self.type = self.MARSAZIMUTH
		elif type == "Jupiterrise":
			self.type = self.JUPITERRISE
		elif type == "Jupiterset":
			self.type = self.JUPITERSET
		elif type == "Jupiterazimuth":
			self.type = self.JUPITERAZIMUTH
		elif type == "Saturnrise":
			self.type = self.SATURNRISE
		elif type == "Saturnset":
			self.type = self.SATURNSET
		elif type == "Saturnazimuth":
			self.type = self.SATURNAZIMUTH
		elif type == "Uranusrise":
			self.type = self.URANUSRISE
		elif type == "Uranusset":
			self.type = self.URANUSSET
		elif type == "Uranusazimuth":
			self.type = self.URANUSAZIMUTH
		elif type == "Neptunerise":
			self.type = self.NEPTUNERISE
		elif type == "Neptuneset":
			self.type = self.NEPTUNESET
		elif type == "Neptuneazimuth":
			self.type = self.NEPTUNEAZIMUTH
		elif type == "Moonrise":
			self.type = self.MOONRISE
		elif type == "Moonset":
			self.type = self.MOONSET
		elif type == "Moondist":
			self.type = self.MOONDIST
		elif type == "Moonazimuth":
			self.type = self.MOONAZIMUTH
		elif type == "Moonphase":
			self.type = self.MOONPHASE
		elif type == "Moonlight":
			self.type = self.MOONLIGHT
		elif type == "PiconMoon":
			self.type = self.MOONPICON
# Сейчас
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
		msnweather = {'Vfd':'',\
			'Date':'',\
			'Shortdate':'',\
			'Day':'',\
			'Shortday':'',\
			'Location':'',\
			'Timezone':'',\
			'Latitude':'',\
			'Longitude':'',\
			'Julianday':'',\
			'Sunrise':'',\
			'Sunset':'',\
			'Solstice':'',\
			'Mercuryrise':'',\
			'Mercuryset':'',\
			'Mercuryazimuth':'',\
			'Venusrise':'',\
			'Venusset':'',\
			'Venusazimuth':'',\
			'Marsrise':'',\
			'Marsset':'',\
			'Marsazimuth':'',\
			'Jupiterrise':'',\
			'Jupiterset':'',\
			'Jupiterazimuth':'',\
			'Saturnrise':'',\
			'Saturnset':'',\
			'Saturnazimuth':'',\
			'Uranusrise':'',\
			'Uranusset':'',\
			'Uranusazimuth':'',\
			'Neptunerise':'',\
			'Neptuneset':'',\
			'Neptuneazimuth':'',\
			'Moonrise':'',\
			'Moonset':'',\
			'Moondist':'',\
			'Moonazimuth':'',\
			'Moonphase':'',\
			'Moonlight':'',\
			'PiconMoon':'1',\
			'Temp':'',\
			'Picon':'',\
			'Skytext':'',\
			'Feelslike':'',\
			'Humidity':'',\
			'Wind':'',\
			'Windspeed':'',\
			'Date0':'',\
			'Shortdate0':'',\
			'Day0':'',\
			'Shortday0':'',\
			'Temp0':'',\
			'Lowtemp0':'',\
			'Hightemp0':'',\
			'Picon0':'',\
			'Skytext0':'',\
			'Precip0':'',\
			'Date1':'',\
			'Shortdate1':'',\
			'Day1':'',\
			'Shortday1':'',\
			'Temp1':'',\
			'Lowtemp1':'',\
			'Hightemp1':'',\
			'Picon1':'',\
			'Skytext1':'',\
			'Precip1':'',\
			'Date2':'',\
			'Shortdate2':'',\
			'Day2':'',\
			'Shortday2':'',\
			'Temp2':'',\
			'Lowtemp2':'',\
			'Hightemp2':'',\
			'Picon2':'',\
			'Skytext2':'',\
			'Precip2':'',\
			'Date3':'',\
			'Shortdate3':'',\
			'Day3':'',\
			'Shortday3':'',\
			'Temp3':'',\
			'Lowtemp3':'',\
			'Hightemp3':'',\
			'Picon3':'',\
			'Skytext3':'',\
			'Precip3':'',\
			'Date4':'',\
			'Shortdate4':'',\
			'Day4':'',\
			'Shortday4':'',\
			'Temp4':'',\
			'Lowtemp4':'',\
			'Hightemp4':'',\
			'Picon4':'',\
			'Skytext4':'',\
			'Precip4':'',\
			}
#		timezone, latitude, longitude, low0weather, hi0weather, low1weather, hi1weather, low2weather, hi2weather, low3weather, hi3weather, low4weather, hi4weather = '', '', '', '', '', '', '', '', '', '', '', '', ''
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
		DEG2RAD = PI / 180 # радианы
		RAD2DEG = 180 / PI # градусы
		try:
			long = float(longitude)
			lat = float(latitude)
			zone = float(timezone)
		except:
			long = lat = zone = 0
		UT = hour + min / 60 + sec / 3600
# Юлианская дата
		if month <= 2:
			year = year - 1
			month = month + 12
		else:
			year = year
			month = month
		JDN = day + int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + 2 - int(year / 100) + int(year / 400) - 1524.5 # - 1522.61
		JD = JDN + UT / 24
# Звездное время
		T = (JDN - 0.5 - 2451545) / 36525 # юлианское столетие на полночь по Гринвичу для введённой даты
		EPS = 23.43929111 - 0.01300416667 * T - 0.00000016389 * T * T + 0.00000050361 * T * T * T # наклон эклиптики
		STT = math.fmod((6.697374558333 + 2400.0513369072223 * T + 0.0000258622 * T * T - 0.00000000172 * T * T * T), 24) # истинное звёздное время в Гринвиче в полночь в долях часа
		ST = math.fmod((STT + (UT - zone + (long / 15)) * 1.0027379093 - (long / 15) * 0.0027379093), 24) # истинное местное звёздное время на момент местного поясного времени η в долях часа
		if ST < 0:
			ST = ST + 24
		ST = ST * 15 # звёздное время момента рассчёта в градусах
# Орбита Земли
		T = (JDN - 2451545) / 36525
		LS = 280.4664568 + 36000.7697509 * T + 0.0003032 * T * T + 0.00000002 * T * T * T # ср долгота солнца
		MS = 357.5291092 + 35999.0502909 * T - 0.0001537 * T * T - 0.00000004 * T * T * T # ср аномалия солнца

		CS = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(MS * DEG2RAD)\
			+ (0.019993 - 0.000101 * T) * math.sin(2 * MS * DEG2RAD)\
			+ 0.000289 * math.sin(3 * MS * DEG2RAD) # уравнение центра солнца
		EO = 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T # эксцентриситет орбиты
		DS = (1.000001018 * (1 - EO * EO)) / (EO * math.cos((MS + CS) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		SLong = LS + CS - (20.4898 / 3600 / DS) # истинная долгота солнца
		EPS = 23.43929111 - 0.01300416667 * T - 0.00000016389 * T * T + 0.00000050361 * T * T * T # наклон эклиптики

#		DEC = math.asin(math.sin(EPS * DEG2RAD) * math.sin(SLong * DEG2RAD)) * RAD2DEG # геоцентрическое склонение солнца
#		RA = math.atan2(math.sin(SLong * DEG2RAD) * math.cos(EPS * DEG2RAD), math.cos(SLong * DEG2RAD)) * RAD2DEG  # геоцентрическое прямое восхождение
#		if RA < 0:
#			RA = RA + 2 * PI
#		QS = math.asin(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(STT - ALFA)) + 0.8332 * DEG2RAD # действительная высота Солнца над горизонтом на момент времени в радианах

		DEC = math.asin(math.sin(EPS * DEG2RAD) * math.sin(SLong * DEG2RAD)) * RAD2DEG # склонение солнца
		ALFA = (7.53 * math.cos(LS * DEG2RAD) + 1.5 * math.sin(LS * DEG2RAD) - 9.87 * math.sin(2 * LS * DEG2RAD)) / 60 # уравнение времени
		BETA = math.acos((math.cos(90.51 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG
		SSS = ALFA + (180 + 15 - long) / 15 + zone # дискретное время zone - long / 15
# Время восхода/захода
		SCh = int(SSS)
		SCm = int(round((SSS - SCh) * 60))
		SRh = int(SSS - BETA / 15)
		SRm = int(round(((SSS - BETA / 15) - SRh - 0.065709833) * 60))
		SSh = int(SSS + BETA / 15)
		SSm = int(round(((SSS + BETA / 15) - SSh + 0.065709833) * 60))
		if SCm == 60:
			SCm = 0
			SCh = SCh + 1
		if SCm < 10:
			SCx = '0'
		else:
			SCx = ''
		if SRm == 60:
			SRm = 0
			SRh = SRh + 1
		if SRm < 10:
			SRx = '0'
		else:
			SRx = ''
		if SSm == 60:
			SSm = 0
			SSh = SSh + 1
		if SSm < 10:
			SSx = '0'
		else:
			SSx = ''
# Орбита Луны
		T = (JDN - 2451545) / 36525
		LM = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T * T * T / 538841 - T * T * T * T / 65194000 # ср долгота луны
		FM = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T - T * T * T / 3526000 + T * T * T * T / 863310000 # ср аргумент широты луны
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср элонгация луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		EM = 1 - 0.002516 * T - 0.0000074 * T * T # поправка на изменяющийся эксцентриситет
		A1 = 119.75 + 131.849 * T
		A2 = 53.09 + 479264.29 * T
		A3 = 313.45 + 481266.484 * T

		EL = 6.288774 * math.sin(MM * DEG2RAD)\
			+ 1.274027 * math.sin((2 * DM - MM) * DEG2RAD)\
			+ 0.658314 * math.sin(2 * DM * DEG2RAD)\
			+ 0.213618 * math.sin(2 * MM * DEG2RAD)\
			- 0.185116 * math.sin(MS * DEG2RAD) * EM\
			- 0.114332 * math.sin(2 * FM * DEG2RAD)\
			+ 0.058793 * math.sin((2 * DM - 2 * MM) * DEG2RAD)\
			+ 0.057066 * math.sin((2 * DM - MS - MM) * DEG2RAD) * EM\
			+ 0.053322 * math.sin((2 * DM + MM) * DEG2RAD)\
			+ 0.045758 * math.sin((2 * DM - MS) * DEG2RAD) * EM\
			- 0.040923 * math.sin((MM - MS) * DEG2RAD)  * EM\
			- 0.034720 * math.sin(DM * DEG2RAD)\
			- 0.030383 * math.sin((MS + MM) * DEG2RAD) * EM\
			+ 0.015327 * math.sin((2 * DM - 2 * FM) * DEG2RAD)\
			- 0.012528 * math.sin((2 * FM + MM) * DEG2RAD)\
			+ 0.010980 * math.sin((2 * FM - MM) * DEG2RAD)\
			+ 0.010675 * math.sin((4 * DM - MM) * DEG2RAD)\
			+ 0.010034 * math.sin(3 * MM * DEG2RAD)\
			+ 0.008548 * math.sin((4 * DM - 2 * MM) * DEG2RAD)\
			- 0.007888 * math.sin((2 * DM + MS - MM) * DEG2RAD) * EM\
			- 0.006766 * math.sin((2 * DM + MS) * DEG2RAD) * EM\
			- 0.005163 * math.sin((MM - DM) * DEG2RAD)\
			+ 0.004987 * math.sin((MS + DM) * DEG2RAD) * EM\
			+ 0.004036 * math.sin((2 * DM + MM - MS) * DEG2RAD) * EM\
			+ 0.003994 * math.sin((2 * MM + 2 * DM) * DEG2RAD)\
			+ 0.003861 * math.sin(4 * DM * DEG2RAD)\
			+ 0.003665 * math.sin((2 * DM - 3 * MM) * DEG2RAD)\
			- 0.002689 * math.sin((2 * MM - MS) * DEG2RAD) * EM\
			- 0.002602 * math.sin((2 * DM + 2 * FM - MM) * DEG2RAD)\
			+ 0.002390 * math.sin((2 * DM - 2 * MM - MS) * DEG2RAD) * EM\
			- 0.002348 * math.sin((MM + DM) * DEG2RAD)\
			+ 0.002236 * math.sin((2 * DM - 2 * MS) * DEG2RAD) * EM * EM\
			- 0.002120 * math.sin((2 * MM + MS) * DEG2RAD) * EM\
			- 0.002069 * math.sin(2 * MS * DEG2RAD) * EM * EM\
			+ 0.002048 * math.sin((2 * DM - 2 * MS - MM) * DEG2RAD) * EM * EM\
			- 0.001773 * math.sin((2 * DM - 2 * FM + MM) * DEG2RAD)\
			- 0.001595 * math.sin((2 * DM + 2 * FM) * DEG2RAD)\
			+ 0.001215 * math.sin((4 * DM - MS - MM) * DEG2RAD) * EM\
			- 0.001110 * math.sin((2 * MM + 2 * FM) * DEG2RAD)\
			- 0.000892 * math.sin((3 * DM - MM) * DEG2RAD)\
			- 0.000810 * math.sin((2 * DM + MS + MM) * DEG2RAD) * EM\
			+ 0.000759 * math.sin((4 * DM - 2 * MM - MS) * DEG2RAD) * EM\
			- 0.000713 * math.sin((2 * MS - MM) * DEG2RAD) * EM * EM\
			- 0.000700 * math.sin((2 * DM + 2 * MS - MM) * DEG2RAD) * EM * EM\
			+ 0.000691 * math.sin((2 * DM - 2 * MM + MS) * DEG2RAD) * EM\
			+ 0.000596 * math.sin((2 * DM - 2 * FM - MS) * DEG2RAD) * EM\
			+ 0.000549 * math.sin((4 * DM + MM) * DEG2RAD)\
			+ 0.000537 * math.sin(4 * MM * DEG2RAD)\
			+ 0.000520 * math.sin((4 * DM - MS) * DEG2RAD) * EM\
			- 0.000487 * math.sin((2 * MM - DM) * DEG2RAD)\
			- 0.000399 * math.sin((2 * DM - 2 * FM + MS) * DEG2RAD) * EM\
			- 0.000381 * math.sin((2 * MM - 2 * FM) * DEG2RAD)\
			+ 0.000351 * math.sin((DM + MS + MM) * DEG2RAD) * EM\
			- 0.000340 * math.sin((3 * DM - 2 * MM) * DEG2RAD)\
			+ 0.000330 * math.sin((4 * DM - 3 * MM) * DEG2RAD)\
			+ 0.000327 * math.sin((2 * DM + 2 * MM - MS) * DEG2RAD) * EM\
			- 0.000323 * math.sin((2 * MS + MM) * DEG2RAD) * EM * EM\
			+ 0.000299 * math.sin((DM + MS - MM) * DEG2RAD) * EM\
			+ 0.000294 * math.sin((2 * DM + 3 * MM) * DEG2RAD)\
			+ 0.003958 * math.sin(A1 * DEG2RAD)\
			+ 0.001962 * math.sin((LM - FM) * DEG2RAD)\
			+ 0.000318 * math.sin(A2 * DEG2RAD)

		EB = 5.128122 * math.sin(FM * DEG2RAD)\
			+ 0.280602 * math.sin((MM + FM) * DEG2RAD)\
			+ 0.277693 * math.sin((MM - FM) * DEG2RAD)\
			+ 0.173237 * math.sin((2 * DM - FM) * DEG2RAD)\
			+ 0.055413 * math.sin((2 * DM + FM - MM) * DEG2RAD)\
			+ 0.046271 * math.sin((2 * DM - FM - MM) * DEG2RAD)\
			+ 0.032573 * math.sin((2 * DM + FM) * DEG2RAD)\
			+ 0.017198 * math.sin((2 * MM + FM) * DEG2RAD)\
			+ 0.009266 * math.sin((2 * DM + MM - FM) * DEG2RAD)\
			+ 0.008822 * math.sin((2 * MM - FM) * DEG2RAD)\
			+ 0.008216 * math.sin((2 * DM - MS - FM) * DEG2RAD) * EM\
			+ 0.004324 * math.sin((2 * DM - 2 * MM - FM) * DEG2RAD)\
			+ 0.004200 * math.sin((2 * DM + FM + MM) * DEG2RAD)\
			- 0.003359 * math.sin((2 * DM + MS -FM) * DEG2RAD) * EM\
			+ 0.002463 * math.sin((2 * DM + FM - MS - MM) * DEG2RAD) * EM\
			+ 0.002211 * math.sin((2 * DM + FM - MS) * DEG2RAD) * EM\
			+ 0.002065 * math.sin((2 * DM - FM - MS - MM) * DEG2RAD) * EM\
			- 0.001870 * math.sin((FM - MS + MM) * DEG2RAD) * EM\
			+ 0.001828 * math.sin((4 * DM - FM - MM) * DEG2RAD)\
			- 0.001794 * math.sin((FM + MS) * DEG2RAD) * EM\
			- 0.001749 * math.sin(3 * FM * DEG2RAD)\
			- 0.001565 * math.sin((FM + MS - MM) * DEG2RAD) * EM\
			- 0.001491 * math.sin((FM + DM) * DEG2RAD)\
			- 0.001475 * math.sin((FM + MS + MM) * DEG2RAD) * EM\
			- 0.001410 * math.sin((MM + MS - FM) * DEG2RAD) * EM\
			- 0.001344 * math.sin((FM - MS) * DEG2RAD) * EM\
			- 0.001335 * math.sin((FM - DM) * DEG2RAD)\
			+ 0.001107 * math.sin((3 * MM + FM) * DEG2RAD)\
			+ 0.001021 * math.sin((4 * DM - FM) * DEG2RAD)\
			+ 0.000833 * math.sin((4 * DM + FM - MM) * DEG2RAD)\
			+ 0.000777 * math.sin((3 * FM - MM) * DEG2RAD)\
			+ 0.000671 * math.sin((4 * DM - 2 * MM + FM) * DEG2RAD)\
			+ 0.000607 * math.sin((2 * DM - 3 * FM) * DEG2RAD)\
			+ 0.000596 * math.sin((2 * DM + 2 * MM - FM) * DEG2RAD)\
			+ 0.000491 * math.sin((2 * DM + MM - MS - FM) * DEG2RAD) * EM\
			- 0.000451 * math.sin((2 * MM - 2 * DM + FM) * DEG2RAD)\
			+ 0.000439 * math.sin((3 * MM - FM) * DEG2RAD)\
			+ 0.000422 * math.sin((2 * DM + 2 * MM + FM) * DEG2RAD)\
			+ 0.000421 * math.sin((2 * DM - 3 * MM - FM) * DEG2RAD)\
			- 0.000366 * math.sin((2 * DM + MS + FM - MM) * DEG2RAD) * EM\
			- 0.000351 * math.sin((2 * DM + MS + FM) * DEG2RAD) * EM\
			+ 0.000331 * math.sin((4 * DM + FM) * DEG2RAD)\
			+ 0.000315 * math.sin((2 * DM + FM - MS + MM) * DEG2RAD) * EM\
			+ 0.000302 * math.sin((2 * DM - 2 * MS - FM) * DEG2RAD) * EM * EM\
			- 0.000283 * math.sin((3 * FM + MM) * DEG2RAD)\
			- 0.000229 * math.sin((2 * DM + MS + MM - FM) * DEG2RAD) * EM\
			+ 0.000223 * math.sin((DM + MS - FM) * DEG2RAD) * EM\
			+ 0.000223 * math.sin((DM + MS + FM) * DEG2RAD) * EM\
			- 0.000220 * math.sin((MS - 2 * MM - FM) * DEG2RAD) * EM\
			- 0.000220 * math.sin((2 * DM + MS - MM - FM) * DEG2RAD) * EM\
			- 0.000185 * math.sin((DM + MM + FM) * DEG2RAD)\
			+ 0.000181 * math.sin((2 * DM - MS - 2 * MM - FM) * DEG2RAD) * EM\
			- 0.000177 * math.sin((2 * MM + MS + FM) * DEG2RAD) * EM\
			+ 0.000176 * math.sin((4 * DM - 2 * MM - FM) * DEG2RAD)\
			+ 0.000166 * math.sin((4 * DM - MS - MM - FM) * DEG2RAD) * EM\
			- 0.000164 * math.sin((DM + MM - FM) * DEG2RAD)\
			+ 0.000132 * math.sin((4 * DM + MM - FM) * DEG2RAD)\
			- 0.000119 * math.sin((DM - MM - FM) * DEG2RAD)\
			+ 0.000115 * math.sin((4 * DM - MS - FM) * DEG2RAD) * EM\
			+ 0.000107 * math.sin((2 * DM - 2 * MS + FM) * DEG2RAD) * EM * EM\
			- 0.002235 * math.sin(LM * DEG2RAD)\
			+ 0.000382 * math.sin(A3 * DEG2RAD)\
			+ 0.000175 * math.sin((A1 - FM) * DEG2RAD)\
			+ 0.000175 * math.sin((A1 + FM) * DEG2RAD)\
			+ 0.000127 * math.sin((LM - MM) * DEG2RAD)\
			- 0.000115 * math.sin((LM + MM) * DEG2RAD)

		ER = - 20.905355 * math.cos(MM * DEG2RAD)\
			- 3.699111 * math.cos((2 * DM - MM) * DEG2RAD)\
			- 2.955968 * math.cos(2 * DM * DEG2RAD)\
			- 0.569925 * math.cos(2 * MM * DEG2RAD)\
			+ 0.048888 * math.cos(MS * DEG2RAD) * EM\
			- 0.003149 * math.cos(2 * FM * DEG2RAD)\
			+ 0.246158 * math.cos((2 * DM - 2 * MM) * DEG2RAD)\
			- 0.152138 * math.cos((2 * DM - MS - MM) * DEG2RAD) * EM\
			- 0.170733 * math.cos((2 * DM + MM) * DEG2RAD)\
			- 0.204586 * math.cos((2 * DM - MS) * DEG2RAD) * EM\
			- 0.129620 * math.cos((MM - MS) * DEG2RAD) * EM\
			+ 0.108743 * math.cos(DM * DEG2RAD)\
			+ 0.104755 * math.cos((MM + MS) * DEG2RAD) * EM\
			+ 0.010321 * math.cos((2 * DM - 2 * FM) * DEG2RAD)\
			+ 0.079661 * math.cos((MM - 2 * FM) * DEG2RAD)\
			- 0.034782 * math.cos((4 * DM - MM) * DEG2RAD)\
			- 0.023210 * math.cos(3 * MM * DEG2RAD)\
			- 0.021636 * math.cos((4 * DM - 2 * MM) * DEG2RAD)\
			+ 0.024208 * math.cos((2 * DM + MS - MM) * DEG2RAD) * EM\
			+ 0.030824 * math.cos((2 * DM + MS) * DEG2RAD) * EM\
			- 0.008379 * math.cos((DM - MM) * DEG2RAD)\
			- 0.016675 * math.cos((DM + MS) * DEG2RAD) * EM\
			- 0.012831 * math.cos((2 * DM - MS + MM) * DEG2RAD) * EM\
			- 0.010445 * math.cos((2 * DM + 2 * MM) * DEG2RAD)\
			- 0.011650 * math.cos(4 * DM * DEG2RAD)\
			+ 0.014403 * math.cos((2 * DM - 3 * MM) * DEG2RAD)\
			- 0.007003 * math.cos((MS - 2 * MM) * DEG2RAD) * EM\
			+ 0.010056 * math.cos((2 * DM - MS - 2 * MM) * DEG2RAD) * EM\
			+ 0.006322 * math.cos((DM + MM) * DEG2RAD)\
			- 0.009884 * math.cos((2 * DM - 2 * MS) * DEG2RAD) * EM * EM\
			+ 0.005751 * math.cos((MS + 2 * MM) * DEG2RAD) * EM\
			- 0.004950 * math.cos((2 * DM - 2 * MS - MM) * DEG2RAD) * EM * EM\
			+ 0.004130 * math.cos((2 * DM + MM - 2 * FM) * DEG2RAD)\
			- 0.003958 * math.cos((4 * DM - MS - MM) * DEG2RAD) * EM\
			+ 0.003258 * math.cos((3 * DM - MM) * DEG2RAD)\
			+ 0.002616 * math.cos((2 * DM + MS + MM) * DEG2RAD) * EM\
			- 0.001897 * math.cos((4 * DM - MS - 2 * MM) * DEG2RAD) * EM\
			- 0.002117 * math.cos((2 * MS - MM) * DEG2RAD) * EM * EM\
			+ 0.002354 * math.cos((2 * DM + 2 * MS - MM) * DEG2RAD) * EM * EM\
			- 0.001423 * math.cos((4 * DM + MM) * DEG2RAD)\
			- 0.001117 * math.cos(4 * MM * DEG2RAD)\
			- 0.001571 * math.cos((4 * DM - MS) * DEG2RAD) * EM\
			- 0.001739 * math.cos((DM - 2 * MM) * DEG2RAD)\
			- 0.004421 * math.cos((2 * MM - 2 * FM) * DEG2RAD)\
			+ 0.001165 * math.cos((2 * MS + MM) * DEG2RAD) * EM * EM\
			+ 0.008752 * math.cos((2 * DM - MM - 2 * FM) * DEG2RAD)

		EPS = 23.43929111 - 0.01300416667 * T - 0.00000016389 * T * T + 0.00000050361 * T * T * T # наклон эклиптики

		MLat = EB # широта луны
		MLong = math.fmod(LM + EL, 360) # долгота луны
		Mdist = int(385000.56 + ER * 1000) # расстояние до луны км
		if MLong < 0:
			MLong = MLong + 360

		RA = math.atan2((math.sin(MLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(MLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(MLong * DEG2RAD)) * RAD2DEG # геоцентрическое прямое восхождение луны
		DEC = math.asin(math.sin(MLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(MLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(MLong * DEG2RAD)) * RAD2DEG # геоцентрическое склонение луны
#		if RA < 0:
#			RA = RA + 2 * PI
		BETA = math.acos((math.cos(89.54 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол луны

		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут
		Mazim = round(AZ, 1)

#		SMR = RA - BETA
		SMR = math.fmod((RA - BETA) / 15 - (zone - long / 15) - (STT - long / 15 / 24 * 0.065709833) * 0.997269566423530, 24) # дискретное время zone - long / 15
		if SMR < 0:
			SMR = SMR + 24
#		SMS = RA + BETA
		SMS = math.fmod((RA + BETA) / 15 - (zone - long / 15) - (STT - long / 15 / 24 * 0.065709833) * 0.997269566423530, 24) # дискретное время zone - long / 15
		if SMS < 0:
			SMS = SMS + 24
# Время восхода/захода
		MRh = int(SMR)
		MRm = int(round(((SMR) - MRh) * 60))
		MSh = int(SMS)
		MSm = int(round(((SMS) - MSh) * 60))
		if MRm == 60:
			MRm = 0
			MRh = MRh + 1
		if MRm < 10:
			MRx = '0'
		else:
			MRx = ''
		if MSm == 60:
			MSm = 0
			MSh = MSh + 1
		if MSm < 10:
			MSx = '0'
		else:
			MSx = ''
# Фазы Луны
		T = (JD - 2451545) / 36525
#		LM = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T * T * T / 538841 - T * T * T * T / 65194000 # ср долгота луны
#		FM = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T - T * T * T / 3526000 + T * T * T * T / 863310000 # ср растояние луны
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср удлинение луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		IM = 180 - DM\
			- 6.289 * math.sin(MM * DEG2RAD)\
			+ 2.100 * math.sin(MS * DEG2RAD)\
			- 1.274 * math.sin((2 * DM - MM) * DEG2RAD)\
			- 0.658 * math.sin(2 * DM * DEG2RAD)\
			- 0.214 * math.sin(2 * MM * DEG2RAD)\
			- 0.114 * math.sin(DM * DEG2RAD)
		pha1 = (1 + math.cos(IM * DEG2RAD)) / 2
#
		T = (JD + 0.5 / 24 - 2451545) / 36525
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср удлинение луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		IM = 180 - DM\
			- 6.289 * math.sin(MM * DEG2RAD)\
			+ 2.100 * math.sin(MS * DEG2RAD)\
			- 1.274 * math.sin((2 * DM - MM) * DEG2RAD)\
			- 0.658 * math.sin(2 * DM * DEG2RAD)\
			- 0.214 * math.sin(2 * MM * DEG2RAD)\
			- 0.114 * math.sin(DM * DEG2RAD)
		pha2 = (1 + math.cos(IM * DEG2RAD)) / 2
		if pha2 - pha1 < 0:
			trend = -1
		else:
			trend = 1
		light = 100 * pha1
		light = round(light, 1)
		if light >= 0 and light <= 5:
			pic = '5'
			phase = _('New moon')
			if trend == -1:
				pic = '05'
				phase = _('New moon')
		elif light > 5 and light <= 10:
			pic = '10'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '010'
				phase = _('Waning crescent')
		elif light > 10 and light <= 15:
			pic = '15'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '015'
				phase = _('Waning crescent')
		elif light > 15 and light <= 20:
			pic = '20'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '020'
				phase = _('Waning crescent')
		elif light > 20 and light <= 25:
			pic = '25'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '025'
				phase = _('Waning crescent')
		elif light > 25 and light <= 30:
			pic = '30'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '030'
				phase = _('Waning crescent')
		elif light > 30 and light <= 35:
			pic = '35'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '035'
				phase = _('Waning crescent')
		elif light > 35 and light <= 40:
			pic = '40'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '040'
				phase = _('Waning crescent')
		elif light > 40 and light <= 45:
			pic = '45'
			phase = _('Waxing cresent')
			if trend == -1:
				pic = '045'
				phase = _('Waning crescent')
		elif light > 45 and light <= 50:
			pic = '50'
			phase = _('First quarter')
			if trend == -1:
				pic = '050'
				phase = _('Last quarter')
		elif light > 50 and light <= 55:
			pic = '55'
			phase = _('First quarter')
			if trend == -1:
				pic = '055'
				phase = _('Last quarter')
		elif light > 55 and light <= 60:
			pic = '60'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '060'
				phase = _('Waning gibbous')
		elif light > 60 and light <= 65:
			pic = '65'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '065'
				phase = _('Waning gibbous')
		elif light > 65 and light <= 70:
			pic = '70'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '070'
				phase = _('Waning gibbous')
		elif light > 70 and light <= 75:
			pic = '75'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '075'
				phase = _('Waning gibbous')
		elif light > 75 and light <= 80:
			pic = '80'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '080'
				phase = _('Waning gibbous')
		elif light > 80 and light <= 85:
			pic = '85'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '085'
				phase = _('Waning gibbous')
		elif light > 85 and light <= 90:
			pic = '90'
			phase = _('Waxing gibbous')
			if trend == -1:
				pic = '090'
				phase = _('Waning gibbous')
		elif light > 90 and light <= 95:
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
			msnweather['Julianday'] = '%s' % JD
			msnweather['Sunrise'] = '%s%s%s%s' % (SRh, unichr(58).encode("latin-1"), SRx, SRm)
			msnweather['Sunset'] = '%s%s%s%s' % (SSh, unichr(58).encode("latin-1"), SSx, SSm)
			msnweather['Solstice'] = '%s%s%s%s' % (SCh, unichr(58).encode("latin-1"), SCx, SCm)

			msnweather['Moondist'] = _('%s km') % Mdist
			msnweather['Moonazimuth'] = '%s %s' % (Mazim, unichr(176).encode("latin-1"))
			msnweather['Moonrise'] = '%s%s%s%s' % (MRh, unichr(58).encode("latin-1"), MRx, MRm)
			msnweather['Moonset'] = '%s%s%s%s' % (MSh, unichr(58).encode("latin-1"), MSx, MSm)
			msnweather['Moonphase'] = '%s' % phase
			msnweather['Moonlight'] = '%s %s' % (light, unichr(37).encode("latin-1"))
			msnweather['PiconMoon'] = '%s' % pic
		except:
			pass
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
# Астро
		if self.type is self.SUNRISE:
			info = msnweather['Sunrise']
		if self.type is self.SUNSET:
			info = msnweather['Sunset']
		if self.type is self.SUNCULMINATION:
			info = msnweather['Solstice']
		if self.type is self.MERCURYRISE:
			info = msnweather['Mercuryrise']
		if self.type is self.MERCURYSET:
			info = msnweather['Mercuryset']
		if self.type is self.MERCURYAZIMUTH:
			info = msnweather['Mercuryazimuth']
		if self.type is self.VENUSRISE:
			info = msnweather['Venusrise']
		if self.type is self.VENUSSET:
			info = msnweather['Venusset']
		if self.type is self.VENUSAZIMUTH:
			info = msnweather['Venusazimuth']
		if self.type is self.MARSRISE:
			info = msnweather['Marsrise']
		if self.type is self.MARSSET:
			info = msnweather['Marsset']
		if self.type is self.MARSAZIMUTH:
			info = msnweather['Marsazimuth']
		if self.type is self.JUPITERRISE:
			info = msnweather['Jupiterrise']
		if self.type is self.JUPITERSET:
			info = msnweather['Jupiterset']
		if self.type is self.JUPITERAZIMUTH:
			info = msnweather['Jupiterazimuth']
		if self.type is self.SATURNRISE:
			info = msnweather['Saturnrise']
		if self.type is self.SATURNSET:
			info = msnweather['Saturnset']
		if self.type is self.SATURNAZIMUTH:
			info = msnweather['Saturnazimuth']
		if self.type is self.URANUSRISE:
			info = msnweather['Uranusrise']
		if self.type is self.URANUSSET:
			info = msnweather['Uranusset']
		if self.type is self.URANUSAZIMUTH:
			info = msnweather['Uranusazimuth']
		if self.type is self.NEPTUNERISE:
			info = msnweather['Neptunerise']
		if self.type is self.NEPTUNESET:
			info = msnweather['Neptuneset']
		if self.type is self.NEPTUNEAZIMUTH:
			info = msnweather['Neptuneazimuth']
		if self.type is self.MOONRISE:
			info = msnweather['Moonrise']
		if self.type is self.MOONSET:
			info = msnweather['Moonset']
		if self.type is self.MOONDIST:
			info = msnweather['Moondist']
		if self.type is self.MOONAZIMUTH:
			info = msnweather['Moonazimuth']
		if self.type is self.MOONPHASE:
			info = msnweather['Moonphase']
		if self.type is self.MOONLIGHT:
			info = msnweather['Moonlight']
		if self.type is self.MOONPICON:
			info = msnweather['PiconMoon']
# Сегодня
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
