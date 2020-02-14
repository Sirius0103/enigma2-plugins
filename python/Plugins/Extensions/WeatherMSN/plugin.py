# -*- coding: UTF-8 -*-
#
# Plugin - Weather MSN
# Developer - Sirius
# Patch Showsearch - Nikolasi
# Homepage - http://www.gisclub.tv
#
# Jean Meeus - Astronomical Algorithms
# Виктор Абалакин - Астрономический календарь
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
import urllib2
import datetime, time
import os, math, gettext
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
			<eLabel position="10,395" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,210" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,395" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,580" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="910,765" size="880,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,950" size="1760,3" backgroundColor="#00555555" zPosition="1" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/logo.png" position="170,60" size="550,125" alphatest="blend" />

			<widget source="locationtxt" render="Label" position="20,220" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="timezonetxt" render="Label" position="20,325" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="latitudetxt" render="Label" position="20,255" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="longitudetxt" render="Label" position="20,290" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="pointtxt" render="Label" position="20,360" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="location" render="Label" position="320,220" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="timezone" render="Label" position="320,325" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="latitude" render="Label" position="320,255" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="longitude" render="Label" position="320,290" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="observationtime" render="Label" position="20,965" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="observationpoint" render="Label" position="320,360" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="attribution" render="Label" position="170,965" size="800,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />

			<widget source="yulianday" render="Label" position="1070,965" size="560,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="risetxt" render="Label" position="210,415" size="170,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="settxt" render="Label" position="380,415" size="170,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="culminationtxt" render="Label" position="550,415" size="170,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="azimuthtxt" render="Label" position="720,415" size="170,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="suntxt" render="Label" position="20,450" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moontxt" render="Label" position="20,730" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="mercurytxt" render="Label" position="20,485" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="venustxt" render="Label" position="20,520" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="marstxt" render="Label" position="20,555" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="jupitertxt" render="Label" position="20,590" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="saturntxt" render="Label" position="20,625" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="uranustxt" render="Label" position="20,660" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="neptunetxt" render="Label" position="20,695" size="200,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonlighttxt" render="Label" position="280,800" size="350,30" font="Regular; 25" foregroundColor="unf4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moondisttxt" render="Label" position="280,835" size="350,30" font="Regular; 25" foregroundColor="unf4f4f4" backgroundColor="background" halign="left" transparent="1" />

			<widget source="sunrise" render="Label" position="220,450" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="sunset" render="Label" position="390,450" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="sunculmination" render="Label" position="560,450" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryrise" render="Label" position="220,485" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryset" render="Label" position="390,486" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryculmination" render="Label" position="560,485" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryazimuth" render="Label" position="730,485" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusset" render="Label" position="390,520" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusrise" render="Label" position="220,520" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusculmination" render="Label" position="560,520" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusazimuth" render="Label" position="730,520" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsrise" render="Label" position="220,555" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsset" render="Label" position="390,555" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsculmination" render="Label" position="560,555" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsazimuth" render="Label" position="730,555" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterrise" render="Label" position="220,590" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterset" render="Label" position="390,590" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterculmination" render="Label" position="560,590" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterazimuth" render="Label" position="730,590" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnrise" render="Label" position="220,625" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnset" render="Label" position="390,625" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnculmination" render="Label" position="560,625" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnazimuth" render="Label" position="730,625" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusrise" render="Label" position="220,660" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusset" render="Label" position="390,660" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusculmination" render="Label" position="560,660" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusazimuth" render="Label" position="730,660" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptunerise" render="Label" position="220,695" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptuneset" render="Label" position="390,695" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptuneculmination" render="Label" position="560,695" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptuneazimuth" render="Label" position="730,695" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonrise" render="Label" position="220,730" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonset" render="Label" position="390,730" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonculmination" render="Label" position="560,730" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moondist" render="Label" position="630,835" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonazimuth" render="Label" position="730,730" size="150,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonlight" render="Label" position="630,800" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonphase" render="Label" position="280,870" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="picmoon" position="100,810" size="90,90" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,35" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="feelsliketxt" render="Label" position="1180,70" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="humiditytxt" render="Label" position="1180,105" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="windtxt" render="Label" position="1180,140" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature" render="Label" position="1530,35" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="feelslike" render="Label" position="1530,70" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext" render="Label" position="1180,175" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="humidity" render="Label" position="1530,105" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="wind" render="Label" position="1430,140" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic" position="980,55" size="128,128" zPosition="2" alphatest="blend" />

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
			<widget source="temperaturetxt" render="Label" position="1180,290" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,325" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,220" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,255" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature1" render="Label" position="1530,290" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext1" render="Label" position="1180,360" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip1" render="Label" position="1530,325" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date1" render="Label" position="1530,255" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day1" render="Label" position="1530,220" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic1" position="980,240" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,475" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,510" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,405" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,440" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature2" render="Label" position="1530,475" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext2" render="Label" position="1180,545" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip2" render="Label" position="1530,510" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date2" render="Label" position="1530,440" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day2" render="Label" position="1530,405" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic2" position="980,425" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,660" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,695" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,590" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,625" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature3" render="Label" position="1530,660" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext3" render="Label" position="1180,730" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip3" render="Label" position="1530,695" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date3" render="Label" position="1530,625" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day3" render="Label" position="1530,590" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic3" position="980,615" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="1180,845" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="1180,880" size="350,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="1180,775" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="1180,810" size="300,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature4" render="Label" position="1530,845" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext4" render="Label" position="1180,915" size="600,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip4" render="Label" position="1530,880" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date4" render="Label" position="1530,810" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day4" render="Label" position="1530,775" size="250,30" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic4" position="980,795" size="128,128" zPosition="2" alphatest="blend" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_menu.png" position="1660,965" size="40,20" alphatest="on" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/buttons/key_epg.png" position="1720,965" size="40,20" alphatest="on" />
	</screen>"""
else: #HD
	SKIN_MSN = """
		<!-- WeatherMSN -->
		<screen name="WeatherMSN" position="40,55" size="1200,650" title=' ' >
			<eLabel position="600,10" size="3,590" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,250" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,130" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,250" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,370" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="610,490" size="570,3" backgroundColor="#00555555" zPosition="1" />
			<eLabel position="20,610" size="1160,3" backgroundColor="#00555555" zPosition="1" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/WeatherMSN/logo.png" position="30,10" size="550,125" alphatest="blend" />

			<widget source="locationtxt" render="Label" position="20,140" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="timezonetxt" render="Label" position="20,200" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="latitudetxt" render="Label" position="20,160" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="longitudetxt" render="Label" position="20,180" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="pointtxt" render="Label" position="20,220" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="location" render="Label" position="90,140" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="timezone" render="Label" position="90,200" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="latitude" render="Label" position="90,160" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="longitude" render="Label" position="90,180" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="observationtime" render="Label" position="20,620" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="observationpoint" render="Label" position="90,220" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="attribution" render="Label" position="120,620" size="500,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />

			<widget source="yulianday" render="Label" position="760,620" size="300,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="risetxt" render="Label" position="125,260" size="170,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="settxt" render="Label" position="230,260" size="170,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="culminationtxt" render="Label" position="350,260" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="azimuthtxt" render="Label" position="470,260" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="suntxt" render="Label" position="20,290" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moontxt" render="Label" position="20,450" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="mercurytxt" render="Label" position="20,310" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="venustxt" render="Label" position="20,330" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="marstxt" render="Label" position="20,350" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="jupitertxt" render="Label" position="20,370" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="saturntxt" render="Label" position="20,390" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="uranustxt" render="Label" position="20,410" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="neptunetxt" render="Label" position="20,430" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moonlighttxt" render="Label" position="190,520" size="300,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="moondisttxt" render="Label" position="190,540" size="300,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />

			<widget source="sunrise" render="Label" position="160,290" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="sunset" render="Label" position="270,290" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="sunculmination" render="Label" position="380,290" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryrise" render="Label" position="160,310" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryset" render="Label" position="270,310" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryculmination" render="Label" position="380,310" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="mercuryazimuth" render="Label" position="490,310" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusset" render="Label" position="270,330" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusrise" render="Label" position="160,330" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusculmination" render="Label" position="380,330" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="venusazimuth" render="Label" position="490,330" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsrise" render="Label" position="160,350" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsset" render="Label" position="270,350" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsculmination" render="Label" position="380,350" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="marsazimuth" render="Label" position="490,350" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterrise" render="Label" position="160,370" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterset" render="Label" position="270,370" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterculmination" render="Label" position="380,370" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="jupiterazimuth" render="Label" position="490,370" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnrise" render="Label" position="160,390" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnset" render="Label" position="270,390" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnculmination" render="Label" position="380,390" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="saturnazimuth" render="Label" position="490,390" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusrise" render="Label" position="160,410" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusset" render="Label" position="270,410" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusculmination" render="Label" position="380,410" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="uranusazimuth" render="Label" position="490,410" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptunerise" render="Label" position="160,430" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptuneset" render="Label" position="270,430" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptuneculmination" render="Label" position="380,430" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="neptuneazimuth" render="Label" position="490,430" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonrise" render="Label" position="160,450" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonset" render="Label" position="270,450" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonculmination" render="Label" position="380,450" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moondist" render="Label" position="390,540" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonazimuth" render="Label" position="490,450" size="100,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="center" transparent="1" />
			<widget source="moonlight" render="Label" position="390,520" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="moonphase" render="Label" position="20,580" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="picmoon" position="50,500" size="90,90" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="830,20" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="feelsliketxt" render="Label" position="830,40" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="humiditytxt" render="Label" position="830,60" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="windtxt" render="Label" position="830,80" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature" render="Label" position="1030,20" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="feelslike" render="Label" position="1030,40" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext" render="Label" position="610,100" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="humidity" render="Label" position="1030,60" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="wind" render="Label" position="890,80" size="290,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic" position="655,0" size="128,128" zPosition="2" alphatest="blend" />

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
			<widget source="temperaturetxt" render="Label" position="830,180" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="830,200" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="830,140" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="830,160" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature1" render="Label" position="1030,180" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext1" render="Label" position="610,220" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip1" render="Label" position="1030,200" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date1" render="Label" position="1030,160" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day1" render="Label" position="1030,140" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic1" position="655,125" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="830,300" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="830,320" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="830,260" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="830,280" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature2" render="Label" position="1030,300" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext2" render="Label" position="610,340" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip2" render="Label" position="1030,320" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date2" render="Label" position="1030,280" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day2" render="Label" position="1030,260" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic2" position="655,245" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="830,420" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="830,440" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="830,380" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="830,400" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature3" render="Label" position="1030,420" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext3" render="Label" position="610,460" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip3" render="Label" position="1030,440" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date3" render="Label" position="1030,400" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day3" render="Label" position="1030,380" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic3" position="655,365" size="128,128" zPosition="2" alphatest="blend" />

			<widget source="temperaturetxt" render="Label" position="830,540" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="preciptxt" render="Label" position="830,560" size="250,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="daytxt" render="Label" position="830,500" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="datetxt" render="Label" position="830,520" size="200,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget source="temperature4" render="Label" position="1030,540" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="skytext4" render="Label" position="610,580" size="570,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="precip4" render="Label" position="1030,560" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="date4" render="Label" position="1030,520" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget source="day4" render="Label" position="1030,500" size="150,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="right" transparent="1" />
			<widget name="pic4" position="655,485" size="128,128" zPosition="2" alphatest="blend" />

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
		self.sunculmination = {'Solstice':''}
		self.mercuryrise = {'Mercuryrise':''}
		self.mercuryset = {'Mercuryset':''}
		self.mercuryculmination = {'Mercuryculmination':''}
		self.mercuryazimuth = {'Mercuryazimuth':''}
		self.venusrise = {'Venusrise':''}
		self.venusset = {'Venusset':''}
		self.venusculmination = {'Venusculmination':''}
		self.venusazimuth = {'Venusazimuth':''}
		self.marsrise = {'Marsrise':''}
		self.marsset = {'Marsset':''}
		self.marsculmination = {'Marsculmination':''}
		self.marsazimuth = {'Marsazimuth':''}
		self.jupiterrise = {'Jupiterrise':''}
		self.jupiterset = {'Jupiterset':''}
		self.jupiterculmination = {'Jupiterculmination':''}
		self.jupiterazimuth = {'Jupiterazimuth':''}
		self.saturnrise = {'Saturnrise':''}
		self.saturnset = {'Saturnset':''}
		self.saturnculmination = {'Saturnculmination':''}
		self.saturnazimuth = {'Saturnazimuth':''}
		self.uranusrise = {'Uranusrise':''}
		self.uranusset = {'Uranusset':''}
		self.uranusculmination = {'Uranusculmination':''}
		self.uranusazimuth = {'Uranusazimuth':''}
		self.neptunerise = {'Neptunerise':''}
		self.neptuneset = {'Neptuneset':''}
		self.neptuneculmination = {'Neptuneculmination':''}
		self.neptuneazimuth = {'Neptuneazimuth':''}
		self.moonrise = {'Moonrise':''}
		self.moonset = {'Moonset':''}
		self.moondist = {'Moondist':''}
		self.moonculmination = {'Moonculmination':''}
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
		self["sunrisetxt"] = StaticText(_("Sun rise:"))
		self["sunsettxt"] = StaticText(_("Sun set:"))
		self["sunculminationtxt"] = StaticText(_("Solstice:"))
		self["mercuryrisetxt"] = StaticText(_("Mercury rise:"))
		self["mercurysettxt"] = StaticText(_("Mercury set:"))
		self["mercuryculminationtxt"] = StaticText(_("Mercury culmination:"))
		self["mercuryazimuthtxt"] = StaticText(_("Mercury azimuth:"))
		self["venusrisetxt"] = StaticText(_("Venus rise:"))
		self["venussettxt"] = StaticText(_("Venus set:"))
		self["venusculminationtxt"] = StaticText(_("Venus culmination:"))
		self["venusazimuthtxt"] = StaticText(_("Venus azimuth:"))
		self["marsrisetxt"] = StaticText(_("Mars rise:"))
		self["marssettxt"] = StaticText(_("Mars set:"))
		self["marsculminationtxt"] = StaticText(_("Mars culmination:"))
		self["marsazimuthtxt"] = StaticText(_("Mars azimuth:"))
		self["jupiterrisetxt"] = StaticText(_("Jupiter rise:"))
		self["jupitersettxt"] = StaticText(_("Jupiter set:"))
		self["jupiterculminationtxt"] = StaticText(_("Jupiter culmination:"))
		self["jupiterazimuthtxt"] = StaticText(_("Jupiter azimuth:"))
		self["saturnrisetxt"] = StaticText(_("Saturn rise:"))
		self["saturnsettxt"] = StaticText(_("Saturn set:"))
		self["saturnculminationtxt"] = StaticText(_("Saturn culmination:"))
		self["saturnazimuthtxt"] = StaticText(_("Saturn azimuth:"))
		self["uranusrisetxt"] = StaticText(_("Uranus rise:"))
		self["uranussettxt"] = StaticText(_("Uranus set:"))
		self["uranusculminationtxt"] = StaticText(_("Uranus culmination:"))
		self["uranusazimuthtxt"] = StaticText(_("Uranus azimuth:"))
		self["neptunerisetxt"] = StaticText(_("Neptune rise:"))
		self["neptunesettxt"] = StaticText(_("Neptune set:"))
		self["neptuneculminationtxt"] = StaticText(_("Neptune culmination:"))
		self["neptuneazimuthtxt"] = StaticText(_("Neptune azimuth:"))
		self["moondisttxt"] = StaticText(_("Moon distance:"))
		self["moonculminationtxt"] = StaticText(_("Moon culmination:"))
		self["moonazimuthtxt"] = StaticText(_("Moon azimuth:"))
		self["moonrisetxt"] = StaticText(_("Moon rise:"))
		self["moonsettxt"] = StaticText(_("Moon set:"))
		self["moonlighttxt"] = StaticText(_("Moon light:"))

		self["risetxt"] = StaticText(_("Rise:"))
		self["settxt"] = StaticText(_("Set:"))
		self["culminationtxt"] = StaticText(_("Culmination:"))
		self["azimuthtxt"] = StaticText(_("Azimuth:"))
		self["suntxt"] = StaticText(_("Sun:"))
		self["mercurytxt"] = StaticText(_("Mercury:"))
		self["venustxt"] = StaticText(_("Venus:"))
		self["marstxt"] = StaticText(_("Mars:"))
		self["jupitertxt"] = StaticText(_("Jupiter:"))
		self["saturntxt"] = StaticText(_("Saturn:"))
		self["uranustxt"] = StaticText(_("Uranus:"))
		self["neptunetxt"] = StaticText(_("Neptune:"))
		self["moontxt"] = StaticText(_("Moon:"))

		self["yulianday"] = StaticText()
		self["sunrise"] = StaticText()
		self["sunset"] = StaticText()
		self["sunculmination"] = StaticText()
		self["mercuryrise"] = StaticText()
		self["mercuryset"] = StaticText()
		self["mercuryculmination"] = StaticText()
		self["mercuryazimuth"] = StaticText()
		self["venusrise"] = StaticText()
		self["venusset"] = StaticText()
		self["venusculmination"] = StaticText()
		self["venusazimuth"] = StaticText()
		self["marsrise"] = StaticText()
		self["marsset"] = StaticText()
		self["marsculmination"] = StaticText()
		self["marsazimuth"] = StaticText()
		self["jupiterrise"] = StaticText()
		self["jupiterset"] = StaticText()
		self["jupiterculmination"] = StaticText()
		self["jupiterazimuth"] = StaticText()
		self["saturnrise"] = StaticText()
		self["saturnset"] = StaticText()
		self["saturnculmination"] = StaticText()
		self["saturnazimuth"] = StaticText()
		self["uranusrise"] = StaticText()
		self["uranusset"] = StaticText()
		self["uranusculmination"] = StaticText()
		self["uranusazimuth"] = StaticText()
		self["neptunerise"] = StaticText()
		self["neptuneset"] = StaticText()
		self["neptuneculmination"] = StaticText()
		self["neptuneazimuth"] = StaticText()
		self["moondist"] = StaticText()
		self["moonculmination"] = StaticText()
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
		JDN = day + int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + 2 - int(year / 100) + int(year / 400) - 1524.5
		JD = JDN + UT / 24
