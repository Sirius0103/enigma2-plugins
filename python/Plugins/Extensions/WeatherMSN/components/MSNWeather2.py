# -*- coding: UTF-8 -*-
## MSNWeather Converter
## Coded by Sirius
## version 0.7

from Tools.Directories import fileExists, pathExists
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config, configfile
from Components.Console import Console as iConsole
from Components.Language import language
from os import environ
from Poll import Poll
import gettext
import time
import os

weather_city = config.plugins.weathermsn.city.value
degreetype = config.plugins.weathermsn.degreetype.value
windtype = config.plugins.weathermsn.windtype.value
weather_location = config.osd.language.value.replace('_', '-')

#weather_city = 'Moscow,Moscow-City,Russia'
#degreetype = 'C'
#windtype = 'ms'
#weather_location = 'ru-RU'
if weather_location == 'en-EN':
	weather_location = 'en-US'

time_update = 20
time_update_ms = 3000

class MSNWeather2(Poll, Converter, object):

	VFD = 1
	DATE = 2
	SHORTDATE = 3
	DAY = 4
	SHORTDAY = 5
	LOCATION = 6
	TIMEZONE = 7
	LATITUDE = 8
	LONGITUDE = 9
	TEMP = 10
	PICON = 11
	SKYTEXT = 12
	FEELSLIKE = 13
	HUMIDITY = 14
	WIND = 15
	WINDSPEED = 16
	DATE0 = 20
	SHORTDATE0 = 21
	DAY0 = 22
	SHORTDAY0 = 23
	TEMP0 = 24
	LOWTEMP0 = 25
	HIGHTEMP0 = 26
	PICON0 = 27
	SKYTEXT0 = 28
	PRECIP0 = 29
	DATE1 = 30
	SHORTDATE1 = 31
	DAY1 = 32
	SHORTDAY1 = 33
	TEMP1 = 34
	LOWTEMP1 = 35
	HIGHTEMP1 = 36
	PICON1 = 37
	SKYTEXT1 = 38
	PRECIP1 = 39
	DATE2 = 40
	SHORTDATE2 = 41
	DAY2 = 42
	SHORTDAY2 = 43
	TEMP2 = 44
	LOWTEMP2 = 45
	HIGHTEMP2 = 46
	PICON2 = 47
	SKYTEXT2 = 48
	PRECIP2 = 49
	DATE3 = 50
	SHORTDATE3 = 51
	DAY3 = 52
	SHORTDAY3 = 53
	TEMP3 = 54
	LOWTEMP3 = 55
	HIGHTEMP3 = 56
	PICON3 = 57
	SKYTEXT3 = 58
	PRECIP3 = 59
	DATE4 = 60
	SHORTDATE4 = 61
	DAY4 = 62
	SHORTDAY4 = 63
	TEMP4 = 64
	LOWTEMP4 = 65
	HIGHTEMP4 = 66
	PICON4 = 67
	SKYTEXT4 = 68
	PRECIP4 = 69

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
		elif type == "Picon3":
			self.type = self.PICON3
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
		with open('/tmp/weathermsn.xml', 'w') as noneweather:
			noneweather.write('None')
		noneweather.close()

	def get_xmlfile(self):
		self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' -O /tmp/weathermsn.xml" % (degreetype, weather_location, weather_city), self.control_xml)

	@cached
	def getText(self):
		info, weze = 'n/a', ''
		msnweather = {'Vfd':'', 'Date':'', 'Shortdate':'', 'Day':'', 'Shortday':'',\
			'Location':'', 'Timezone':'', 'Latitude':'', 'Longitude':'',\
			'Temp':'', 'Picon':'', 'Skytext':'', 'Feelslike':'', 'Humidity':'', 'Wind':'', 'Windspeed':'',\
			'Date0':'', 'Shortdate0':'', 'Day0':'', 'Shortday0':'', 'Temp0':'', 'Lowtemp0':'', 'Hightemp0':'', 'Picon0':'', 'Skytext0':'', 'Precip0':'',\
			'Date1':'', 'Shortdate1':'', 'Day1':'', 'Shortday1':'', 'Temp1':'', 'Lowtemp1':'', 'Hightemp1':'', 'Picon1':'', 'Skytext1':'', 'Precip1':'',\
			'Date2':'', 'Shortdate2':'', 'Day2':'', 'Shortday2':'', 'Temp2':'', 'Lowtemp2':'', 'Hightemp2':'', 'Picon2':'', 'Skytext2':'', 'Precip2':'',\
			'Date3':'', 'Shortdate3':'', 'Day3':'', 'Shortday3':'', 'Temp3':'', 'Lowtemp3':'', 'Hightemp3':'', 'Picon3':'', 'Skytext3':'', 'Precip3':'',\
			'Date4':'', 'Shortdate4':'', 'Day4':'', 'Shortday4':'', 'Temp4':'', 'Lowtemp4':'', 'Hightemp4':'', 'Picon4':'', 'Skytext4':'', 'Precip4':'',\
			}
		low0weather, hi0weather, low1weather, hi1weather, low2weather, hi2weather, low3weather, hi3weather, low4weather, hi4weather = '', '', '', '', '', '', '', '', '', ''
		if fileExists("/tmp/weathermsn.xml"):
			if int((time.time() - os.stat('/tmp/weathermsn.xml').st_mtime)/60) >= time_update:
				self.get_xmlfile()
		else:
			self.get_xmlfile()
		if not fileExists('/tmp/weathermsn.xml'):
			self.write_none()
			return info
		if fileExists('/tmp/weathermsn.xml') and open('/tmp/weathermsn.xml').read() is 'None':
			return info
		for line in open("/tmp/weathermsn.xml"):
			try:
				if "<weather" in line:
					msnweather['Location'] = line.split('weatherlocationname')[1].split('"')[1].split(",")[0]
					if not line.split('timezone')[1].split('"')[1][0] is '0':
						msnweather['Timezone'] = '+' + line.split('timezone')[1].split('"')[1] + ' h'
					else:
						msnweather['Timezone'] = line.split('timezone')[1].split('"')[1] + ' h'
					msnweather['Latitude'] = line.split(' lat')[1].split('"')[1]
					msnweather['Longitude'] = line.split(' long')[1].split('"')[1]
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
					msnweather['Humidity'] = line.split('humidity')[1].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
					try:
						msnweather['Wind'] = line.split('winddisplay')[1].split('"')[1].split(' ')[2]
					except:
						pass
					if line.split('attribution2')[1].split('"')[1] == '© Foreca':
				# m/s
						if windtype == 'ms':
							msnweather['Windspeed'] = '%3.02f m/s' % (float(line.split('windspeed')[1].split('"')[1]) * 0.28)
				# ft/s
						elif windtype == 'fts':
							msnweather['Windspeed']= '%3.02f ft/s' % (float(line.split('windspeed')[1].split('"')[1]) * 0.91)
				# mp/h
						elif windtype == 'mph':
							msnweather['Windspeed'] = '%3.02f mp/h' % (float(line.split('windspeed')[1].split('"')[1]) * 0.62)
				# knots
						elif windtype == 'knots':
							msnweather['Windspeed'] = '%3.02f knots' % (float(line.split('windspeed')[1].split('"')[1]) * 0.54)
				# km/h
						elif windtype == 'kmh':
							msnweather['Windspeed'] = '%s km/h' % line.split('windspeed')[1].split('"')[1]
					if line.split('attribution2')[1].split('"')[1] == 'wdt':
				# m/s
						if windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'm/s':
							msnweather['Windspeed'] = '%s m/s' % line.split('windspeed')[1].split('"')[1].split(" ")[0]
						elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'kmph':
							msnweather['Windspeed'] = '%3.02f m/s' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 0.28)
						elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'mph':
							msnweather['Windspeed'] = '%3.02f m/s' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 0.45)
				# ft/s
						elif windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'm/s':
							msnweather['Windspeed']= '%3.02f ft/s' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 3.28)
						elif windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'kmph':
							msnweather['Windspeed']= '%3.02f ft/s' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 0.91)
						elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'mph':
							msnweather['Windspeed'] = '%3.02f ft/s' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 1.47)
				# mp/h
						elif windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'm/s':
							msnweather['Windspeed'] = '%3.02f mp/h' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 2.24)
						elif windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'kmph':
							msnweather['Windspeed'] = '%3.02f mp/h' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 0.62)
						elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'mph':
							msnweather['Windspeed'] =  '%s mp/h' % line.split('windspeed')[1].split('"')[1].split(" ")[0]
				# knots
						elif windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'm/s':
							msnweather['Windspeed'] = '%3.02f knots' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 1.94)
						elif windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'kmph':
							msnweather['Windspeed'] = '%3.02f knots' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 0.54)
						elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'mph':
							msnweather['Windspeed'] = '%3.02f knots' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 0.87)
				# km/h
						elif windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'm/s':
							msnweather['Windspeed'] = '%3.02f km/h' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 3.6)
						elif windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'kmph':
							msnweather['Windspeed'] = '%s km/h' % line.split('windspeed')[1].split('"')[1].split(" ")[0]
						elif windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(" ")[1] == 'mph':
							msnweather['Windspeed'] = '%3.02f km/h' % (float(line.split('windspeed')[1].split('"')[1].split(" ")[0]) * 1.61)
					msnweather['Date'] = line.split('date')[1].split('"')[1].split("-")[2].strip() + '.' + line.split('date')[1].split('"')[1].split("-")[1].strip() + '.' + line.split('date')[1].split('"')[1].split("-")[0].strip()
					msnweather['Shortdate'] = line.split('shortday')[1].split('"')[1] + ' ' + line.split('date')[1].split('"')[1].split("-")[2].strip()
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
					msnweather['Temp0'] =  '%s / %s' % (hi0weather, low0weather)
					msnweather['Picon0'] = line.split('skycodeday')[1].split('"')[1]
					msnweather['Date0'] = line.split('date')[2].split('"')[1].split("-")[2].strip() + '.' + line.split('date')[2].split('"')[1].split("-")[1].strip() + '.' + line.split('date')[2].split('"')[1].split("-")[0].strip()
					msnweather['Shortdate0'] = line.split('shortday')[2].split('"')[1] + ' ' + line.split('date')[2].split('"')[1].split("-")[2].strip()
					msnweather['Day0'] = line.split(' day')[2].split('"')[1]
					msnweather['Shortday0'] = line.split('shortday')[2].split('"')[1]
					msnweather['Skytext0'] = line.split('skytextday')[1].split('"')[1]
					msnweather['Precip0'] = line.split('precip')[1].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
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
					msnweather['Temp1'] =  '%s / %s' % (hi1weather, low1weather)
					msnweather['Picon1'] = line.split('skycodeday')[2].split('"')[1]
					msnweather['Date1'] = line.split('date')[3].split('"')[1].split("-")[2].strip() + '.' + line.split('date')[3].split('"')[1].split("-")[1].strip() + '.' + line.split('date')[3].split('"')[1].split("-")[0].strip()
					msnweather['Shortdate1'] = line.split('shortday')[3].split('"')[1] + ' ' + line.split('date')[3].split('"')[1].split("-")[2].strip()
					msnweather['Day1'] = line.split(' day')[3].split('"')[1]
					msnweather['Shortday1'] = line.split('shortday')[3].split('"')[1]
					msnweather['Skytext1'] = line.split('skytextday')[2].split('"')[1]
					msnweather['Precip1'] = line.split('precip')[2].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
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
					msnweather['Temp2'] =  '%s / %s' % (hi2weather, low2weather)
					msnweather['Picon2'] = line.split('skycodeday')[3].split('"')[1]
					msnweather['Date2'] = line.split('date')[4].split('"')[1].split("-")[2].strip() + '.' + line.split('date')[4].split('"')[1].split("-")[1].strip() + '.' + line.split('date')[4].split('"')[1].split("-")[0].strip()
					msnweather['Shortdate2'] = line.split('shortday')[4].split('"')[1] + ' ' + line.split('date')[4].split('"')[1].split("-")[2].strip()
					msnweather['Day2'] = line.split(' day')[4].split('"')[1]
					msnweather['Shortday2'] = line.split('shortday')[4].split('"')[1]
					msnweather['Skytext2'] = line.split('skytextday')[3].split('"')[1]
					msnweather['Precip2'] = line.split('precip')[3].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
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
					msnweather['Temp3'] =  '%s / %s' % (hi3weather, low3weather)
					msnweather['Picon3'] = line.split('skycodeday')[4].split('"')[1]
					msnweather['Date3'] = line.split('date')[5].split('"')[1].split("-")[2].strip() + '.' + line.split('date')[5].split('"')[1].split("-")[1].strip() + '.' + line.split('date')[5].split('"')[1].split("-")[0].strip()
					msnweather['Shortdate3'] = line.split('shortday')[5].split('"')[1] + ' ' + line.split('date')[5].split('"')[1].split("-")[2].strip()
					msnweather['Day3'] = line.split(' day')[5].split('"')[1]
					msnweather['Shortday3'] = line.split('shortday')[5].split('"')[1]
					msnweather['Skytext3'] = line.split('skytextday')[4].split('"')[1]
					msnweather['Precip3'] = line.split('precip')[4].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
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
					msnweather['Temp4'] =  '%s / %s' % (hi4weather, low4weather)
					msnweather['Picon4'] = line.split('skycodeday')[5].split('"')[1]
					msnweather['Date4'] = line.split('date')[6].split('"')[1].split("-")[2].strip() + '.' + line.split('date')[6].split('"')[1].split("-")[1].strip() + '.' + line.split('date')[6].split('"')[1].split("-")[0].strip()
					msnweather['Shortdate4'] = line.split('shortday')[6].split('"')[1] + ' ' + line.split('date')[6].split('"')[1].split("-")[2].strip()
					msnweather['Day4'] = line.split(' day')[6].split('"')[1]
					msnweather['Shortday4'] = line.split('shortday')[6].split('"')[1]
					msnweather['Skytext4'] = line.split('skytextday')[5].split('"')[1]
					msnweather['Precip4'] = line.split('precip')[5].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
			except:
				pass
#
		if self.type is self.VFD:
			try:
				weze = msnweather['Skytext'].split(" ")[1]
			except:
				weze = msnweather['Skytext']
			info = msnweather['Temp'] + " " + weze
		if self.type is self.DATE:
			info = msnweather['Date']
		if self.type is self.SHORTDATE:
			info = msnweather['Shortdate']
		if self.type is self.DAY:
			info = msnweather['Day']
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
		if self.type is self.PICON3:
			info = msnweather['Picon3']
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
