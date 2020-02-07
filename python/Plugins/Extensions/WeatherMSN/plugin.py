# -*- coding: UTF-8 -*-
#
# Plugin - Weather MSN
# Developer - Sirius
# Patch Showsearch - Nikolasi
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
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Language import language
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigText, ConfigYesNo, ConfigSubsection, ConfigSelection, config, configfile, NoSave
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from xml.etree.cElementTree import fromstring as cet_fromstring
from urllib2 import Request, urlopen, URLError, HTTPError
from twisted.web.client import downloadPage
from time import localtime, strftime
from enigma import eTimer, ePoint
from enigma import getDesktop
from os import system, environ
from datetime import date
import os, math, gettext
import datetime, time

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("WeatherMSN", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/WeatherMSN/locale"))

def _(txt):
	t = gettext.dgettext("WeatherMSN", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

config.plugins.weathermsn = ConfigSubsection()
config.plugins.weathermsn.menu = ConfigSelection(default="no", choices = [
	("no", _("no")),
	("yes", _("yes"))])
config.plugins.weathermsn.converter = ConfigSelection(default="no", choices = [
	("no", _("no")),
	("yes", _("yes"))])
config.plugins.weathermsn.city = ConfigText(default="Moscow,Moscow-City,Russia", visible_width = 250, fixed_size = False)
config.plugins.weathermsn.windtype = ConfigSelection(default="ms", choices = [
	("ms", _("m/s")),
	("fts", _("ft/s")),
	("kmh", _("km/h")),
	("mph", _("mp/h")),
	("knots", _("knots"))])
config.plugins.weathermsn.degreetype = ConfigSelection(default="C", choices = [
	("C", _("Celsius")),
	("F", _("Fahrenheit"))])

if getDesktop(0).size().width() >= 1920: #FHD
	SKIN_MSN = """
		<screen name="WeatherMSN" position="60,55" size="1800,1000" title=" ">
			<eLabel position="900,10" size="3,930" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="10,430" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="10,720" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,240" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,480" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,720" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,950" size="1760,3" backgroundColor="#00555555" zPosition="1" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/logo.png" position="170,60" size="550,125" alphatest="blend" />
			<widget source="locationtxt" render="Label" position="20,230" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="timezonetxt" render="Label" position="20,350" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="latitudetxt" render="Label" position="20,270" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="longitudetxt" render="Label" position="20,310" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="pointtxt" render="Label" position="20,390" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="location" render="Label" position="320,230" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="timezone" render="Label" position="320,350" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="latitude" render="Label" position="320,270" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="longitude" render="Label" position="320,310" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="observationtime" render="Label" position="20,965" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="observationpoint" render="Label" position="320,390" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="attribution" render="Label" position="170,965" size="800,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />

			<widget source="sunrisetxt" render="Label" position="280,440" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="sunsettxt" render="Label" position="280,480" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="solsticetxt" render="Label" position="280,520" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonrisetxt" render="Label" position="280,560" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonsettxt" render="Label" position="280,600" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonlighttxt" render="Label" position="280,640" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="yulianday" render="Label" position="1070,965" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="sunrise" render="Label" position="630,440" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="sunset" render="Label" position="630,480" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="solstice" render="Label" position="630,520" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonrise" render="Label" position="630,560" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonset" render="Label" position="630,600" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moondist" render="Label" position="630,680" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonlight" render="Label" position="630,640" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonphase" render="Label" position="20,680" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="picmoon" position="100,530" size="90,90" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="280,740" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="feelsliketxt" render="Label" position="280,780" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="humiditytxt" render="Label" position="280,820" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="windtxt" render="Label" position="280,860" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature" render="Label" position="630,740" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="feelslike" render="Label" position="630,780" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext" render="Label" position="280,900" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="humidity" render="Label" position="630,820" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="wind" render="Label" position="530,860" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic" position="80,770" size="128,128" zPosition="2" alphatest="blend" />

<!--		<widget source="temperaturetxt" render="Label" position="250,525" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="250,550" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="250,475" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="250,500" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature0" render="Label" position="440,525" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext0" render="Label" position="20,575" size="570,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip0" render="Label" position="440,550" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date0" render="Label" position="440,500" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day0" render="Label" position="440,475" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic0" position="70,470" size="128,128" zPosition="2" alphatest="blend" />
-->
			<widget source="temperaturetxt" render="Label" position="1180,110" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,150" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,30" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,70" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature1" render="Label" position="1530,110" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext1" render="Label" position="1180,190" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip1" render="Label" position="1530,150" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date1" render="Label" position="1530,70" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day1" render="Label" position="1530,30" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic1" position="980,60" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,350" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,390" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,270" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,310" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature2" render="Label" position="1530,350" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext2" render="Label" position="1180,430" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip2" render="Label" position="1530,390" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date2" render="Label" position="1530,310" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day2" render="Label" position="1530,270" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic2" position="980,300" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,590" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,630" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,510" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,550" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature3" render="Label" position="1530,590" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext3" render="Label" position="1180,670" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip3" render="Label" position="1530,630" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date3" render="Label" position="1530,550" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day3" render="Label" position="1530,510" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic3" position="980,540" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,820" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,860" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,740" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,780" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature4" render="Label" position="1530,820" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext4" render="Label" position="1180,900" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip4" render="Label" position="1530,860" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date4" render="Label" position="1530,780" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day4" render="Label" position="1530,740" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic4" position="980,770" size="128,128" zPosition="2" alphatest="blend" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_menu.png" position="1660,965" size="40,20" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_epg.png" position="1720,965" size="40,20" alphatest="on" />
	</screen>"""
else: #HD
	SKIN_MSN = """
		<!-- WeatherMSN -->
		<screen name="WeatherMSN" position="40,55" size="1200,650" title=' ' >
			<eLabel position="600,10" size="3,590" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,270" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,460" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,160" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,310" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,460" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,610" size="1160,3" backgroundColor="#00555555" zPosition="1" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/logo.png" position="30,10" size="550,125" alphatest="blend" />
			<widget source="locationtxt" render="Label" position="20,140" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="timezonetxt" render="Label" position="20,215" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="latitudetxt" render="Label" position="20,165" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="longitudetxt" render="Label" position="20,190" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="pointtxt" render="Label" position="20,240" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="location" render="Label" position="90,140" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="timezone" render="Label" position="90,215" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="latitude" render="Label" position="90,165" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="longitude" render="Label" position="90,190" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="observationtime" render="Label" position="20,620" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="observationpoint" render="Label" position="90,240" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="attribution" render="Label" position="120,620" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />

			<widget source="sunrisetxt" render="Label" position="250,275" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="sunsettxt" render="Label" position="250,300" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="solsticetxt" render="Label" position="250,325" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonrisetxt" render="Label" position="250,350" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonsettxt" render="Label" position="250,375" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonlighttxt" render="Label" position="250,400" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="yulianday" render="Label" position="760,620" size="300,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="sunrise" render="Label" position="440,275" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="sunset" render="Label" position="440,300" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="solstice" render="Label" position="440,325" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonrise" render="Label" position="440,350" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonset" render="Label" position="440,375" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moondist" render="Label" position="440,425" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonlight" render="Label" position="440,400" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonphase" render="Label" position="20,425" size="430,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="picmoon" position="90,315" size="90,90" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="250,475" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="feelsliketxt" render="Label" position="250,500" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="humiditytxt" render="Label" position="250,525" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="windtxt" render="Label" position="250,550" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature" render="Label" position="440,475" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="feelslike" render="Label" position="440,500" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext" render="Label" position="20,575" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="humidity" render="Label" position="440,525" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="wind" render="Label" position="300,550" size="290,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic" position="70,470" size="128,128" zPosition="2" alphatest="blend" />

<!--		<widget source="temperaturetxt" render="Label" position="250,525" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="250,550" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="250,475" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="250,500" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature0" render="Label" position="440,525" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext0" render="Label" position="20,575" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip0" render="Label" position="440,550" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date0" render="Label" position="440,500" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day0" render="Label" position="440,475" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic0" position="70,470" size="128,128" zPosition="2" alphatest="blend" />
-->
			<widget source="temperaturetxt" render="Label" position="840,75" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="840,100" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="840,25" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="840,50" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature1" render="Label" position="1030,75" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext1" render="Label" position="610,125" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip1" render="Label" position="1030,100" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date1" render="Label" position="1030,50" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day1" render="Label" position="1030,25" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic1" position="660,20" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="840,225" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="840,250" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="840,175" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="840,200" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature2" render="Label" position="1030,225" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext2" render="Label" position="610,275" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip2" render="Label" position="1030,250" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date2" render="Label" position="1030,200" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day2" render="Label" position="1030,175" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic2" position="660,170" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="840,375" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="840,400" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="840,325" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="840,350" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature3" render="Label" position="1030,375" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext3" render="Label" position="610,425" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip3" render="Label" position="1030,400" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date3" render="Label" position="1030,350" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day3" render="Label" position="1030,325" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic3" position="660,320" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="840,525" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="840,550" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="840,475" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="840,500" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature4" render="Label" position="1030,525" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext4" render="Label" position="610,575" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip4" render="Label" position="1030,550" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date4" render="Label" position="1030,500" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day4" render="Label" position="1030,475" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic4" position="660,470" size="128,128" zPosition="2" alphatest="blend" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_menu.png" position="1080,620" size="40,20" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_epg.png" position="1130,620" size="40,20" alphatest="on" />
		</screen>"""

class WeatherMSN(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_MSN

		self.time_update = 30
		self.language = config.osd.language.value.replace('_', '-')
		if self.language == 'en-EN':
			self.language = 'en-US'
		self.city = config.plugins.weathermsn.city.value
		self.degreetype = config.plugins.weathermsn.degreetype.value
		self.windtype = config.plugins.weathermsn.windtype.value

		self.yulianday = {'Julianday':''}
		self.sunrise = {'Sunrise':''}
		self.sunset = {'Sunset':''}
		self.solstice = {'Solstice':''}
#		self.sunculmination = {'Solstice':''}
		self.mercuryrise = {'Mercuryrise':''}
		self.mercuryset = {'Mercuryset':''}
		self.mercuryazimuth = {'Mercuryazimuth':''}
		self.venusrise = {'Venusrise':''}
		self.venusset = {'Venusset':''}
		self.venusazimuth = {'Venusazimuth':''}
		self.marsrise = {'Marsrise':''}
		self.marsset = {'Marsset':''}
		self.marsazimuth = {'Marsazimuth':''}
		self.jupiterrise = {'Jupiterrise':''}
		self.jupiterset = {'Jupiterset':''}
		self.jupiterazimuth = {'Jupiterazimuth':''}
		self.saturnrise = {'Saturnrise':''}
		self.saturnset = {'Saturnset':''}
		self.saturnazimuth = {'Saturnazimuth':''}
		self.uranusrise = {'Uranusrise':''}
		self.uranusset = {'Uranusset':''}
		self.uranusazimuth = {'Uranusazimuth':''}
		self.neptunerise = {'Neptunerise':''}
		self.neptuneset = {'Neptuneset':''}
		self.neptuneazimuth = {'Neptuneazimuth':''}
		self.moonrise = {'Moonrise':''}
		self.moonset = {'Moonset':''}
		self.moondist = {'Moondist':''}
		self.moonazimuth = {'Moonazimuth':''}
		self.moonphase = {'Moonphase':''}
		self.moonlight = {'Moonlight':''}
		self.picmoon = {'PicMoon':''}

		self.location = {'Location':''}
		self.timezone = {'Timezone':''}
		self.latitude = {'Latitude':''}
		self.longitude = {'Longitude':''}
		self.observationtime = {'Time':''}
		self.observationpoint = {'Point':''}
		self.attribution = {'Attribution':''}
		self.temperature = {'Temperature':''}
		self.feelslike = {'Feelslike':''}
		self.skytext = {'Skytext':''}
		self.humidity = {'Humidity':''}
		self.wind = {'Wind':''}
		self.windspeed = {'Windspeed':''}
		self.pic = {'Pic':''}

		self.lowtemp0 = {'Lowtemp0':''}
		self.hightemp0 = {'Hightemp0':''}
		self.skytext0 = {'Skytext0':''}
		self.precip0 = {'Precip0':''}
		self.date0 = {'Date0':''}
		self.day0 = {'Day0':''}
		self.pic0 = {'Pic0':''}

		self.lowtemp1 = {'Lowtemp1':''}
		self.hightemp1 = {'Hightemp1':''}
		self.skytext1 = {'Skytext1':''}
		self.precip1 = {'Precip1':''}
		self.date1 = {'Date1':''}
		self.day1 = {'Day1':''}
		self.pic1 = {'Pic1':''}

		self.lowtemp2 = {'Lowtemp2':''}
		self.hightemp2 = {'Hightemp2':''}
		self.skytext2 = {'Skytext2':''}
		self.precip2 = {'Precip2':''}
		self.date2 = {'Date2':''}
		self.day2 = {'Day2':''}
		self.pic2 = {'Pic2':''}

		self.lowtemp3 = {'Lowtemp3':''}
		self.hightemp3 = {'Hightemp3':''}
		self.skytext3 = {'Skytext3':''}
		self.precip3 = {'Precip3':''}
		self.date3 = {'Date3':''}
		self.day3 = {'Day3':''}
		self.pic3 = {'Pic3':''}

		self.lowtemp4 = {'Lowtemp4':''}
		self.hightemp4 = {'Hightemp4':''}
		self.skytext4 = {'Skytext4':''}
		self.precip4 = {'Precip4':''}
		self.date4 = {'Date4':''}
		self.day4 = {'Day4':''}
		self.pic4 = {'Pic4':''}

		self["shortcuts"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions", "EPGSelectActions"], 
		{ "cancel": self.exit,
		"menu": self.config,
		"info": self.about,
		}, -1)

		self.forecast = []
		self.forecastdata = {}
		self["Title"] = StaticText(_("Weather MSN"))

		self["yuliandaytxt"] = StaticText(_("Julian day:"))
		self["sunrisetxt"] = StaticText(_("Sunrise:"))
		self["sunsettxt"] = StaticText(_("Sunset:"))
		self["solsticetxt"] = StaticText(_("Solstice:"))
#		self["sunculminationtxt"] = StaticText(_("Solstice:"))
		self["mercuryrisetxt"] = StaticText(_("Mercuryrise:"))
		self["mercurysettxt"] = StaticText(_("Mercuryset:"))
		self["mercuryazimuthtxt"] = StaticText(_("Mercury azimuth:"))
		self["venusrisetxt"] = StaticText(_("Venusrise:"))
		self["venussettxt"] = StaticText(_("Venusset:"))
		self["venusazimuthtxt"] = StaticText(_("Venus azimuth:"))
		self["marsrisetxt"] = StaticText(_("Marsrise:"))
		self["marssettxt"] = StaticText(_("Marsset:"))
		self["marsazimuthtxt"] = StaticText(_("Mars azimuth:"))
		self["jupiterrisetxt"] = StaticText(_("Jupiterrise:"))
		self["jupitersettxt"] = StaticText(_("Jupiterset:"))
		self["jupiterazimuthtxt"] = StaticText(_("Jupiter azimuth:"))
		self["saturnrisetxt"] = StaticText(_("Saturnrise:"))
		self["saturnsettxt"] = StaticText(_("Saturnset:"))
		self["saturnazimuthtxt"] = StaticText(_("Saturn azimuth:"))
		self["uranusrisetxt"] = StaticText(_("Uranusrise:"))
		self["uranussettxt"] = StaticText(_("Uranusset:"))
		self["uranusazimuthtxt"] = StaticText(_("Uranus azimuth:"))
		self["neptunerisetxt"] = StaticText(_("Neptunerise:"))
		self["neptunesettxt"] = StaticText(_("Neptuneset:"))
		self["neptuneazimuthtxt"] = StaticText(_("Neptune azimuth:"))
		self["moondisttxt"] = StaticText(_("Moon distance:"))
		self["moonazimuthtxt"] = StaticText(_("Moon azimutht:"))
		self["moonrisetxt"] = StaticText(_("Moonrise:"))
		self["moonsettxt"] = StaticText(_("Moonset:"))
		self["moonlighttxt"] = StaticText(_("Moonlight:"))

		self["yulianday"] = StaticText()
		self["sunrise"] = StaticText()
		self["sunset"] = StaticText()
		self["solstice"] = StaticText()
#		self["sunculmination"] = StaticText()
		self["mercuryrise"] = StaticText()
		self["mercuryset"] = StaticText()
		self["mercuryazimuth"] = StaticText()
		self["venusrise"] = StaticText()
		self["venusset"] = StaticText()
		self["venusazimuth"] = StaticText()
		self["marsrise"] = StaticText()
		self["marsset"] = StaticText()
		self["marsazimuth"] = StaticText()
		self["jupiterrise"] = StaticText()
		self["jupiterset"] = StaticText()
		self["jupiterazimuth"] = StaticText()
		self["saturnrise"] = StaticText()
		self["saturnset"] = StaticText()
		self["saturnazimuth"] = StaticText()
		self["uranusrise"] = StaticText()
		self["uranusset"] = StaticText()
		self["uranusazimuth"] = StaticText()
		self["neptunerise"] = StaticText()
		self["neptuneset"] = StaticText()
		self["neptuneazimuth"] = StaticText()
		self["moondist"] = StaticText()
		self["moonazimuth"] = StaticText()
		self["moonrise"] = StaticText()
		self["moonset"] = StaticText()
		self["moonphase"] = StaticText()
		self["moonlight"] = StaticText()
		self["picmoon"] = Pixmap()

		self["locationtxt"] = StaticText(_("Location:"))
		self["timezonetxt"] = StaticText(_("Timezone:"))
		self["latitudetxt"] = StaticText(_("Latitude:"))
		self["longitudetxt"] = StaticText(_("Longitude:"))
		self["temperaturetxt"] = StaticText(_("Temperature:"))
		self["feelsliketxt"] = StaticText(_("Feels like:"))
		self["humiditytxt"] = StaticText(_("Humidity:"))
		self["preciptxt"] = StaticText(_("Chance precip:"))
		self["windtxt"] = StaticText(_("Wind:"))
		self["pointtxt"] = StaticText(_("Observation point:"))
		self["datetxt"] = StaticText(_("Date:"))
		self["daytxt"] = StaticText(_("Day week:"))

		self["location"] = StaticText()
		self["timezone"] = StaticText()
		self["latitude"] = StaticText()
		self["longitude"] = StaticText()
		self["observationtime"] = StaticText()
		self["observationpoint"] = StaticText()
		self["attribution"] = StaticText()
		self["temperature"] = StaticText()
		self["feelslike"] = StaticText()
		self["skytext"] = StaticText()
		self["humidity"] = StaticText()
		self["wind"] = StaticText()
		self["pic"] = Pixmap()

		self["temperature0"] = StaticText()
		self["skytext0"] = StaticText()
		self["precip0"] = StaticText()
		self["date0"] = StaticText()
		self["day0"] = StaticText()
		self["pic0"] = Pixmap()

		self["temperature1"] = StaticText()
		self["skytext1"] = StaticText()
		self["precip1"] = StaticText()
		self["date1"] = StaticText()
		self["day1"] = StaticText()
		self["pic1"] = Pixmap()

		self["temperature2"] = StaticText()
		self["skytext2"] = StaticText()
		self["precip2"] = StaticText()
		self["date2"] = StaticText()
		self["day2"] = StaticText()
		self["pic2"] = Pixmap()

		self["temperature3"] = StaticText()
		self["skytext3"] = StaticText()
		self["precip3"] = StaticText()
		self["date3"] = StaticText()
		self["day3"] = StaticText()
		self["pic3"] = Pixmap()

		self["temperature4"] = StaticText()
		self["skytext4"] = StaticText()
		self["precip4"] = StaticText()
		self["date4"] = StaticText()
		self["day4"] = StaticText()
		self["pic4"] = Pixmap()

		self.notdata = False
		self.onShow.append(self.get_weather_data)

	def get_xmlfile(self):
#		xmlfile = "http://weather.service.msn.com/data.aspx?weadegreetype=C&culture=ru-RU&weasearchstr=Moscow,Moscow-City,Russia&src=outlook"
		xmlfile = "http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook" % (self.degreetype, self.language, self.city)
		downloadPage(xmlfile, "/tmp/weathermsn1.xml").addCallback(self.downloadFinished).addErrback(self.downloadFailed)

	def downloadFinished(self, result):
		print "[WeatherMSN] Download finished"
		self.notdata = False
		self.parse_weather_data()

	def downloadFailed(self, result):
		self.notdata = True
		print "[WeatherMSN] Download failed!"

	def get_weather_data(self):
		if not os.path.exists("/tmp/weathermsn1.xml") or int((time.time() - os.stat("/tmp/weathermsn1.xml").st_mtime)/60) >= self.time_update or self.notdata:
			self.get_xmlfile()
		else:
			self.parse_weather_data()

	def parse_weather_data(self):
		self.forecast = []
		for line in open("/tmp/weathermsn1.xml"):
			try:
				if "<weather" in line:
					self.location['Location'] = line.split('weatherlocationname')[1].split('"')[1].split(',')[0]
					if not line.split('timezone')[1].split('"')[1][0] is '0':
						timezone = '%s' % (float(line.split('timezone')[1].split('"')[1]) - 1)
						self.timezone['Timezone'] = '+' + line.split('timezone')[1].split('"')[1]
					else:
						timezone = '%s' % (float(line.split('timezone')[1].split('"')[1]) - 1)
						self.timezone['Timezone'] = line.split('timezone')[1].split('"')[1]
					self.latitude['Latitude'] = latitude = line.split(' lat')[1].split('"')[1].replace(',', '.')
					self.longitude['Longitude'] = longitude = line.split(' long')[1].split('"')[1].replace(',', '.')
					self.observationtime['Time'] = line.split('observationtime')[1].split('"')[1]
					self.observationpoint['Point'] = line.split('observationpoint')[1].split('"')[1]
					self.attribution['Attribution'] = line.split('attribution')[1].split('"')[1]
				if "<current" in line:
					if not line.split('temperature')[1].split('"')[1][0] is '-' and not line.split('temperature')[1].split('"')[1][0] is '0':
						self.temperature['Temperature'] = '+' + line.split('temperature')[1].split('"')[1]
					else:
						self.temperature['Temperature'] = line.split('temperature')[1].split('"')[1]
					if not line.split('feelslike')[1].split('"')[1][0] is '-' and not line.split('feelslike')[1].split('"')[1][0] is '0':
						self.feelslike['Feelslike'] = '+' + line.split('feelslike')[1].split('"')[1]
					else:
						self.feelslike['Feelslike'] = line.split('feelslike')[1].split('"')[1]
					self.pic['Pic'] = line.split('skycode')[1].split('"')[1]
					self.skytext['Skytext'] = line.split('skytext')[1].split('"')[1]
					self.humidity['Humidity'] = line.split('humidity')[1].split('"')[1]
					try:
						self.wind['Wind'] = line.split('winddisplay')[1].split('"')[1].split(' ')[2]
					except:
						pass
# m/s
					if self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						self.windspeed['Windspeed'] = _('%s m/s') % line.split('windspeed')[1].split('"')[1].split(' ')[0]
					elif self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						self.windspeed['Windspeed'] = _('%.01f m/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.28)
					elif self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						self.windspeed['Windspeed'] = _('%.01f m/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.45)
# ft/s
					elif self.windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						self.windspeed['Windspeed']= _('%.01f ft/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 3.28)
					elif self.windtype == 'fts' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						self.windspeed['Windspeed']= _('%.01f ft/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.91)
					elif self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						self.windspeed['Windspeed'] = _('%.01f ft/s') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.47)
# mp/h
					elif self.windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						self.windspeed['Windspeed'] = _('%.01f mp/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 2.24)
					elif self.windtype == 'mph' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						self.windspeed['Windspeed'] = _('%.01f mp/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.62)
					elif self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						self.windspeed['Windspeed'] =  _('%s mp/h') % line.split('windspeed')[1].split('"')[1].split(' ')[0]
# knots
					elif self.windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						self.windspeed['Windspeed'] = _('%.01f knots') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.94)
					elif self.windtype == 'knots' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						self.windspeed['Windspeed'] = _('%.01f knots') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.54)
					elif self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						self.windspeed['Windspeed'] = _('%.01f knots') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 0.87)
# km/h
					elif self.windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'm/s':
						self.windspeed['Windspeed'] = _('%.01f km/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 3.6)
					elif self.windtype == 'kmh' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'km/h':
						self.windspeed['Windspeed'] = _('%s km/h') % line.split('windspeed')[1].split('"')[1].split(' ')[0]
					elif self.windtype == 'ms' and line.split('windspeed')[1].split('"')[1].split(' ')[1] == 'mph':
						self.windspeed['Windspeed'] = _('%.01f km/h') % (float(line.split('windspeed')[1].split('"')[1].split(' ')[0]) * 1.61)
# День 0
				if "<forecast" in line:
					if not line.split('low')[1].split('"')[1][0] is '-' and not line.split('low')[1].split('"')[1][0] is '0':
						self.lowtemp0['Lowtemp0'] = '+' + line.split('low')[1].split('"')[1]
					else:
						self.lowtemp0['Lowtemp0'] = line.split('low')[1].split('"')[1]
					if not line.split('high')[1].split('"')[1][0] is '-' and not line.split('high')[1].split('"')[1][0] is '0':
						self.hightemp0['Hightemp0'] = '+' + line.split('high')[1].split('"')[1]
					else:
						self.hightemp0['Hightemp0'] = line.split('high')[1].split('"')[1]
					self.pic0['Pic0'] = line.split('skycodeday')[1].split('"')[1]
					self.date0['Date0'] = line.split('date')[2].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[0].strip()
					self.day0['Day0'] = line.split(' day')[2].split('"')[1]
					self.skytext0['Skytext0'] = line.split('skytextday')[1].split('"')[1]
					self.precip0['Precip0'] = line.split('precip')[1].split('"')[1]
# День 1
				if "<forecast" in line:
					if not line.split('low')[2].split('"')[1][0] is '-' and not line.split('low')[2].split('"')[1][0] is '0':
						self.lowtemp1['Lowtemp1'] = '+' + line.split('low')[2].split('"')[1]
					else:
						self.lowtemp1['Lowtemp1'] = line.split('low')[2].split('"')[1]
					if not line.split('high')[2].split('"')[1][0] is '-' and not line.split('high')[2].split('"')[1][0] is '0':
						self.hightemp1['Hightemp1'] = '+' + line.split('high')[2].split('"')[1]
					else:
						self.hightemp1['Hightemp1'] = line.split('high')[2].split('"')[1]
					self.pic1['Pic1'] = line.split('skycodeday')[2].split('"')[1]
					self.date1['Date1'] = line.split('date')[3].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[0].strip()
					self.day1['Day1'] = line.split(' day')[3].split('"')[1]
					self.skytext1['Skytext1'] = line.split('skytextday')[2].split('"')[1]
					self.precip1['Precip1'] = line.split('precip')[2].split('"')[1]
# День 2
				if "<forecast" in line:
					if not line.split('low')[3].split('"')[1][0] is '-' and not line.split('low')[3].split('"')[1][0] is '0':
						self.lowtemp2['Lowtemp2'] = '+' + line.split('low')[3].split('"')[1]
					else:
						self.lowtemp2['Lowtemp2'] = line.split('low')[3].split('"')[1]
					if not line.split('high')[3].split('"')[1][0] is '-' and not line.split('high')[3].split('"')[1][0] is '0':
						self.hightemp2['Hightemp2'] = '+' + line.split('high')[3].split('"')[1]
					else:
						self.hightemp2['Hightemp2'] = line.split('high')[3].split('"')[1]
					self.pic2['Pic2'] = line.split('skycodeday')[3].split('"')[1]
					self.date2['Date2'] = line.split('date')[4].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[0].strip()
					self.day2['Day2'] = line.split(' day')[4].split('"')[1]
					self.skytext2['Skytext2'] = line.split('skytextday')[3].split('"')[1]
					self.precip2['Precip2'] = line.split('precip')[3].split('"')[1]
# День 3
				if "<forecast" in line:
					if not line.split('low')[4].split('"')[1][0] is '-' and not line.split('low')[4].split('"')[1][0] is '0':
						self.lowtemp3['Lowtemp3'] = '+' + line.split('low')[4].split('"')[1]
					else:
						self.lowtemp3['Lowtemp3'] = line.split('low')[4].split('"')[1]
					if not line.split('high')[4].split('"')[1][0] is '-' and not line.split('high')[4].split('"')[1][0] is '0':
						self.hightemp3['Hightemp3'] = '+' + line.split('high')[4].split('"')[1]
					else:
						self.hightemp3['Hightemp3'] = line.split('high')[4].split('"')[1]
					self.pic3['Pic3'] = line.split('skycodeday')[4].split('"')[1]
					self.date3['Date3'] = line.split('date')[5].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[0].strip()
					self.day3['Day3'] = line.split(' day')[5].split('"')[1]
					self.skytext3['Skytext3'] = line.split('skytextday')[4].split('"')[1]
					self.precip3['Precip3'] = line.split('precip')[4].split('"')[1]
# День 4
				if "<forecast" in line:
					if not line.split('low')[5].split('"')[1][0] is '-' and not line.split('low')[5].split('"')[1][0] is '0':
						self.lowtemp4['Lowtemp4'] = '+' + line.split('low')[5].split('"')[1]
					else:
						self.lowtemp4['Lowtemp4'] = line.split('low')[5].split('"')[1]
					if not line.split('high')[5].split('"')[1][0] is '-' and not line.split('high')[5].split('"')[1][0] is '0':
						self.hightemp4['Hightemp4'] = '+' + line.split('high')[5].split('"')[1]
					else:
						self.hightemp4['Hightemp4'] = line.split('high')[5].split('"')[1]
					self.pic4['Pic4'] = line.split('skycodeday')[5].split('"')[1]
					self.date4['Date4'] = line.split('date')[6].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[0].strip()
					self.day4['Day4'] = line.split(' day')[6].split('"')[1]
					self.skytext4['Skytext4'] = line.split('skytextday')[5].split('"')[1]
					self.precip4['Precip4'] = line.split('precip')[5].split('"')[1]
			except:
				pass
# Астро
		PI = 3.14159265359
		DEG2RAD = PI / 180 # радианы
		RAD2DEG = 180 / PI # градусы
		year = float(strftime('%Y'))
		month = float(strftime('%m'))
		day = float(strftime('%d'))
		hour = float(strftime('%H'))
		min = float(strftime('%M'))
		sec = float(strftime('%S'))
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
#		FM = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T - T * T * T / 3526000 + T * T * T * T / 863310000 # ср аргумент широты луны
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср элонгация луны
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
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср элонгация луны
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
			self.yulianday['Julianday'] = JD
			self.sunrise['Sunrise'] = '%s%s%s%s' % (SRh, unichr(58).encode("latin-1"), SRx, SRm)
			self.sunset['Sunset'] = '%s%s%s%s' % (SSh, unichr(58).encode("latin-1"), SSx, SSm)
			self.solstice['Solstice'] = '%s%s%s%s' % (SCh, unichr(58).encode("latin-1"), SCx, SCm)

			self.moondist['Moondist'] = _('%s km') % Mdist
			self.moonazimuth['Moonazimuth'] = '%s %s' % (Mazim, unichr(176).encode("latin-1"))
			self.moonrise['Moonrise'] = '%s%s%s%s' % (MRh, unichr(58).encode("latin-1"), MRx, MRm)
			self.moonset['Moonset'] = '%s%s%s%s' % (MSh, unichr(58).encode("latin-1"), MSx, MSm)
			self.moonphase['Moonphase'] = '%s' % phase
			self.moonlight['Moonlight'] = '%s %s' % (light, unichr(37).encode("latin-1"))
			self.picmoon['PicMoon'] = '%s' % pic
		except:
			pass
			self.picmoon['PicMoon'] = '1'
		self.get_widgets()

	def get_widgets(self):
		defpic = "%sExtensions/WeatherMSN/icons/weather/na.png" % resolveFilename(SCOPE_PLUGINS)
		if self.location['Location'] is not '':
			self["location"].text = _('%s') % self.location['Location']
		else:
			self["location"].text = _('n/a')
			self.notdata = True
		if self.timezone['Timezone'] is not '':
			self["timezone"].text = _('%s h') % self.timezone['Timezone']
		else:
			self["timezone"].text = _('n/a')
			self.notdata = True
		if self.latitude['Latitude'] is not '':
			self["latitude"].text = _('%s') % self.latitude['Latitude']
		else:
			self["latitude"].text = _('n/a')
			self.notdata = True
		if self.longitude['Longitude'] is not '':
			self["longitude"].text = _('%s') % self.longitude['Longitude']
		else:
			self["longitude"].text = _('n/a')
			self.notdata = True
		if self.observationtime['Time'] is not '':
			self["observationtime"].text = _('%s') % self.observationtime['Time']
		else:
			self["observationtime"].text = _('n/a')
			self.notdata = True
		if self.observationpoint['Point'] is not '':
			self["observationpoint"].text = _('%s') % self.observationpoint['Point']
		else:
			self["observationpoint"].text = _('n/a')
			self.notdata = True
		if self.attribution['Attribution'] is not '':
			self["attribution"].text = _('%s') % self.attribution['Attribution']
		else:
			self["attribution"].text = _('n/a')
			self.notdata = True
		if self.temperature['Temperature'] is not '':
			self["temperature"].text = _('%s%s%s') % (self.temperature['Temperature'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature"].text = _('n/a')
			self.notdata = True
		if self.feelslike['Feelslike'] is not '':
			self["feelslike"].text = _('%s%s%s') % (self.feelslike['Feelslike'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["feelslike"].text = _('n/a')
			self.notdata = True
		if self.skytext['Skytext'] is not '':
			self["skytext"].text = _('%s') % self.skytext['Skytext']
		else:
			self["skytext"].text = _('n/a')
			self.notdata = True
		if self.humidity['Humidity'] is not '':
			self["humidity"].text = _('%s %s') % (self.humidity['Humidity'], unichr(37).encode("latin-1"))
		else:
			self["humidity"].text = _('n/a')
			self.notdata = True
		if self.windspeed['Windspeed'] is not '':
			self["wind"].text = _('%s %s %s') % (self.wind['Wind'], unichr(126).encode("latin-1"), self.windspeed['Windspeed'])
		else:
			self["wind"].text = _('n/a')
			self.notdata = True
		self["pic"].instance.setScale(1)
		if self.pic['Pic'] is not '':
			self["pic"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/weather/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic['Pic']))
		else:
			self["pic"].instance.setPixmapFromFile(defpic)
		self["pic"].instance.show()
# День 0
		if self.lowtemp0['Lowtemp0'] is not '' and self.hightemp0['Hightemp0'] is not '':
			self["temperature0"].text = _('%s%s%s / %s%s%s') % (self.hightemp0['Hightemp0'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp0['Lowtemp0'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature0"].text = _('n/a')
			self.notdata = True
		if self.skytext0['Skytext0'] is not '':
			self["skytext0"].text = _('%s') % self.skytext0['Skytext0']
		else:
			self["skytext0"].text = _('n/a')
			self.notdata = True
		if self.precip0['Precip0'] is not '':
			self["precip0"].text = _('%s %s') % (self.precip0['Precip0'], unichr(37).encode("latin-1"))
		else:
			self["precip0"].text = _('n/a')
			self.notdata = True
		if self.date0['Date0'] is not '':
			self["date0"].text = _('%s') % self.date0['Date0']
		else:
			self["date0"].text = _('n/a')
			self.notdata = True
		if self.day0['Day0'] is not '':
			self["day0"].text = _('%s') % self.day0['Day0']
		else:
			self["day0"].text = _('n/a')
			self.notdata = True
		self["pic0"].instance.setScale(1)
		if self.pic0['Pic0'] is not '':
			self["pic0"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/weather/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic0['Pic0']))
		else:
			self["pic0"].instance.setPixmapFromFile(defpic)
		self["pic0"].instance.show()
# День 1
		if self.lowtemp1['Lowtemp1'] is not '' and self.hightemp1['Hightemp1'] is not '':
			self["temperature1"].text = _('%s%s%s / %s%s%s') % (self.hightemp1['Hightemp1'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp1['Lowtemp1'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature1"].text = _('n/a')
			self.notdata = True
		if self.skytext1['Skytext1'] is not '':
			self["skytext1"].text = _('%s') % self.skytext1['Skytext1']
		else:
			self["skytext1"].text = _('n/a')
			self.notdata = True
		if self.precip1['Precip1'] is not '':
			self["precip1"].text = _('%s %s') % (self.precip1['Precip1'], unichr(37).encode("latin-1"))
		else:
			self["precip1"].text = _('n/a')
			self.notdata = True
		if self.date1['Date1'] is not '':
			self["date1"].text = _('%s') % self.date1['Date1']
		else:
			self["date1"].text = _('n/a')
			self.notdata = True
		if self.day1['Day1'] is not '':
			self["day1"].text = _('%s') % self.day1['Day1']
		else:
			self["day1"].text = _('n/a')
			self.notdata = True
		self["pic1"].instance.setScale(1)
		if self.pic1['Pic1'] is not '':
			self["pic1"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/weather/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic1['Pic1']))
		else:
			self["pic1"].instance.setPixmapFromFile(defpic)
		self["pic1"].instance.show()
# День 2
		if self.lowtemp2['Lowtemp2'] is not '' and self.hightemp2['Hightemp2'] is not '':
			self["temperature2"].text = _('%s%s%s / %s%s%s') % (self.hightemp2['Hightemp2'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp2['Lowtemp2'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature2"].text = _('n/a')
			self.notdata = True
		if self.skytext2['Skytext2'] is not '':
			self["skytext2"].text = _('%s') % self.skytext2['Skytext2']
		else:
			self["skytext2"].text = _('n/a')
			self.notdata = True
		if self.precip2['Precip2'] is not '':
			self["precip2"].text = _('%s %s') % (self.precip2['Precip2'], unichr(37).encode("latin-1"))
		else:
			self["precip2"].text = _('n/a')
			self.notdata = True
		if self.date2['Date2'] is not '':
			self["date2"].text = _('%s') % self.date2['Date2']
		else:
			self["date2"].text = _('n/a')
			self.notdata = True
		if self.day2['Day2'] is not '':
			self["day2"].text = _('%s') % self.day2['Day2']
		else:
			self["day2"].text = _('n/a')
			self.notdata = True
		self["pic2"].instance.setScale(1)
		if self.pic2['Pic2'] is not '':
			self["pic2"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/weather/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic2['Pic2']))
		else:
			self["pic2"].instance.setPixmapFromFile(defpic)
		self["pic2"].instance.show()
# День 3
		if self.lowtemp3['Lowtemp3'] is not '' and self.hightemp3['Hightemp3'] is not '':
			self["temperature3"].text = _('%s%s%s / %s%s%s') % (self.hightemp3['Hightemp3'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp3['Lowtemp3'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature3"].text = _('n/a')
			self.notdata = True
		if self.skytext3['Skytext3'] is not '':
			self["skytext3"].text = _('%s') % self.skytext3['Skytext3']
		else:
			self["skytext3"].text = _('n/a')
			self.notdata = True
		if self.precip3['Precip3'] is not '':
			self["precip3"].text = _('%s %s') % (self.precip3['Precip3'], unichr(37).encode("latin-1"))
		else:
			self["precip3"].text = _('n/a')
			self.notdata = True
		if self.date3['Date3'] is not '':
			self["date3"].text = _('%s') % self.date3['Date3']
		else:
			self["date3"].text = _('n/a')
			self.notdata = True
		if self.day3['Day3'] is not '':
			self["day3"].text = _('%s') % self.day3['Day3']
		else:
			self["day3"].text = _('n/a')
			self.notdata = True
		self["pic3"].instance.setScale(1)
		if self.pic3['Pic3'] is not '':
			self["pic3"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/weather/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic3['Pic3']))
		else:
			self["pic3"].instance.setPixmapFromFile(defpic)
		self["pic3"].instance.show()
# День 4
		if self.lowtemp4['Lowtemp4'] is not '' and self.hightemp4['Hightemp4'] is not '':
			self["temperature4"].text = _('%s%s%s / %s%s%s') % (self.hightemp4['Hightemp4'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp4['Lowtemp4'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature4"].text = _('n/a')
			self.notdata = True
		if self.skytext4['Skytext4'] is not '':
			self["skytext4"].text = _('%s') % self.skytext4['Skytext4']
		else:
			self["skytext4"].text = _('n/a')
			self.notdata = True
		if self.precip4['Precip4'] is not '':
			self["precip4"].text = _('%s %s') % (self.precip4['Precip4'], unichr(37).encode("latin-1"))
		else:
			self["precip4"].text = _('n/a')
			self.notdata = True
		if self.date4['Date4'] is not '':
			self["date4"].text = _('%s') % self.date4['Date4']
		else:
			self["date4"].text = _('n/a')
			self.notdata = True
		if self.day4['Day4'] is not '':
			self["day4"].text = _('%s') % self.day4['Day4']
		else:
			self["day4"].text = _('n/a')
			self.notdata = True
		self["pic4"].instance.setScale(1)
		if self.pic4['Pic4'] is not '':
			self["pic4"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/weather/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic4['Pic4']))
		else:
			self["pic4"].instance.setPixmapFromFile(defpic)
		self["pic4"].instance.show()

		if self.yulianday['Julianday'] is not '':
			self["yulianday"].text = '%s' % self.yulianday['Julianday']
		else:
			self["yulianday"].text = _('n/a')
			self.notdata = True
		if self.sunrise['Sunrise'] is not '':
			self["sunrise"].text = '%s' % self.sunrise['Sunrise']
		else:
			self["sunrise"].text = _('n/a')
			self.notdata = True
		if self.sunset['Sunset'] is not '':
			self["sunset"].text = '%s' % self.sunset['Sunset']
		else:
			self["sunset"].text = _('n/a')
			self.notdata = True
		if self.solstice['Solstice'] is not '':
			self["solstice"].text = '%s' % self.solstice['Solstice']
		else:
			self["solstice"].text = _('n/a')
			self.notdata = True
		if self.moondist['Moondist'] is not '':
			self["moondist"].text = '%s' % self.moondist['Moondist']
		else:
			self["moondist"].text = _('n/a')
			self.notdata = True
		if self.moonrise['Moonrise'] is not '':
			self["moonrise"].text = '%s' % self.moonrise['Moonrise']
		else:
			self["moonrise"].text = _('n/a')
			self.notdata = True
		if self.moonset['Moonset'] is not '':
			self["moonset"].text = '%s' % self.moonset['Moonset']
		else:
			self["moonset"].text = _('n/a')
			self.notdata = True
		if self.moonphase['Moonphase'] is not '':
			self["moonphase"].text = '%s' % self.moonphase['Moonphase']
		else:
			self["moonphase"].text = _('n/a')
			self.notdata = True
		if self.moonlight['Moonlight'] is not '':
			self["moonlight"].text = '%s' % self.moonlight['Moonlight']
		else:
			self["moonlight"].text = _('n/a')
			self.notdata = True
		self["picmoon"].instance.setScale(1)
		if self.picmoon['PicMoon'] is not '':
			self["picmoon"].instance.setPixmapFromFile("%sExtensions/WeatherMSN/icons/moon/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.picmoon['PicMoon']))
		else:
			self["picmoon"].instance.setPixmapFromFile(defpic)
		self["picmoon"].instance.show()

	def config (self):
		self.session.open(ConfigWeatherMSN)

	def about(self):
		self.session.open(MessageBox, _("Weather MSN\nDeveloper: Sirius0103 \nHomepage: www.gisclub.tv \nGithub: www.github.com/Sirius0103 \n\nDonate:\nVISA 4276 4000 5465 0552"), MessageBox.TYPE_INFO)

	def exit(self):
		self.close()

if getDesktop(0).size().width() >= 1920: #FHD
	SKIN_CONF = """
		<!-- Config WeatherMSN -->
		<screen name="ConfigWeatherMSN" position="center,260" size="950,570" title=' '>
			<eLabel position="20,525" size="910,3" backgroundColor="#00555555" zPosition="1" />
			<widget name="config" position="20,20" size="910,500" scrollbarMode="showOnDemand" transparent="1" />
			<widget source="key_red" render="Label" position="80,535" size="220,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_green" render="Label" position="380,535" size="220,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_blue" render="Label" position="680,532" size="250,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_red.png" position="30,535" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_green.png" position="320,535" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_blue.png" position="620,535" size="40,20" alphatest="blend" />
			<widget name="HelpWindow" position="25,300" zPosition="1" size="1,1" backgroundColor="background" transparent="1" alphatest="blend" />
		</screen>"""
else: #HD
	SKIN_CONF = """
		<!-- Config WeatherMSN -->
		<screen name="ConfigWeatherMSN" position="center,160" size="750,370" title=' '>
			<eLabel position="20,325" size="710,3" backgroundColor="#00555555" zPosition="1" />
			<widget name="config" position="15,10" size="720,300" scrollbarMode="showOnDemand" transparent="1" />
			<widget source="key_red" render="Label" position="80,330" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_green" render="Label" position="310,330" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_blue" render="Label" position="540,330" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_red.png" position="30,335" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_green.png" position="260,335" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_blue.png" position="490,335" size="40,20" alphatest="blend" />
			<widget name="HelpWindow" position="25,300" zPosition="1" size="1,1" backgroundColor="background" transparent="1" alphatest="blend" />
		</screen>"""

class ConfigWeatherMSN(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_CONF
		self.list = []

		ConfigListScreen.__init__(self, self.list, session = session)

		self.setTitle(_("Config Weather MSN"))
		self.converterpath = "/usr/lib/enigma2/python/Components/Converter/"
		self.pluginpath = "/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/components/"
		self.city = config.plugins.weathermsn.city.value
		self.language = config.osd.language.value.replace('_', '-')
		if self.language == 'en-EN':
			self.language = 'en-US'
		self.degreetype = config.plugins.weathermsn.degreetype.value
		self.windtype = config.plugins.weathermsn.windtype.value
		self.converter = config.plugins.weathermsn.converter.value
		self.createSetup()

		self["setupActions"] = ActionMap(["DirectionActions", "SetupActions", "ColorActions"], 
		{ "red": self.cancel,
		"cancel": self.cancel,
		"green": self.save,
		"blue": self.openVirtualKeyBoard,
		"ok": self.save
		}, -2)

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["key_blue"] = StaticText(_("Search Location"))
		self["HelpWindow"] = Pixmap()

	def openVirtualKeyBoard(self):
		self.session.openWithCallback(self.ShowsearchBarracuda, VirtualKeyBoard, title=_('Enter text to search city'))

	def ShowsearchBarracuda(self, name):
		if name is not None:
			self.session.open(SearchLocationMSN, name)

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Show Weather MSN in menu information:"), config.plugins.weathermsn.menu))
		self.list.append(getConfigListEntry(_("Location:"), config.plugins.weathermsn.city))
		self.list.append(getConfigListEntry(_("Scale of wind speed:"), config.plugins.weathermsn.windtype))
		self.list.append(getConfigListEntry(_("Scale of temperature:"), config.plugins.weathermsn.degreetype))
		self.list.append(getConfigListEntry(_("Create converter in system:"), config.plugins.weathermsn.converter))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self["config"].onSelectionChanged.append(self.selectionChanged)

	def selectionChanged(self):
		current = self["config"].getCurrent()
		try:
			helpwindowpos = self["HelpWindow"].getPosition()
			if current[1].help_window.instance is not None:
				current[1].help_window.instance.move(ePoint(helpwindowpos[0],helpwindowpos[1]))
		except:
			pass

	def createConverter(self):
		os.system("cp %sMSNWeather2.py %sMSNWeather2.py" % (self.pluginpath, self.converterpath))

	def restart(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False)

	def save(self):
		os.system("rm -f /tmp/weathermsn1.xml")
		os.system("rm -f /tmp/weathermsn2.xml")
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		if config.plugins.weathermsn.converter.value == 'yes':
			self.createConverter()
			self.session.openWithCallback(self.restart, MessageBox,_("Do you want to restart the GUI now ?"), MessageBox.TYPE_YESNO)
		else:
			self.mbox = self.session.open(MessageBox,(_("Configuration is saved")), MessageBox.TYPE_INFO, timeout = 3)
			self.close()

if getDesktop(0).size().width() >= 1920: #FHD
	SKIN_LOC = """
		<!-- Search LocationMSN -->
		<screen name="SearchLocationMSN" position="center,260" size="950,570" title=" ">
			<widget name="menu" position="20,20" size="910,500" scrollbarMode="showOnDemand" transparent="1" />
		</screen>"""
else: #HD
	SKIN_LOC = """
		<!-- Search LocationMSN -->
		<screen name="SearchLocationMSN" position="center,160" size="750,370" title=" ">
			<widget name="menu" position="15,10" size="720,300" scrollbarMode="showOnDemand" transparent="1" />
		</screen>"""

class SearchLocationMSN(Screen):
	def __init__(self, session, name):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_LOC
		self.eventname = name
		self.resultlist = []
		self.setTitle(_("Search Location Weather MSN"))
		self["menu"] = MenuList(self.resultlist)

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], 
		{"ok": self.okClicked,
		"cancel": self.close,
		"up": self.pageUp,
		"down": self.pageDown
		}, -1)

		self.showMenu()

	def pageUp(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveUp)

	def pageDown(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveDown)

	def showMenu(self):
		try:
			results = search_title(self.eventname)
		except:
			results = []
		if len(results) == 0:
			return False
		self.resultlist = []
		for searchResult in results:
			try:
				self.resultlist.append(searchResult)
			except:
				pass
		self['menu'].l.setList(self.resultlist)

	def okClicked(self):
		id = self['menu'].getCurrent()
		if id:
			config.plugins.weathermsn.city.value = id.replace(', ', ',')
			config.plugins.weathermsn.city.save()
			self.close()

def search_title(id):
	url = "http://weather.service.msn.com/find.aspx?outputview=search&weasearchstr=%s&culture=en-US&src=outlook" % id
	watchrequest = Request(url)
	try:
		watchvideopage = urlopen(watchrequest)
	except (URLError, HTTPException, socket.error) as err:
		print "[Location] Error: Unable to retrieve page - Error code: ", str(err)
	content = watchvideopage.read()
	root = cet_fromstring(content)
	search_results = []
	if content:
		for childs in root:
			if childs.tag == 'weather':
				locationcode = childs.attrib.get('weatherlocationname').encode('utf-8', 'ignore')
				search_results.append(locationcode)
	return search_results

def WeatherMenu(menuid):
	if menuid != "information":
		return [ ]
	return [(_("Weather MSN"), openWeather, "Weather_MSN", None)]

def openWeather(session, **kwargs):
	session.open(WeatherMSN)

def main(session, **kwargs):
	session.open(WeatherMSN)

def Plugins(**kwargs):
	if config.plugins.weathermsn.menu.value == 'yes':
		result = [
		PluginDescriptor(name=_("Weather MSN"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=WeatherMenu),
		PluginDescriptor(name=_("Weather MSN"),
		description=_("Weather forecast for 5 days"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="plugin.png",
		fnc=main)
		]
		return result
	else:
		result = [
		PluginDescriptor(name=_("Weather MSN"),
		description=_("Weather forecast for 5 days"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="plugin.png",
		fnc=main)
		]
		return result