# Звездное время
		T = (JDN - 2451545) / 36525 # юлианское столетие на полночь по Гринвичу
		STT = math.fmod((6.697374558333 + 2400.0513369072223 * T + 0.0000258622 * T * T - 0.00000000172 * T * T * T), 24) # звёздное время в Гринвиче в полночь
		ST = math.fmod((STT + UT * 1.0027379093 - (long / 15) * 0.0027379093), 24) # местное звёздное время на момент местного времени
		if ST < 0:
			ST = ST + 24
		ST = ST * 15 # звёздное время на момент рассчёта в градусах
# Восход, закат, кульминация
# Орбита Земли
		T = (JDN - 2451545) / 36525
		LS = 280.4664568 + 36000.7697509 * T + 0.0003032 * T * T + 0.00000002 * T * T * T # ср долгота
		MS = 357.5291092 + 35999.0502909 * T - 0.0001537 * T * T - 0.00000004 * T * T * T # ср аномалия
		ES = 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T # эксцентриситет орбиты
		EPS = 23.43929111 - 0.01300416667 * T - 0.00000016389 * T * T + 0.00000050361 * T * T * T # наклон эклиптики

		CS = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(MS * DEG2RAD)\
			+ (0.019993 - 0.000101 * T) * math.sin(2 * MS * DEG2RAD)\
			+ 0.000289 * math.sin(3 * MS * DEG2RAD) # уравнение центра
		DS = (1.000001018 * (1 - ES * ES)) / (ES * math.cos((MS + CS) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		SLong = LS + CS - (20.4898 / 3600 / DS) # истинная долгота солнца

		# гелиоцентрические координаты
		wP3 = 288.064
		WP3 = 174.873
		XE = DS * math.cos(WP3 * DEG2RAD) * math.cos((wP3 + MS) * DEG2RAD)
		YE = DS * math.sin(WP3 * DEG2RAD) * math.cos((wP3 + MS) * DEG2RAD)
		# эклиптические координаты
		DEC = math.asin(math.sin(EPS * DEG2RAD) * math.sin(SLong * DEG2RAD)) * RAD2DEG # склонение
		ALFA = (7.53 * math.cos(LS * DEG2RAD) + 1.5 * math.sin(LS * DEG2RAD) - 9.87 * math.sin(2 * LS * DEG2RAD)) / 60 # уравнение времени
		BETA = math.acos((math.cos(90.85 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG
		SSS = ALFA + (180 + 15 - long) / 15 + zone
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
# Орбиты планет
		T = (JDN - 2451545) / 36525
		MP1 = 102.27938 + 149472.51529 * T + 0.000007 * T * T
		MP2 = 212.60322 + 58517.80387 * T + 0.001286 * T * T
		MP3 = 358.47583 + 35999.04975 * T - 0.000150 * T * T - 0.0000033 * T * T * T
		MP4 = 319.51913 + 19139.85475 * T + 0.000181 * T * T
		MP5 = 225.32833 + 3034.69202 * T - 0.000722 * T * T
		MP6 = 175.46622 + 1221.55147 * T - 0.000502 * T * T
		MP7 = 72.64878 + 428.37911 * T + 0.000079 * T * T
		MP8 = 37.73063 + 218.46134 * T - 0.000070 * T * T
# Орбита меркурия
		LP1 = 178.179078 + 149474.07078 * T + 0.0003011 * T * T # ср долгота L
		wP1 = 28.753753 + 0.3702806 * T + 0.0001208 * T * T # аргумент перигелия w
		WP1 = 47.145944 + 1.1852083 * T + 0.0001739 * T * T # долгота восходящего узла W
		IP1 = 7.002881 + 0.0018608 * T - 0.0000183 * T * T # наклон на плоскости эклиптики i
		EP1 = 0.20561421 + 0.00002046 * T - 0.000000030 * T * T # эксцентриситет орбиты e

		EL = 0.00204 * math.cos((5 * MP2 - 2 * MP1 + 12.220) * DEG2RAD)\
			 + 0.00103 * math.cos((2 * MP2 - MP1 - 160.692) * DEG2RAD)\
			 + 0.00091 * math.cos((2 * MP5 - MP1 - 37.003) * DEG2RAD)\
			 + 0.00078 * math.cos((5 * MP2 - 3 * MP1 + 10.137) * DEG2RAD)

		LP = LP1 + EL
		M0 = math.fmod(174.795 + 4.092317 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP1 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (0.3870986 * (1 - EP1 * EP1)) / (EP1 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP1 * DEG2RAD) * math.cos((wP1 + MP) * DEG2RAD) - math.sin(WP1 * DEG2RAD) * math.cos(IP1 * DEG2RAD) * math.sin((wP1 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP1 * DEG2RAD) * math.cos((wP1 + MP) * DEG2RAD) + math.cos(WP1 * DEG2RAD) * math.cos(IP1 * DEG2RAD) * math.sin((wP1 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP1 * DEG2RAD) * math.sin((wP1 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол

		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P1Ch = int(SPC)
		P1Cm = int(round((SPC - P1Ch) * 60))
		P1Rh = int(SPR)
		P1Rm = int(round(((SPR) - P1Rh) * 60))
		P1Sh = int(SPS)
		P1Sm = int(round(((SPS) - P1Sh) * 60))
		if P1Cm == 60:
			P1Cm = 0
			P1Ch = P1Ch + 1
		if P1Cm < 10:
			P1Cx = '0'
		else:
			P1Cx = ''
		if P1Rm == 60:
			P1Rm = 0
			P1Rh = P1Rh + 1
		if P1Rm < 10:
			P1Rx = '0'
		else:
			P1Rx = ''
		if P1Sm == 60:
			P1Sm = 0
			P1Sh = P1Sh + 1
		if P1Sm < 10:
			P1Sx = '0'
		else:
			P1Sx = ''
# Орбита венеры
		LP2 = 342.767053 + 58519.21191 * T + 0.0003097 * T * T # ср долгота L
		wP2 = 54.384186 + 0.5081861 * T - 0.0013864 * T * T # аргумент перигелия w
		WP2 = 75.779647 + 0.8998500 * T + 0.0004100 * T * T # долгота восходящего узла W
		IP2 = 3.393631 + 0.0010058 * T - 0.0000010 * T * T # наклон на плоскости эклиптики i
		EP2 = 0.00682069 - 0.00004774 * T + 0.000000091 * T * T # эксцентриситет орбиты e

		EL = 0.00313 * math.cos((2 * MP3 - 2 * MP2 - 148.225) * DEG2RAD)\
			+ 0.00198 * math.cos((3 * MP3 - 3 * MP2 + 2.565) * DEG2RAD)\
			+ 0.00136 * math.cos((MP3 - MP2 - 119.107) * DEG2RAD)\
			+ 0.00096 * math.cos((3 * MP3 - 2 * MP2 - 135.912) * DEG2RAD)\
			+ 0.00082 * math.cos((MP5 - MP2 - 208.087) * DEG2RAD)

		CP = 0.00077 * math.sin((237.24 + 150.27 * T) * DEG2RAD)

		LP = LP2 + EL + CP
		M0 = math.fmod(50.416 + 1.602136 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP2 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (0.7233316 * (1 - EP2 * EP2)) / (EP2 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP2 * DEG2RAD) * math.cos((wP2 + MP) * DEG2RAD) - math.sin(WP2 * DEG2RAD) * math.cos(IP2 * DEG2RAD) * math.sin((wP2 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP2 * DEG2RAD) * math.cos((wP2 + MP) * DEG2RAD) + math.cos(WP2 * DEG2RAD) * math.cos(IP2 * DEG2RAD) * math.sin((wP2 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP2 * DEG2RAD) * math.sin((wP2 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P2Ch = int(SPC)
		P2Cm = int(round((SPC - P2Ch) * 60))
		P2Rh = int(SPR)
		P2Rm = int(round(((SPR) - P2Rh) * 60))
		P2Sh = int(SPS)
		P2Sm = int(round(((SPS) - P2Sh) * 60))
		if P2Cm == 60:
			P2Cm = 0
			P2Ch = P2Ch + 1
		if P2Cm < 10:
			P2Cx = '0'
		else:
			P2Cx = ''
		if P2Rm == 60:
			P2Rm = 0
			P2Rh = P2Rh + 1
		if P2Rm < 10:
			P2Rx = '0'
		else:
			P2Rx = ''
		if P2Sm == 60:
			P2Sm = 0
			P2Sh = P2Sh + 1
		if P2Sm < 10:
			P2Sx = '0'
		else:
			P2Sx = ''
# Орбита марса
		LP4 = 293.737334 + 19141.69551 * T + 0.0003107 * T * T # ср долгота L
		wP4 = 285.431761 + 1.0697667 * T + 0.0001313 * T * T + 0.00000414 * T * T * T # аргумент перигелия w
		WP4 = 48.786442 + 0.7709917 * T - 0.0000014 * T * T - 0.00000533 * T * T * T # долгота восходящего узла W
		IP4 = 1.850333 - 0.0006750 * T + 0.0000126 * T * T # наклон на плоскости эклиптики i
		EP4 = 0.09331290 + 0.000092064 * T - 0.000000077 * T * T # эксцентриситет орбиты e

		EL = 0.00705 * math.cos((MP5 - MP4 - 48.958) * DEG2RAD)\
			+ 0.00607 * math.cos((2 * MP5 - MP4 - 188.350) * DEG2RAD)\
			+ 0.00445 * math.cos((2 * MP5 - 2 * MP4 - 191.897) * DEG2RAD)\
			+ 0.00388 * math.cos((MP3 - 2 * MP4 + 20.495) * DEG2RAD)\
			+ 0.00238 * math.cos((MP3 - MP4 + 35.097) * DEG2RAD)\
			+ 0.00204 * math.cos((2 * MP3 - 3 * MP4 + 158.638) * DEG2RAD)\
			+ 0.00177 * math.cos((3 * MP4 - MP2 - 57.602) * DEG2RAD)\
			+ 0.00136 * math.cos((2 * MP3 - 4 * MP4 + 154.093) * DEG2RAD)\
			+ 0.00104 * math.cos((MP5 + 17.618) * DEG2RAD)

		CP = (- 0.01133 * math.sin((3 * MP5 - 8 * MP4 + 4 * MP3) * DEG2RAD)\
			- 0.00933 * math.cos((3 * MP5 - 8 * MP4 + 4 * MP3) * DEG2RAD)) # уравнение центра

		LP = LP4 + EL + CP
		M0 = math.fmod(19.373 + 0.524039 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP4 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (1.5236883 * (1 - EP4 * EP4)) / (EP4 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP4 * DEG2RAD) * math.cos((wP4 + MP) * DEG2RAD) - math.sin(WP4 * DEG2RAD) * math.cos(IP4 * DEG2RAD) * math.sin((wP4 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP4 * DEG2RAD) * math.cos((wP4 + MP) * DEG2RAD) + math.cos(WP4 * DEG2RAD) * math.cos(IP4 * DEG2RAD) * math.sin((wP4 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP4 * DEG2RAD) * math.sin((wP4 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P4Ch = int(SPC)
		P4Cm = int(round((SPC - P4Ch) * 60))
		P4Rh = int(SPR)
		P4Rm = int(round(((SPR) - P4Rh) * 60))
		P4Sh = int(SPS)
		P4Sm = int(round(((SPS) - P4Sh) * 60))
		if P4Cm == 60:
			P4Cm = 0
			P4Ch = P4Ch + 1
		if P4Cm < 10:
			P4Cx = '0'
		else:
			P4Cx = ''
		if P4Rm == 60:
			P4Rm = 0
			P4Rh = P4Rh + 1
		if P4Rm < 10:
			P4Rx = '0'
		else:
			P4Rx = ''
		if P4Sm == 60:
			P4Sm = 0
			P4Sh = P4Sh + 1
		if P4Sm < 10:
			P4Sx = '0'
		else:
			P4Sx = ''
# Орбита юпитера
		LP5 = 238.049257 + 3036.301986 * T + 0.0003347 * T * T - 0.00000165 * T * T * T # ср долгота L
		wP5 = 273.277558 + 0.5994317 * T + 0.00070405 * T * T + 0.00000508 * T * T * T # аргумент перигелия w
		WP5 = 99.443414 + 1.0105300 * T + 0.00035222 * T * T - 0.00000851 * T * T * T # долгота восходящего узла W
		IP5 = 1.308736 - 0.0056961 * T + 0.0000039 * T * T # наклон на плоскости эклиптики i
		EP5 = 0.04833475 + 0.000164180 * T - 0.0000004676 * T * T - 0.0000000017 * T * T * T # эксцентриситет орбиты e

		NJ = T / 5.0 + 0.1
		PJ = 237.47555 + 3034.9061 * T
		QJ = 265.91650 + 1222.1139 * T
		SJ = 243.51721 + 428.4677 * T
		VJ = 5.0 * QJ - 2.0 * PJ
		WJ = 2.0 * PJ - 6.0 * QJ + 3.0 * SJ
		ZJ = QJ - PJ

		EL = (0.331364 - 0.010281 * NJ - 0.004692 * NJ * NJ) * math.sin(VJ * DEG2RAD)\
			+ (0.003228 - 0.064436 * NJ + 0.002075 * NJ * NJ) * math.cos(VJ * DEG2RAD)\
			- (0.003083 + 0.000275 * NJ - 0.000489 * NJ * NJ) * math.sin(2 * VJ * DEG2RAD)\
			+ 0.002472 * math.sin(WJ * DEG2RAD)\
			+ 0.013619 * math.sin(ZJ * DEG2RAD)\
			+ 0.018472 * math.sin(2 * ZJ * DEG2RAD)\
			+ 0.006717 * math.sin(3 * ZJ * DEG2RAD)\
			+ 0.002775 * math.sin(4 * ZJ * DEG2RAD)\
			+ (0.007275 - 0.001253 * NJ) * math.sin(ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			+ 0.006417 * math.sin(2 * ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			+ 0.002439 * math.sin(3 * ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)

		EL = EL - (0.033839 + 0.001125 * NJ) * math.cos(ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			- 0.003767 * math.cos(2 * ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			- (0.035681 + 0.001208 * NJ) * math.sin(ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.004261 * math.sin(2 * ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			+ 0.002178 * math.cos(QJ * DEG2RAD)\
			+ (-0.006333 + 0.001161 * NJ) * math.cos(ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.006675 * math.cos(2 * ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.002664 * math.cos(3 * ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.002572 * math.sin(ZJ * DEG2RAD) * math.sin(2 * QJ * DEG2RAD)\
			- 0.003567 * math.sin(2 * ZJ * DEG2RAD) * math.sin(2 * QJ * DEG2RAD)\
			+ 0.002094 * math.cos(ZJ * DEG2RAD) * math.cos(2 * QJ * DEG2RAD)\
			+ 0.003342 * math.cos(2 * ZJ * DEG2RAD) * math.cos(2 * QJ * DEG2RAD)

		LP = LP5 + EL
		M0 = math.fmod(20.020 + 0.083056 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP5 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (5.202561 * (1 - EP5 * EP5)) / (EP5 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP5 * DEG2RAD) * math.cos((wP5 + MP) * DEG2RAD) - math.sin(WP5 * DEG2RAD) * math.cos(IP5 * DEG2RAD) * math.sin((wP5 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP5 * DEG2RAD) * math.cos((wP5 + MP) * DEG2RAD) + math.cos(WP5 * DEG2RAD) * math.cos(IP5 * DEG2RAD) * math.sin((wP5 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP5 * DEG2RAD) * math.sin((wP5 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P5Ch = int(SPC)
		P5Cm = int(round((SPC - P5Ch) * 60))
		P5Rh = int(SPR)
		P5Rm = int(round(((SPR) - P5Rh) * 60))
		P5Sh = int(SPS)
		P5Sm = int(round(((SPS) - P5Sh) * 60))
		if P5Cm == 60:
			P5Cm = 0
			P5Ch = P5Ch + 1
		if P5Cm < 10:
			P5Cx = '0'
		else:
			P5Cx = ''
		if P5Rm == 60:
			P5Rm = 0
			P5Rh = P5Rh + 1
		if P5Rm < 10:
			P5Rx = '0'
		else:
			P5Rx = ''
		if P5Sm == 60:
			P5Sm = 0
			P5Sh = P5Sh + 1
		if P5Sm < 10:
			P5Sx = '0'
		else:
			P5Sx = ''
# Орбита сатурна
		LP6 = 266.564377 + 1223.509884 * T + 0.0003245 * T * T - 0.0000058 * T * T * T # ср долгота L
		wP6 = 338.307800 + 1.0852207 * T + 0.00097854 * T * T + 0.00000992 * T * T * T # аргумент перигелия w
		WP6 = 112.790414 + 0.8731951 * T - 0.00015218 * T * T - 0.00000531 * T * T * T # долгота восходящего узла W
		IP6 = 2.492519 - 0.0039189 * T - 0.00001549 * T * T + 0.00000004 * T * T * T # наклон на плоскости эклиптики i
		EP6 = 0.05589232 - 0.00034550 * T - 0.000000728 * T * T + 0.00000000074 * T * T * T # эксцентриситет орбиты e

		NS = T / 5.0 + 0.1
		PS = 237.47555 + 3034.9061 * T
		QS = 265.91650 + 1222.1139 * T
		SS = 243.51721 + 428.4677 * T
		VS = 5.0 * QS - 2.0 * PS
		WS = 2.0 * PS - 6.0 * QS + 3.0 * SS
		ZS = QS - PS
		PSI = SS - QS

		EL = (-0.814181 + 0.018150 * NS + 0.016714 * NS * NS) * math.sin(VS * DEG2RAD)\
			+ (-0.010497 + 0.160906 * NS - 0.004100 * NS * NS) * math.cos(VS * DEG2RAD)\
			+ 0.007581 * math.sin(2 * VS * DEG2RAD)\
			- 0.007986 * math.sin(WS * DEG2RAD)\
			- 0.148811 * math.sin(ZS * DEG2RAD)\
			- 0.040786 * math.sin(2 * ZS * DEG2RAD)\
			- 0.015208 * math.sin(3 * ZS * DEG2RAD)\
			- 0.006339 * math.sin(4 * ZS * DEG2RAD)\
			- 0.006244 * math.sin(QS * DEG2RAD)

		EL = EL + (0.008931 + 0.002728 * NS) * math.sin(ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			- 0.016500 * math.sin(2 * ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			- 0.005775 * math.sin(3 * ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			+ (0.081344 + 0.003206 * NS) * math.cos(ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			+ 0.015019 * math.cos(2 * ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			+ (0.085581 + 0.002494 * NS) * math.sin(ZS * DEG2RAD) * math.cos(QS * DEG2RAD)\
			+ (0.025328 - 0.003117 * NS) * math.cos(ZS * DEG2RAD) * math.cos(QS * DEG2RAD)

		EL = EL + 0.014394 * math.cos(2 * ZS * DEG2RAD) * math.cos(QS * DEG2RAD)\
			+ 0.006319 * math.cos(3 * ZS * DEG2RAD) * math.cos(QS * DEG2RAD)\
			+ 0.006369 * math.sin(ZS * DEG2RAD) * math.sin(2 * QS * DEG2RAD)\
			+ 0.009156 * math.sin(2 * ZS * DEG2RAD) * math.sin(2 * QS * DEG2RAD)\
			+ 0.007525 * math.sin(3 * PSI * DEG2RAD) * math.sin(2 * QS * DEG2RAD)\
			- 0.005236 * math.cos(ZS * DEG2RAD) * math.cos(2 * QS * DEG2RAD)\
			- 0.007736 * math.cos(2 * ZS * DEG2RAD) * math.cos(2 * QS * DEG2RAD)\
			- 0.007528 * math.cos(3 * PSI * DEG2RAD) * math.cos(2 * QS * DEG2RAD)

		LP = LP6 + EL
		M0 = math.fmod(317.021 + 0.033371 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP6 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (9.554747 * (1 - EP6 * EP6)) / (EP6 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP6 * DEG2RAD) * math.cos((wP6 + MP) * DEG2RAD) - math.sin(WP6 * DEG2RAD) * math.cos(IP6 * DEG2RAD) * math.sin((wP6 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP6 * DEG2RAD) * math.cos((wP6 + MP) * DEG2RAD) + math.cos(WP6 * DEG2RAD) * math.cos(IP6 * DEG2RAD) * math.sin((wP6 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP6 * DEG2RAD) * math.sin((wP6 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P6Ch = int(SPC)
		P6Cm = int(round((SPC - P6Ch) * 60))
		P6Rh = int(SPR)
		P6Rm = int(round(((SPR) - P6Rh) * 60))
		P6Sh = int(SPS)
		P6Sm = int(round(((SPS) - P6Sh) * 60))
		if P6Cm == 60:
			P6Cm = 0
			P6Ch = P6Ch + 1
		if P6Cm < 10:
			P6Cx = '0'
		else:
			P6Cx = ''
		if P6Rm == 60:
			P6Rm = 0
			P6Rh = P6Rh + 1
		if P6Rm < 10:
			P6Rx = '0'
		else:
			P6Rx = ''
		if P6Sm == 60:
			P6Sm = 0
			P6Sh = P6Sh + 1
		if P6Sm < 10:
			P6Sx = '0'
		else:
			P6Sx = ''
# Орбита урана
		LP7 = 244.197470 + 429.863546 * T + 0.0003160 * T * T - 0.00000060 * T * T * T # ср долгота L
		wP7 = 98.071581 + 0.9857650 * T - 0.0010745 * T * T - 0.00000061 * T * T * T # аргумент перигелия w
		WP7 = 73.477111 + 0.4986678 * T + 0.0013117 * T * T # долгота восходящего узла W
		IP7 = 0.772464 + 0.0006253 * T + 0.0000395 * T * T # наклон на плоскости эклиптики i
		EP7 = 0.0463444 - 0.00002658 * T + 0.000000077 * T * T # эксцентриситет орбиты e

		NU = T / 5.0 + 0.1
		PU = 237.47555 + 3034.9061 * T
		QU = 265.91650 + 1222.1139 * T
		SU = 243.51721 + 428.4677 * T
		GU = 83.76922 + 218.4901 * T
		WU = 2.0 * PU - 6.0 * QU + 3.0 * SU
		HU = 2.0 * GU - SU

		EL = (0.864319 - 0.001583 * NU) * math.sin(HU * DEG2RAD)\
			+ (0.082222 - 0.006833 * NU) * math.cos(HU * DEG2RAD)\
			+ 0.036017 * math.sin(2 * HU * DEG2RAD)\
			- 0.003019 * math.cos(2 * HU * DEG2RAD)\
			+ 0.008122 * math.sin(WU)

		LP = LP7 + EL
		M0 = math.fmod(141.050 + 0.011698 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP7 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (19.21814 * (1 - EP7 * EP7)) / (EP7 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP7 * DEG2RAD) * math.cos((wP7 + MP) * DEG2RAD) - math.sin(WP7 * DEG2RAD) * math.cos(IP7 * DEG2RAD) * math.sin((wP7 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP7 * DEG2RAD) * math.cos((wP7 + MP) * DEG2RAD) + math.cos(WP7 * DEG2RAD) * math.cos(IP7 * DEG2RAD) * math.sin((wP7 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP7 * DEG2RAD) * math.sin((wP7 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P7Ch = int(SPC)
		P7Cm = int(round((SPC - P7Ch) * 60))
		P7Rh = int(SPR)
		P7Rm = int(round(((SPR) - P7Rh) * 60))
		P7Sh = int(SPS)
		P7Sm = int(round(((SPS) - P7Sh) * 60))
		if P7Cm == 60:
			P7Cm = 0
			P7Ch = P7Ch + 1
		if P7Cm < 10:
			P7Cx = '0'
		else:
			P7Cx = ''
		if P7Rm == 60:
			P7Rm = 0
			P7Rh = P7Rh + 1
		if P7Rm < 10:
			P7Rx = '0'
		else:
			P7Rx = ''
		if P7Sm == 60:
			P7Sm = 0
			P7Sh = P7Sh + 1
		if P7Sm < 10:
			P7Sx = '0'
		else:
			P7Sx = ''
# Орбита нептуна
		LP8 = 84.457994 + 219.885914 * T + 0.0003205 * T * T - 0.00000060 * T * T * T # ср долгота L
		wP8 = 276.045975 + 0.3256394 * T + 0.00014095 * T * T + 0.000004113 * T * T * T # аргумент перигелия w
		WP8 = 130.681389 + 1.0989350 * T + 0.00024987 * T * T - 0.000004718 * T * T * T # долгота восходящего узла W
		IP8 = 1.779242 - 0.0095436 * T - 0.0000091 * T * T # наклон на плоскости эклиптики i
		EP8 = 0.00899704 + 0.000006330 * T - 0.000000002 * T * T # эксцентриситет орбиты e

		NN = T / 5.0 + 0.1
		SN = 243.51721 + 428.4677 * T
		GN = 83.76922 + 218.4901 * T
		HN = 2.0 * GN - SN

		EL = (-0.589833 + 0.001089 * NN) * math.sin(HN * DEG2RAD)\
			+ (-0.056094 + 0.004658 * NN) * math.cos(HN * DEG2RAD)\
			- 0.024286 * math.sin(2 * HN * DEG2RAD)

		LP = LP8 + EL
		M0 = math.fmod(256.225 + 0.005965 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP8 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (30.10957 * (1 - EP8 * EP8)) / (EP8 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP8 * DEG2RAD) * math.cos((wP8 + MP) * DEG2RAD) - math.sin(WP8 * DEG2RAD) * math.cos(IP8 * DEG2RAD) * math.sin((wP8 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP8 * DEG2RAD) * math.cos((wP8 + MP) * DEG2RAD) + math.cos(WP8 * DEG2RAD) * math.cos(IP8 * DEG2RAD) * math.sin((wP8 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP8 * DEG2RAD) * math.sin((wP8 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		BETA = math.acos((math.cos(90.35 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SPR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPR < 0:
			SPR = SPR + 24
		SPS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 + zone - long / 15, 24)
		if SPS < 0:
			SPS = SPS + 24
		if SPR < SPS:
			SPC = (SPR + SPS) / 2
		else:
			SPC = (SPR + SPS) / 2 + 12
			if SPC >= 24:
				SPC = SPC - 24
# Время восхода/захода
		P8Ch = int(SPC)
		P8Cm = int(round((SPC - P8Ch) * 60))
		P8Rh = int(SPR)
		P8Rm = int(round(((SPR) - P8Rh) * 60))
		P8Sh = int(SPS)
		P8Sm = int(round(((SPS) - P8Sh) * 60))
		if P8Cm == 60:
			P8Cm = 0
			P8Ch = P8Ch + 1
		if P8Cm < 10:
			P8Cx = '0'
		else:
			P8Cx = ''
		if P8Rm == 60:
			P8Rm = 0
			P8Rh = P8Rh + 1
		if P8Rm < 10:
			P8Rx = '0'
		else:
			P8Rx = ''
		if P8Sm == 60:
			P8Sm = 0
			P8Sh = P8Sh + 1
		if P8Sm < 10:
			P8Sx = '0'
		else:
			P8Sx = ''
# Орбита луны
		LM = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T * T * T / 538841 - T * T * T * T / 65194000 # ср долгота луны
		FM = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T - T * T * T / 3526000 + T * T * T * T / 863310000 # ср аргумент широты луны
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср элонгация луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		EM = 1 - 0.002516 * T - 0.0000074 * T * T # поправка на изменяющийся эксцентриситет

		EL = 6.289 * math.sin(MM * DEG2RAD)\
			+ 1.274 * math.sin((2 * DM - MM) * DEG2RAD)\
			+ 0.658 * math.sin(2 * DM * DEG2RAD)\
			+ 0.214 * math.sin(2 * MM * DEG2RAD)\
			- 0.186 * math.sin(MS * DEG2RAD)\
			- 0.114 * math.sin(2 * FM * DEG2RAD)\
			+ 0.059 * math.sin((2 * DM - 2 * MM) * DEG2RAD)\
			+ 0.057 * math.sin((2 * DM - MS - MM) * DEG2RAD)\
			+ 0.053 * math.sin((2 * DM + MM) * DEG2RAD)\
			+ 0.046 * math.sin((2 * DM - MS) * DEG2RAD)\
			- 0.041 * math.sin((MS - MM) * DEG2RAD)\
			- 0.035 * math.sin(DM * DEG2RAD)\
			- 0.030 * math.sin((MS + MM) * DEG2RAD)

		EB = 5.128 * math.sin(FM * DEG2RAD)\
			+ 0.281 * math.sin((MM + FM) * DEG2RAD)\
			+ 0.278 * math.sin((MM - FM) * DEG2RAD)\
			+ 0.173 * math.sin((2 * DM - FM) * DEG2RAD)\
			+ 0.055 * math.sin((2 * DM - MM + FM) * DEG2RAD)\
			+ 0.046 * math.sin((2 * DM - MM - FM) * DEG2RAD)\
			+ 0.033 * math.sin((2 * DM + FM) * DEG2RAD)\
			+ 0.017 * math.sin((2 * MM + FM) * DEG2RAD)\
			+ 0.009 * math.sin((2 * DM + MM - FM) * DEG2RAD)\
			+ 0.009 * math.sin((2 * MM - FM) * DEG2RAD)

		MLat = math.fmod(EB, 360) # широта
		MLong = math.fmod(LM + EL, 360) # долгота

		RA = math.atan2((math.sin(MLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(MLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(MLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		DEC = math.asin(math.sin(MLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(MLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(MLong * DEG2RAD)) * RAD2DEG # склонение
		if RA < 0:
			RA = RA + 2 * PI
		BETA = math.acos((math.cos(89.55 * DEG2RAD) - math.sin(DEC * DEG2RAD) * math.sin(lat * DEG2RAD)) / (math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD))) * RAD2DEG # часовой угол
		SMR = math.fmod((RA - BETA - STT * 15) / 15 * 0.997269566423530 - zone + long / 15, 24)
		if SMR < 0:
			SMR = SMR + 24
		SMS = math.fmod((RA + BETA - STT * 15) / 15 * 0.997269566423530 - zone + long / 15, 24)
		if SMS < 0:
			SMS = SMS + 24
		if SMR < SMS:
			SMC = (SMR + SMS) / 2
		else:
			SMC = (SMR + SMS) / 2 + 12
			if SMC >= 24:
				SMC = SMC - 24
# Время восхода/захода
		MCh = int(SMC)
		MCm = int(round((SMC - MCh) * 60))
		MRh = int(SMR)
		MRm = int(round(((SMR) - MRh) * 60))
		MSh = int(SMS)
		MSm = int(round(((SMS) - MSh) * 60))
		if MCm == 60:
			MCm = 0
			MCh = MCh + 1
		if MCm < 10:
			MCx = '0'
		else:
			MCx = ''
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
# Азимут
# Орбиты планет
		T = (JD - 2451545) / 36525
		MP1 = 102.27938 + 149472.51529 * T + 0.000007 * T * T
		MP2 = 212.60322 + 58517.80387 * T + 0.001286 * T * T
		MP3 = 358.47583 + 35999.04975 * T - 0.000150 * T * T - 0.0000033 * T * T * T
		MP4 = 319.51913 + 19139.85475 * T + 0.000181 * T * T
		MP5 = 225.32833 + 3034.69202 * T - 0.000722 * T * T
		MP6 = 175.46622 + 1221.55147 * T - 0.000502 * T * T
		MP7 = 72.64878 + 428.37911 * T + 0.000079 * T * T
		MP8 = 37.73063 + 218.46134 * T - 0.000070 * T * T
# Орбита меркурия
		LP1 = 178.179078 + 149474.07078 * T + 0.0003011 * T * T # ср долгота L
		wP1 = 28.753753 + 0.3702806 * T + 0.0001208 * T * T # аргумент перигелия w
		WP1 = 47.145944 + 1.1852083 * T + 0.0001739 * T * T # долгота восходящего узла W
		IP1 = 7.002881 + 0.0018608 * T - 0.0000183 * T * T # наклон на плоскости эклиптики i
		EP1 = 0.20561421 + 0.00002046 * T - 0.000000030 * T * T # эксцентриситет орбиты e

		EL = 0.00204 * math.cos((5 * MP2 - 2 * MP1 + 12.220) * DEG2RAD)\
			 + 0.00103 * math.cos((2 * MP2 - MP1 - 160.692) * DEG2RAD)\
			 + 0.00091 * math.cos((2 * MP5 - MP1 - 37.003) * DEG2RAD)\
			 + 0.00078 * math.cos((5 * MP2 - 3 * MP1 + 10.137) * DEG2RAD)

		LP = LP1 + EL
		M0 = math.fmod(174.795 + 4.092317 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP1 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (0.3870986 * (1 - EP1 * EP1)) / (EP1 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP1 * DEG2RAD) * math.cos((wP1 + MP) * DEG2RAD) - math.sin(WP1 * DEG2RAD) * math.cos(IP1 * DEG2RAD) * math.sin((wP1 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP1 * DEG2RAD) * math.cos((wP1 + MP) * DEG2RAD) + math.cos(WP1 * DEG2RAD) * math.cos(IP1 * DEG2RAD) * math.sin((wP1 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP1 * DEG2RAD) * math.sin((wP1 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P1A = round(AZ, 1)
# Орбита венеры
		LP2 = 342.767053 + 58519.21191 * T + 0.0003097 * T * T # ср долгота L
		wP2 = 54.384186 + 0.5081861 * T - 0.0013864 * T * T # аргумент перигелия w
		WP2 = 75.779647 + 0.8998500 * T + 0.0004100 * T * T # долгота восходящего узла W
		IP2 = 3.393631 + 0.0010058 * T - 0.0000010 * T * T # наклон на плоскости эклиптики i
		EP2 = 0.00682069 - 0.00004774 * T + 0.000000091 * T * T # эксцентриситет орбиты e

		EL = 0.00313 * math.cos((2 * MP3 - 2 * MP2 - 148.225) * DEG2RAD)\
			+ 0.00198 * math.cos((3 * MP3 - 3 * MP2 + 2.565) * DEG2RAD)\
			+ 0.00136 * math.cos((MP3 - MP2 - 119.107) * DEG2RAD)\
			+ 0.00096 * math.cos((3 * MP3 - 2 * MP2 - 135.912) * DEG2RAD)\
			+ 0.00082 * math.cos((MP5 - MP2 - 208.087) * DEG2RAD)

		CP = 0.00077 * math.sin((237.24 + 150.27 * T) * DEG2RAD)

		LP = LP2 + EL + CP
		M0 = math.fmod(50.416 + 1.602136 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP2 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (0.7233316 * (1 - EP2 * EP2)) / (EP2 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP2 * DEG2RAD) * math.cos((wP2 + MP) * DEG2RAD) - math.sin(WP2 * DEG2RAD) * math.cos(IP2 * DEG2RAD) * math.sin((wP2 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP2 * DEG2RAD) * math.cos((wP2 + MP) * DEG2RAD) + math.cos(WP2 * DEG2RAD) * math.cos(IP2 * DEG2RAD) * math.sin((wP2 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP2 * DEG2RAD) * math.sin((wP2 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # гсклонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P2A = round(AZ, 1)
# Орбита марса
		LP4 = 293.737334 + 19141.69551 * T + 0.0003107 * T * T # ср долгота L
		wP4 = 285.431761 + 1.0697667 * T + 0.0001313 * T * T + 0.00000414 * T * T * T # аргумент перигелия w
		WP4 = 48.786442 + 0.7709917 * T - 0.0000014 * T * T - 0.00000533 * T * T * T # долгота восходящего узла W
		IP4 = 1.850333 - 0.0006750 * T + 0.0000126 * T * T # наклон на плоскости эклиптики i
		EP4 = 0.09331290 + 0.000092064 * T - 0.000000077 * T * T # эксцентриситет орбиты e

		EL = 0.00705 * math.cos((MP5 - MP4 - 48.958) * DEG2RAD)\
			+ 0.00607 * math.cos((2 * MP5 - MP4 - 188.350) * DEG2RAD)\
			+ 0.00445 * math.cos((2 * MP5 - 2 * MP4 - 191.897) * DEG2RAD)\
			+ 0.00388 * math.cos((MP3 - 2 * MP4 + 20.495) * DEG2RAD)\
			+ 0.00238 * math.cos((MP3 - MP4 + 35.097) * DEG2RAD)\
			+ 0.00204 * math.cos((2 * MP3 - 3 * MP4 + 158.638) * DEG2RAD)\
			+ 0.00177 * math.cos((3 * MP4 - MP2 - 57.602) * DEG2RAD)\
			+ 0.00136 * math.cos((2 * MP3 - 4 * MP4 + 154.093) * DEG2RAD)\
			+ 0.00104 * math.cos((MP5 + 17.618) * DEG2RAD)

		CP = (- 0.01133 * math.sin((3 * MP5 - 8 * MP4 + 4 * MP3) * DEG2RAD)\
			- 0.00933 * math.cos((3 * MP5 - 8 * MP4 + 4 * MP3) * DEG2RAD)) # уравнение центра

		LP = LP4 + EL + CP
		M0 = math.fmod(19.373 + 0.524039 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP4 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (1.5236883 * (1 - EP4 * EP4)) / (EP4 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP4 * DEG2RAD) * math.cos((wP4 + MP) * DEG2RAD) - math.sin(WP4 * DEG2RAD) * math.cos(IP4 * DEG2RAD) * math.sin((wP4 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP4 * DEG2RAD) * math.cos((wP4 + MP) * DEG2RAD) + math.cos(WP4 * DEG2RAD) * math.cos(IP4 * DEG2RAD) * math.sin((wP4 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP4 * DEG2RAD) * math.sin((wP4 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P4A = round(AZ, 1)
# Орбита юпитера
		LP5 = 238.049257 + 3036.301986 * T + 0.0003347 * T * T - 0.00000165 * T * T * T # ср долгота L
		wP5 = 273.277558 + 0.5994317 * T + 0.00070405 * T * T + 0.00000508 * T * T * T # аргумент перигелия w
		WP5 = 99.443414 + 1.0105300 * T + 0.00035222 * T * T - 0.00000851 * T * T * T # долгота восходящего узла W
		IP5 = 1.308736 - 0.0056961 * T + 0.0000039 * T * T # наклон на плоскости эклиптики i
		EP5 = 0.04833475 + 0.000164180 * T - 0.0000004676 * T * T - 0.0000000017 * T * T * T # эксцентриситет орбиты e

		NJ = T / 5.0 + 0.1
		PJ = 237.47555 + 3034.9061 * T
		QJ = 265.91650 + 1222.1139 * T
		SJ = 243.51721 + 428.4677 * T
		VJ = 5.0 * QJ - 2.0 * PJ
		WJ = 2.0 * PJ - 6.0 * QJ + 3.0 * SJ
		ZJ = QJ - PJ

		EL = (0.331364 - 0.010281 * NJ - 0.004692 * NJ * NJ) * math.sin(VJ * DEG2RAD)\
			+ (0.003228 - 0.064436 * NJ + 0.002075 * NJ * NJ) * math.cos(VJ * DEG2RAD)\
			- (0.003083 + 0.000275 * NJ - 0.000489 * NJ * NJ) * math.sin(2 * VJ * DEG2RAD)\
			+ 0.002472 * math.sin(WJ * DEG2RAD)\
			+ 0.013619 * math.sin(ZJ * DEG2RAD)\
			+ 0.018472 * math.sin(2 * ZJ * DEG2RAD)\
			+ 0.006717 * math.sin(3 * ZJ * DEG2RAD)\
			+ 0.002775 * math.sin(4 * ZJ * DEG2RAD)\
			+ (0.007275 - 0.001253 * NJ) * math.sin(ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			+ 0.006417 * math.sin(2 * ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			+ 0.002439 * math.sin(3 * ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)

		EL = EL - (0.033839 + 0.001125 * NJ) * math.cos(ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			- 0.003767 * math.cos(2 * ZJ * DEG2RAD) * math.sin(QJ * DEG2RAD)\
			- (0.035681 + 0.001208 * NJ) * math.sin(ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.004261 * math.sin(2 * ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			+ 0.002178 * math.cos(QJ * DEG2RAD)\
			+ (-0.006333 + 0.001161 * NJ) * math.cos(ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.006675 * math.cos(2 * ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.002664 * math.cos(3 * ZJ * DEG2RAD) * math.cos(QJ * DEG2RAD)\
			- 0.002572 * math.sin(ZJ * DEG2RAD) * math.sin(2 * QJ * DEG2RAD)\
			- 0.003567 * math.sin(2 * ZJ * DEG2RAD) * math.sin(2 * QJ * DEG2RAD)\
			+ 0.002094 * math.cos(ZJ * DEG2RAD) * math.cos(2 * QJ * DEG2RAD)\
			+ 0.003342 * math.cos(2 * ZJ * DEG2RAD) * math.cos(2 * QJ * DEG2RAD)

		LP = LP5 + EL
		M0 = math.fmod(20.020 + 0.083056 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP5 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (5.202561 * (1 - EP5 * EP5)) / (EP5 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP5 * DEG2RAD) * math.cos((wP5 + MP) * DEG2RAD) - math.sin(WP5 * DEG2RAD) * math.cos(IP5 * DEG2RAD) * math.sin((wP5 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP5 * DEG2RAD) * math.cos((wP5 + MP) * DEG2RAD) + math.cos(WP5 * DEG2RAD) * math.cos(IP5 * DEG2RAD) * math.sin((wP5 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP5 * DEG2RAD) * math.sin((wP5 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P5A = round(AZ, 1)
# Орбита сатурна
		LP6 = 266.564377 + 1223.509884 * T + 0.0003245 * T * T - 0.0000058 * T * T * T # ср долгота L
		wP6 = 338.307800 + 1.0852207 * T + 0.00097854 * T * T + 0.00000992 * T * T * T # аргумент перигелия w
		WP6 = 112.790414 + 0.8731951 * T - 0.00015218 * T * T - 0.00000531 * T * T * T # долгота восходящего узла W
		IP6 = 2.492519 - 0.0039189 * T - 0.00001549 * T * T + 0.00000004 * T * T * T # наклон на плоскости эклиптики i
		EP6 = 0.05589232 - 0.00034550 * T - 0.000000728 * T * T + 0.00000000074 * T * T * T # эксцентриситет орбиты e

		NS = T / 5.0 + 0.1
		PS = 237.47555 + 3034.9061 * T
		QS = 265.91650 + 1222.1139 * T
		SS = 243.51721 + 428.4677 * T
		VS = 5.0 * QS - 2.0 * PS
		WS = 2.0 * PS - 6.0 * QS + 3.0 * SS
		ZS = QS - PS
		PSI = SS - QS

		EL = (-0.814181 + 0.018150 * NS + 0.016714 * NS * NS) * math.sin(VS * DEG2RAD)\
			+ (-0.010497 + 0.160906 * NS - 0.004100 * NS * NS) * math.cos(VS * DEG2RAD)\
			+ 0.007581 * math.sin(2 * VS * DEG2RAD)\
			- 0.007986 * math.sin(WS * DEG2RAD)\
			- 0.148811 * math.sin(ZS * DEG2RAD)\
			- 0.040786 * math.sin(2 * ZS * DEG2RAD)\
			- 0.015208 * math.sin(3 * ZS * DEG2RAD)\
			- 0.006339 * math.sin(4 * ZS * DEG2RAD)\
			- 0.006244 * math.sin(QS * DEG2RAD)

		EL = EL + (0.008931 + 0.002728 * NS) * math.sin(ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			- 0.016500 * math.sin(2 * ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			- 0.005775 * math.sin(3 * ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			+ (0.081344 + 0.003206 * NS) * math.cos(ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			+ 0.015019 * math.cos(2 * ZS * DEG2RAD) * math.sin(QS * DEG2RAD)\
			+ (0.085581 + 0.002494 * NS) * math.sin(ZS * DEG2RAD) * math.cos(QS * DEG2RAD)\
			+ (0.025328 - 0.003117 * NS) * math.cos(ZS * DEG2RAD) * math.cos(QS * DEG2RAD)

		EL = EL + 0.014394 * math.cos(2 * ZS * DEG2RAD) * math.cos(QS * DEG2RAD)\
			+ 0.006319 * math.cos(3 * ZS * DEG2RAD) * math.cos(QS * DEG2RAD)\
			+ 0.006369 * math.sin(ZS * DEG2RAD) * math.sin(2 * QS * DEG2RAD)\
			+ 0.009156 * math.sin(2 * ZS * DEG2RAD) * math.sin(2 * QS * DEG2RAD)\
			+ 0.007525 * math.sin(3 * PSI * DEG2RAD) * math.sin(2 * QS * DEG2RAD)\
			- 0.005236 * math.cos(ZS * DEG2RAD) * math.cos(2 * QS * DEG2RAD)\
			- 0.007736 * math.cos(2 * ZS * DEG2RAD) * math.cos(2 * QS * DEG2RAD)\
			- 0.007528 * math.cos(3 * PSI * DEG2RAD) * math.cos(2 * QS * DEG2RAD)

		LP = LP6 + EL
		M0 = math.fmod(317.021 + 0.033371 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP6 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (9.554747 * (1 - EP6 * EP6)) / (EP6 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP6 * DEG2RAD) * math.cos((wP6 + MP) * DEG2RAD) - math.sin(WP6 * DEG2RAD) * math.cos(IP6 * DEG2RAD) * math.sin((wP6 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP6 * DEG2RAD) * math.cos((wP6 + MP) * DEG2RAD) + math.cos(WP6 * DEG2RAD) * math.cos(IP6 * DEG2RAD) * math.sin((wP6 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP6 * DEG2RAD) * math.sin((wP6 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P6A = round(AZ, 1)
# Орбита урана
		LP7 = 244.197470 + 429.863546 * T + 0.0003160 * T * T - 0.00000060 * T * T * T # ср долгота L
		wP7 = 98.071581 + 0.9857650 * T - 0.0010745 * T * T - 0.00000061 * T * T * T # аргумент перигелия w
		WP7 = 73.477111 + 0.4986678 * T + 0.0013117 * T * T # долгота восходящего узла W
		IP7 = 0.772464 + 0.0006253 * T + 0.0000395 * T * T # наклон на плоскости эклиптики i
		EP7 = 0.0463444 - 0.00002658 * T + 0.000000077 * T * T # эксцентриситет орбиты e

		NU = T / 5.0 + 0.1
		PU = 237.47555 + 3034.9061 * T
		QU = 265.91650 + 1222.1139 * T
		SU = 243.51721 + 428.4677 * T
		GU = 83.76922 + 218.4901 * T
		WU = 2.0 * PU - 6.0 * QU + 3.0 * SU
		HU = 2.0 * GU - SU

		EL = (0.864319 - 0.001583 * NU) * math.sin(HU * DEG2RAD)\
			+ (0.082222 - 0.006833 * NU) * math.cos(HU * DEG2RAD)\
			+ 0.036017 * math.sin(2 * HU * DEG2RAD)\
			- 0.003019 * math.cos(2 * HU * DEG2RAD)\
			+ 0.008122 * math.sin(WU)

		LP = LP7 + EL
		M0 = math.fmod(141.050 + 0.011698 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP7 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (19.21814 * (1 - EP7 * EP7)) / (EP7 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP7 * DEG2RAD) * math.cos((wP7 + MP) * DEG2RAD) - math.sin(WP7 * DEG2RAD) * math.cos(IP7 * DEG2RAD) * math.sin((wP7 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP7 * DEG2RAD) * math.cos((wP7 + MP) * DEG2RAD) + math.cos(WP7 * DEG2RAD) * math.cos(IP7 * DEG2RAD) * math.sin((wP7 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP7 * DEG2RAD) * math.sin((wP7 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P7A = round(AZ, 1)
# Орбита нептуна
#		AP8 = 30.10957 # большая полуось орбиты a
		LP8 = 84.457994 + 219.885914 * T + 0.0003205 * T * T - 0.00000060 * T * T * T # ср долгота L
		wP8 = 276.045975 + 0.3256394 * T + 0.00014095 * T * T + 0.000004113 * T * T * T # аргумент перигелия w
		WP8 = 130.681389 + 1.0989350 * T + 0.00024987 * T * T - 0.000004718 * T * T * T # долгота восходящего узла W
		IP8 = 1.779242 - 0.0095436 * T - 0.0000091 * T * T # наклон на плоскости эклиптики i
		EP8 = 0.00899704 + 0.000006330 * T - 0.000000002 * T * T # эксцентриситет орбиты e

		NN = T / 5.0 + 0.1
		SN = 243.51721 + 428.4677 * T
		GN = 83.76922 + 218.4901 * T
		HN = 2.0 * GN - SN

		EL = (-0.589833 + 0.001089 * NN) * math.sin(HN * DEG2RAD)\
			+ (-0.056094 + 0.004658 * NN) * math.cos(HN * DEG2RAD)\
			- 0.024286 * math.sin(2 * HN * DEG2RAD)

		LP = LP8 + EL
		M0 = math.fmod(256.225 + 0.005965 * (JDN - 2451545), 360) # ср аномалия
		MP = M0 - EP8 * math.sin(M0 * DEG2RAD) # уравнение Кеплера
		DP = (30.10957 * (1 - EP8 * EP8)) / (EP8 * math.cos((MP + LP) * DEG2RAD) + 1) # расстояние до солнца в а.е.
		# гелиоцентрические координаты
		XP = DP * (math.cos(WP8 * DEG2RAD) * math.cos((wP8 + MP) * DEG2RAD) - math.sin(WP8 * DEG2RAD) * math.cos(IP8 * DEG2RAD) * math.sin((wP8 + MP) * DEG2RAD))
		YP = DP * (math.sin(WP8 * DEG2RAD) * math.cos((wP8 + MP) * DEG2RAD) + math.cos(WP8 * DEG2RAD) * math.cos(IP8 * DEG2RAD) * math.sin((wP8 + MP) * DEG2RAD))
		ZP = DP * math.sin(IP8 * DEG2RAD) * math.sin((wP8 + MP) * DEG2RAD)
		# геоцентрические координаты
		XP = XP - XE
		YP = YP - YE
		ZP = ZP
		# эклиптические координаты
		PLong =  math.atan2(YP, XP) * RAD2DEG
		PLat = math.asin(ZP / math.sqrt(XP * XP + YP * YP + ZP * ZP)) * RAD2DEG

		RA = math.atan2((math.sin(PLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(PLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(PLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(PLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(PLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		P8A = round(AZ, 1)
# Фазы луны, расстояние до луны, азимут луны
		LM = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T * T * T / 538841 - T * T * T * T / 65194000 # ср долгота луны
		FM = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T - T * T * T / 3526000 + T * T * T * T / 863310000 # ср аргумент широты луны
		DM = 297.8501921 + 445267.114034 * T - 0.0018819 * T * T + T * T * T / 545868 - T * T * T * T / 113065000 # ср элонгация луны
		MS = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T * T * T / 24490000 # ср солнечная аномалия
		MM = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T * T * T / 69699 - T * T * T * T / 14712000 # ср лунная аномалия
		EM = 1 - 0.002516 * T - 0.0000074 * T * T # поправка на изменяющийся эксцентриситет

		EL = 6.289 * math.sin(MM * DEG2RAD)\
			+ 1.274 * math.sin((2 * DM - MM) * DEG2RAD)\
			+ 0.658 * math.sin(2 * DM * DEG2RAD)\
			+ 0.214 * math.sin(2 * MM * DEG2RAD)\
			- 0.186 * math.sin(MS * DEG2RAD)\
			- 0.114 * math.sin(2 * FM * DEG2RAD)\
			+ 0.059 * math.sin((2 * DM - 2 * MM) * DEG2RAD)\
			+ 0.057 * math.sin((2 * DM - MS - MM) * DEG2RAD)\
			+ 0.053 * math.sin((2 * DM + MM) * DEG2RAD)\
			+ 0.046 * math.sin((2 * DM - MS) * DEG2RAD)\
			- 0.041 * math.sin((MS - MM) * DEG2RAD)\
			- 0.035 * math.sin(DM * DEG2RAD)\
			- 0.030 * math.sin((MS + MM) * DEG2RAD)

		EB = 5.128 * math.sin(FM * DEG2RAD)\
			+ 0.281 * math.sin((MM + FM) * DEG2RAD)\
			+ 0.278 * math.sin((MM - FM) * DEG2RAD)\
			+ 0.173 * math.sin((2 * DM - FM) * DEG2RAD)\
			+ 0.055 * math.sin((2 * DM - MM + FM) * DEG2RAD)\
			+ 0.046 * math.sin((2 * DM - MM - FM) * DEG2RAD)\
			+ 0.033 * math.sin((2 * DM + FM) * DEG2RAD)\
			+ 0.017 * math.sin((2 * MM + FM) * DEG2RAD)\
			+ 0.009 * math.sin((2 * DM + MM - FM) * DEG2RAD)\
			+ 0.009 * math.sin((2 * MM - FM) * DEG2RAD)

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
			- 0.010445 * math.cos((2 * DM + 2 * MM) * DEG2RAD)

		IM = 180 - DM\
			- 6.289 * math.sin(MM * DEG2RAD)\
			+ 2.100 * math.sin(MS * DEG2RAD)\
			- 1.274 * math.sin((2 * DM - MM) * DEG2RAD)\
			- 0.658 * math.sin(2 * DM * DEG2RAD)\
			- 0.214 * math.sin(2 * MM * DEG2RAD)\
			- 0.114 * math.sin(DM * DEG2RAD)
		pha1 = (1 + math.cos(IM * DEG2RAD)) / 2

		MLat = math.fmod(EB, 360) # широта
		MLong = math.fmod(LM + EL, 360) # долгота

		Mdist = int(385000.56 + ER * 1000) # расстояние до луны км
		RA = math.atan2((math.sin(MLong * DEG2RAD) * math.cos(EPS * DEG2RAD) - math.tan(MLat * DEG2RAD) * math.sin(EPS * DEG2RAD)) , math.cos(MLong * DEG2RAD)) * RAD2DEG # прямое восхождение
		if RA < 0:
			RA = RA + 2 * PI
		DEC = math.asin(math.sin(MLat * DEG2RAD) * math.cos(EPS * DEG2RAD) + math.cos(MLat * DEG2RAD) * math.sin(EPS * DEG2RAD) * math.sin(MLong * DEG2RAD)) * RAD2DEG # склонение
		TH = ST - RA
		Z  = math.acos(math.sin(lat * DEG2RAD) * math.sin(DEC * DEG2RAD) + math.cos(lat * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(TH * DEG2RAD)) * RAD2DEG # косинус зенитного угла
		H = 90 - Z # угол места
		AZ = math.atan2(math.sin(TH * DEG2RAD) * math.cos(DEC * DEG2RAD) * math.cos(lat * DEG2RAD), math.sin(H * DEG2RAD) * math.sin(lat * DEG2RAD) - math.sin(DEC * DEG2RAD)) * RAD2DEG + 180 # азимут + 180
		MA = round(AZ, 1)
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
			self.sunculmination['Solstice'] = '%s%s%s%s' % (SCh, unichr(58).encode("latin-1"), SCx, SCm)
			self.mercuryrise['Mercuryrise'] = '%s%s%s%s' % (P1Rh, unichr(58).encode("latin-1"), P1Rx, P1Rm)
			self.mercuryset['Mercuryset'] = '%s%s%s%s' % (P1Sh, unichr(58).encode("latin-1"), P1Sx, P1Sm)
			self.mercuryculmination['Mercuryculmination'] = '%s%s%s%s' % (P1Ch, unichr(58).encode("latin-1"), P1Cx, P1Cm)
			self.mercuryazimuth['Mercuryazimuth'] = '%s %s' % (P1A, unichr(176).encode("latin-1"))
			self.venusrise['Venusrise'] = '%s%s%s%s' % (P2Rh, unichr(58).encode("latin-1"), P2Rx, P2Rm)
			self.venusset['Venusset'] = '%s%s%s%s' % (P2Sh, unichr(58).encode("latin-1"), P2Sx, P2Sm)
			self.venusculmination['Venusculmination'] = '%s%s%s%s' % (P2Ch, unichr(58).encode("latin-1"), P2Cx, P2Cm)
			self.venusazimuth['Venusazimuth'] = '%s %s' % (P2A, unichr(176).encode("latin-1"))
			self.marsrise['Marsrise'] = '%s%s%s%s' % (P4Rh, unichr(58).encode("latin-1"), P4Rx, P4Rm)
			self.marsset['Marsset'] = '%s%s%s%s' % (P4Sh, unichr(58).encode("latin-1"), P4Sx, P4Sm)
			self.marsculmination['Marsculmination'] = '%s%s%s%s' % (P4Ch, unichr(58).encode("latin-1"), P4Cx, P4Cm)
			self.marsazimuth['Marsazimuth'] = '%s %s' % (P4A, unichr(176).encode("latin-1"))
			self.jupiterrise['Jupiterrise'] = '%s%s%s%s' % (P5Rh, unichr(58).encode("latin-1"), P5Rx, P5Rm)
			self.jupiterset['Jupiterset'] = '%s%s%s%s' % (P5Sh, unichr(58).encode("latin-1"), P5Sx, P5Sm)
			self.jupiterculmination['Jupiterculmination'] = '%s%s%s%s' % (P5Ch, unichr(58).encode("latin-1"), P5Cx, P5Cm)
			self.jupiterazimuth['Jupiterazimuth'] = '%s %s' % (P5A, unichr(176).encode("latin-1"))
			self.saturnrise['Saturnrise'] = '%s%s%s%s' % (P6Rh, unichr(58).encode("latin-1"), P6Rx, P6Rm)
			self.saturnset['Saturnset'] = '%s%s%s%s' % (P6Sh, unichr(58).encode("latin-1"), P6Sx, P6Sm)
			self.saturnculmination['Saturnculmination'] = '%s%s%s%s' % (P6Ch, unichr(58).encode("latin-1"), P6Cx, P6Cm)
			self.saturnazimuth['Saturnazimuth'] = '%s %s' % (P6A, unichr(176).encode("latin-1"))
			self.uranusrise['Uranusrise'] = '%s%s%s%s' % (P7Rh, unichr(58).encode("latin-1"), P7Rx, P7Rm)
			self.uranusset['Uranusset'] = '%s%s%s%s' % (P7Sh, unichr(58).encode("latin-1"), P7Sx, P7Sm)
			self.uranusculmination['Uranusculmination'] = '%s%s%s%s' % (P7Ch, unichr(58).encode("latin-1"), P7Cx, P7Cm)
			self.uranusazimuth['Uranusazimuth'] = '%s %s' % (P7A, unichr(176).encode("latin-1"))
			self.neptunerise['Neptunerise'] = '%s%s%s%s' % (P8Rh, unichr(58).encode("latin-1"), P8Rx, P8Rm)
			self.neptuneset['Neptuneset'] = '%s%s%s%s' % (P8Sh, unichr(58).encode("latin-1"), P8Sx, P8Sm)
			self.neptuneculmination['Neptuneculmination'] = '%s%s%s%s' % (P8Ch, unichr(58).encode("latin-1"), P8Cx, P8Cm)
			self.neptuneazimuth['Neptuneazimuth'] = '%s %s' % (P8A, unichr(176).encode("latin-1"))
			self.moondist['Moondist'] = _('%s km') % Mdist
			self.moonazimuth['Moonazimuth'] = '%s %s' % (MA, unichr(176).encode("latin-1"))
			self.moonrise['Moonrise'] = '%s%s%s%s' % (MRh, unichr(58).encode("latin-1"), MRx, MRm)
			self.moonset['Moonset'] = '%s%s%s%s' % (MSh, unichr(58).encode("latin-1"), MSx, MSm)
			self.moonculmination['Moonculmination'] = '%s%s%s%s' % (MCh, unichr(58).encode("latin-1"), MCx, MCm)
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
# Астро
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
		if self.sunculmination['Solstice'] is not '':
			self["sunculmination"].text = '%s' % self.sunculmination['Solstice']
		else:
			self["sunculmination"].text = _('n/a')
			self.notdata = True
		if self.mercuryrise['Mercuryrise'] is not '':
			self["mercuryrise"].text = '%s' % self.mercuryrise['Mercuryrise']
		else:
			self["mercuryrise"].text = _('n/a')
			self.notdata = True
		if self.mercuryset['Mercuryset'] is not '':
			self["mercuryset"].text = '%s' % self.mercuryset['Mercuryset']
		else:
			self["mercuryset"].text = _('n/a')
			self.notdata = True
		if self.mercuryculmination['Mercuryculmination'] is not '':
			self["mercuryculmination"].text = '%s' % self.mercuryculmination['Mercuryculmination']
		else:
			self["mercuryculmination"].text = _('n/a')
			self.notdata = True
		if self.mercuryazimuth['Mercuryazimuth'] is not '':
			self["mercuryazimuth"].text = '%s' % self.mercuryazimuth['Mercuryazimuth']
		else:
			self["mercuryazimuth"].text = _('n/a')
			self.notdata = True
		if self.venusrise['Venusrise'] is not '':
			self["venusrise"].text = '%s' % self.venusrise['Venusrise']
		else:
			self["venusrise"].text = _('n/a')
			self.notdata = True
		if self.venusset['Venusset'] is not '':
			self["venusset"].text = '%s' % self.venusset['Venusset']
		else:
			self["venusset"].text = _('n/a')
			self.notdata = True
		if self.venusculmination['Venusculmination'] is not '':
			self["venusculmination"].text = '%s' % self.venusculmination['Venusculmination']
		else:
			self["venusculmination"].text = _('n/a')
			self.notdata = True
		if self.venusazimuth['Venusazimuth'] is not '':
			self["venusazimuth"].text = '%s' % self.venusazimuth['Venusazimuth']
		else:
			self["venusazimuth"].text = _('n/a')
			self.notdata = True
		if self.marsrise['Marsrise'] is not '':
			self["marsrise"].text = '%s' % self.marsrise['Marsrise']
		else:
			self["marsrise"].text = _('n/a')
			self.notdata = True
		if self.marsset['Marsset'] is not '':
			self["marsset"].text = '%s' % self.marsset['Marsset']
		else:
			self["marsset"].text = _('n/a')
			self.notdata = True
		if self.marsculmination['Marsculmination'] is not '':
			self["marsculmination"].text = '%s' % self.marsculmination['Marsculmination']
		else:
			self["marsculmination"].text = _('n/a')
			self.notdata = True
		if self.marsazimuth['Marsazimuth'] is not '':
			self["marsazimuth"].text = '%s' % self.marsazimuth['Marsazimuth']
		else:
			self["marsazimuth"].text = _('n/a')
			self.notdata = True
		if self.jupiterrise['Jupiterrise'] is not '':
			self["jupiterrise"].text = '%s' % self.jupiterrise['Jupiterrise']
		else:
			self["jupiterrise"].text = _('n/a')
			self.notdata = True
		if self.jupiterset['Jupiterset'] is not '':
			self["jupiterset"].text = '%s' % self.jupiterset['Jupiterset']
		else:
			self["jupiterset"].text = _('n/a')
			self.notdata = True
		if self.jupiterculmination['Jupiterculmination'] is not '':
			self["jupiterculmination"].text = '%s' % self.jupiterculmination['Jupiterculmination']
		else:
			self["jupiterculmination"].text = _('n/a')
			self.notdata = True
		if self.jupiterazimuth['Jupiterazimuth'] is not '':
			self["jupiterazimuth"].text = '%s' % self.jupiterazimuth['Jupiterazimuth']
		else:
			self["jupiterazimuth"].text = _('n/a')
			self.notdata = True
		if self.saturnrise['Saturnrise'] is not '':
			self["saturnrise"].text = '%s' % self.saturnrise['Saturnrise']
		else:
			self["saturnrise"].text = _('n/a')
			self.notdata = True
		if self.saturnset['Saturnset'] is not '':
			self["saturnset"].text = '%s' % self.saturnset['Saturnset']
		else:
			self["saturnset"].text = _('n/a')
			self.notdata = True
		if self.saturnculmination['Saturnculmination'] is not '':
			self["saturnculmination"].text = '%s' % self.saturnculmination['Saturnculmination']
		else:
			self["saturnculmination"].text = _('n/a')
			self.notdata = True
		if self.saturnazimuth['Saturnazimuth'] is not '':
			self["saturnazimuth"].text = '%s' % self.saturnazimuth['Saturnazimuth']
		else:
			self["saturnazimuth"].text = _('n/a')
			self.notdata = True
		if self.uranusrise['Uranusrise'] is not '':
			self["uranusrise"].text = '%s' % self.uranusrise['Uranusrise']
		else:
			self["uranusrise"].text = _('n/a')
			self.notdata = True
		if self.uranusset['Uranusset'] is not '':
			self["uranusset"].text = '%s' % self.uranusset['Uranusset']
		else:
			self["uranusset"].text = _('n/a')
			self.notdata = True
		if self.uranusculmination['Uranusculmination'] is not '':
			self["uranusculmination"].text = '%s' % self.uranusculmination['Uranusculmination']
		else:
			self["uranusculmination"].text = _('n/a')
			self.notdata = True
		if self.uranusazimuth['Uranusazimuth'] is not '':
			self["uranusazimuth"].text = '%s' % self.uranusazimuth['Uranusazimuth']
		else:
			self["uranusazimuth"].text = _('n/a')
			self.notdata = True
		if self.neptunerise['Neptunerise'] is not '':
			self["neptunerise"].text = '%s' % self.neptunerise['Neptunerise']
		else:
			self["neptunerise"].text = _('n/a')
			self.notdata = True
		if self.neptuneset['Neptuneset'] is not '':
			self["neptuneset"].text = '%s' % self.neptuneset['Neptuneset']
		else:
			self["neptuneset"].text = _('n/a')
			self.notdata = True
		if self.neptuneculmination['Neptuneculmination'] is not '':
			self["neptuneculmination"].text = '%s' % self.neptuneculmination['Neptuneculmination']
		else:
			self["neptuneculmination"].text = _('n/a')
			self.notdata = True
		if self.neptuneazimuth['Neptuneazimuth'] is not '':
			self["neptuneazimuth"].text = '%s' % self.neptuneazimuth['Neptuneazimuth']
		else:
			self["neptuneazimuth"].text = _('n/a')
			self.notdata = True
		if self.moondist['Moondist'] is not '':
			self["moondist"].text = '%s' % self.moondist['Moondist']
		else:
			self["moondist"].text = _('n/a')
			self.notdata = True
		if self.moonazimuth['Moonazimuth'] is not '':
			self["moonazimuth"].text = '%s' % self.moonazimuth['Moonazimuth']
		else:
			self["moonazimuth"].text = _('n/a')
			self.notdata = True
		if self.moonculmination['Moonculmination'] is not '':
			self["moonculmination"].text = '%s' % self.moonculmination['Moonculmination']
		else:
			self["moonculmination"].text = _('n/a')
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
		self.session.open(MessageBox, _("Weather MSN \nDeveloper: Sirius0103 \nHomepage: www.gisclub.tv \nGithub: www.github.com/Sirius0103 \n\nDonate: \nR460680746216 \nZ395874509364 \nE284580190260"), MessageBox.TYPE_INFO)

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
				locationcode = "%s,%s" % (childs.attrib.get('weatherlocationname').encode('utf-8', 'ignore'), childs.attrib.get('region').encode('utf-8', 'ignore'))
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
		description=_("Weather forecast, astronomical calculations"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="plugin.png",
		fnc=main)
		]
		return result
	else:
		result = [
		PluginDescriptor(name=_("Weather MSN"),
		description=_("Weather forecast, astronomical calculations"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="plugin.png",
		fnc=main)
		]
		return result
