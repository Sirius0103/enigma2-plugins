# -*- coding: UTF-8 -*-

# Plugin - DownSkinLIB
# Developer - Sirius
# Homepage - http://www.gisclub.Tv
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

import urllib3
import requests
import os, gettext
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Language import language
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_LANGUAGE
from Tools.LoadPixmap import LoadPixmap
from requests.exceptions import HTTPError
from os import system, environ
from enigma import getDesktop

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("DownSkinLIB", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/DownSkinLIB/locale"))

def _(txt):
	t = gettext.dgettext("DownSkinLIB", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

if getDesktop(0).size().width() >= 1920: #FHD
	SKIN_SKINLIB = """
		<!-- Download SkinLIB -->
		<screen name="DownSkinLIB" position="60,55" size="1800,1000" title="Download SkinLIB">
			<eLabel position="20,950" size="1760,3" backgroundColor="#00555555" zPosition="1" />

			<widget name="info_conv_l" position="20,20" size="500,800" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_conv_r" position="540,20" size="500,800" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_rend" position="1060,20" size="500,800" font="Regular; 25" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_git" position="20,840" size="1760,60" font="Regular; 25" foregroundColor="#008f8f8f" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_pl" position="20,910" size="1760,30" font="Regular; 25" foregroundColor="#008f8f8f" backgroundColor="background" halign="left" transparent="1" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_epg.png" position="1720,965" size="40,20" alphatest="on" />
			<widget source="key_red" render="Label" position="70,960" size="280,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_green" render="Label" position="410,960" size="280,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_yellow" render="Label" position="750,960" size="280,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_blue" render="Label" position="1090,960" size="280,30" font="Regular; 25" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_red.png" position="20,965" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_green.png" position="360,965" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_yellow.png" position="700,965" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_blue.png" position="1040,965" size="40,20" alphatest="blend" />
		</screen>"""
else: #HD
	SKIN_SKINLIB = """
		<!-- Download SkinLIB -->
		<screen name="DownSkinLIB" position="40,55" size="1200,650" title="Download SkinLIB">
			<eLabel position="20,610" size="1160,3" backgroundColor="#00555555" zPosition="1" />

			<widget name="info_conv_l" position="10,10" size="300,500" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_conv_r" position="320,10" size="300,500" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_rend" position="630,10" size="300,500" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_git" position="10,520" size="1180,50" font="Regular; 20" foregroundColor="#008f8f8f" backgroundColor="background" halign="left" transparent="1" />
			<widget name="info_pl" position="10,580" size="1180,25" font="Regular; 20" foregroundColor="#008f8f8f" backgroundColor="background" halign="left" transparent="1" />

			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_epg.png" position="1140,620" size="40,20" alphatest="on" />
			<widget source="key_red" render="Label" position="65,615" size="230,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_green" render="Label" position="345,615" size="230,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_yellow" render="Label" position="625,615" size="230,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<widget source="key_blue" render="Label" position="905,616" size="230,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_red.png" position="20,620" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_green.png" position="300,620" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_yellow.png" position="580,620" size="40,20" alphatest="blend" />
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DownSkinLIB/buttons/key_blue.png" position="860,620" size="40,20" alphatest="blend" />
		</screen>"""

class DownSkinLIB(Screen):
	def __init__(self, session):

		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_SKINLIB

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "EPGSelectActions"],
		{
			"cancel": self.exit,
			"red": self.exit,
			"yellow": self.download_pl,
			"blue": self.download_com,
			"info": self.about
		}, -1)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_(" "))
		self["key_yellow"] = StaticText(_("Update plugin"))
		self["key_blue"] = StaticText(_("Update library"))
		self["Title"] = StaticText(_("Download SkinLIB"))

		self["info_pl"] = Label(_(" "))
		self["info_git"] = Label(_(" "))
		self["info_conv_l"] = Label(_(" "))
		self["info_conv_r"] = Label(_(" "))
		self["info_rend"] = Label(_(" "))

		self.infocom()
		self.version()
		self.infopl()

	def version(self):
		try:
			file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-plugins/master/python/Plugins/Extensions/DownSkinLIB/version").text
			f = open("/tmp/version", "w")
			f.write(file)
			f.close()
			self.infogit()
		except:
			pass

	def infogit(self):
		version = ""
		try:
			for text in open("/tmp/version").readlines()[3]:
				version += text
			self["info_git"].setText(version)
			return version
		except:
			return ""

	def infopl(self):
		pluginpath = "/usr/lib/enigma2/python/Plugins/Extensions/"
		version = ""
		try:
			for text in open("%sDownSkinLIB/version" % (pluginpath)).readlines()[1]:
				version += text
			self["info_pl"].setText(version)
			return version
		except:
			return ""

	def infocom(self):
		lib = "Converter:\
			\n   AC3DownMixStatus.py\
			\n   AlwaysTrue.py\
			\n   Bitrate2.py\
			\n   CaidBar.py\
			\n   CaidInfo2.py\
			\n   CamdInfo3.py\
			\n   ConverterRotator.py\
			\n   CpuUsage.py\
			\n   DiskInfo.py\
			\n   EcmInfoLine.py\
			\n   EmuName.py\
			\n   EventName2.py\
			\n   ExtraNumText.py\
			\n   FanTempInfo.py\
			\n   FlashingDotClock.py\
			\n   FrontendInfo2.py\
			\n   IsNet.py\
			\n   MemoryInfo.py\
			\n   ModuleControl.py\
			\n   MovieInfo2.py\
			"
		self["info_conv_l"].setText(lib)

		lib = "...\
			\n   ProgressDiskSpaceInfo.py\
			\n   RefString.py\
			\n   RouteInfo.py\
			\n   ServiceInfo2.py\
			\n   ServiceInfoEX.py\
			\n   ServiceName2.py\
			\n   ServiceOrbitalPosition2.py\
			\n   TunerBar.py\
			\n   WiFiInfo.py\
			"
		self["info_conv_r"].setText(lib)

		lib = "Renderer:\
			\n   AnimatedWeatherPixmap.py\
			\n   AnimatedMoonPixmap.py\
			\n   LabelDuoColors.py\
			\n   MovieCover.py\
			\n   MovieRating.py\
			\n   PiconUni.py\
			\n   RendVolumeText.py\
			\n   RendVolumeTextP.py\
			\n   RunningText.py\
			\n   Watches.py\
			"
		self["info_rend"].setText(lib)

	def install_pl(self):
		pluginpath = "/usr/lib/enigma2/python/Plugins/Extensions/"
		if fileExists ("/tmp/version"\
			and "/tmp/plugin.py"\
			and "/tmp/ruDownSkinLIB.mo"\
			and "/tmp/deDownSkinLIB.mo"\
			and "/tmp/ukDownSkinLIB.mo"):

			os.system("cp /tmp/version %sDownSkinLIB/version" % (pluginpath))
	# install plugin
			os.system("cp /tmp/plugin.py %sDownSkinLIB/plugin.py" % (pluginpath))
			os.system("cp /tmp/ruDownSkinLIB.mo %sDownSkinLIB/locale/ru/LC_MESSAGES/DownSkinLIB.mo" % (pluginpath))
			os.system("cp /tmp/deDownSkinLIB.mo %sDownSkinLIB/locale/de/LC_MESSAGES/DownSkinLIB.mo" % (pluginpath))
			os.system("cp /tmp/ukDownSkinLIB.mo %sDownSkinLIB/locale/uk/LC_MESSAGES/DownSkinLIB.mo" % (pluginpath))
	# end
			self.session.openWithCallback(self.restart, MessageBox,_("Do you want to restart the GUI now ?"), MessageBox.TYPE_YESNO)
		else:
			self.session.open(MessageBox,(_("Download failed, check your internet connection !!!")), MessageBox.TYPE_INFO, timeout = 10)

	def install_com(self):
		pluginpath = "/usr/lib/enigma2/python/Plugins/Extensions/"
		componentspath = "/usr/lib/enigma2/python/Components/"
		if fileExists ("/tmp/version"\
	# converter
			and "/tmp/AC3DownMixStatus.py"\
			and "/tmp/AlwaysTrue.py"\
			and "/tmp/Bitrate2.py"\
			and "/tmp/CaidBar.py"\
			and "/tmp/CaidInfo2.py"\
			and "/tmp/CamdInfo3.py"\
			and "/tmp/ConverterRotator.py"\
			and "/tmp/CpuUsage.py"\
			and "/tmp/DiskInfo.py"\
			and "/tmp/EcmInfoLine.py"\
			and "/tmp/EmuName.py"\
			and "/tmp/EventName2.py"\
			and "/tmp/ExtraNumText.py"\
			and "/tmp/FanTempInfo.py"\
			and "/tmp/FlashingDotClock.py"\
			and "/tmp/FrontendInfo2.py"\
			and "/tmp/IsNet.py"\
			and "/tmp/MemoryInfo.py"\
			and "/tmp/ModuleControl.py"\
			and "/tmp/MovieInfo2.py"\
			and "/tmp/ProgressDiskSpaceInfo.py"\
			and "/tmp/RefString.py"\
			and "/tmp/RouteInfo.py"\
			and "/tmp/ServiceInfo2.py"\
			and "/tmp/ServiceInfoEX.py"\
			and "/tmp/ServiceName2.py"\
			and "/tmp/ServiceName2.ref"\
			and "/tmp/ServiceOrbitalPosition2.py"\
			and "/tmp/TunerBar.py"\
			and "/tmp/WiFiInfo.py"\
	# renderer
			and "/tmp/AnimatedWeatherPixmap.py"\
			and "/tmp/AnimatedMoonPixmap.py"\
			and "/tmp/LabelDuoColors.py"\
			and "/tmp/MovieCover.py"\
			and "/tmp/MovieRating.py"\
			and "/tmp/PiconUni.py"\
			and "/tmp/RendVolumeText.py"\
			and "/tmp/RendVolumeTextP.py"\
			and "/tmp/RunningText.py"\
			and "/tmp/Watches.py"):

			os.system("cp /tmp/version %sDownSkinLIB/version" % (pluginpath))
	# install converter
			os.system("cp /tmp/AC3DownMixStatus.py %sConverter/AC3DownMixStatus.py" % (componentspath))
			os.system("cp /tmp/AlwaysTrue.py %sConverter/AlwaysTrue.py" % (componentspath))
			os.system("cp /tmp/Bitrate2.py %sConverter/Bitrate2.py" % (componentspath))
			os.system("cp /tmp/CaidBar.py %sConverter/CaidBar.py" % (componentspath))
			os.system("cp /tmp/CaidInfo2.py %sConverter/CaidInfo2.py" % (componentspath))
			os.system("cp /tmp/CamdInfo3.py %sConverter/CamdInfo3.py" % (componentspath))
			os.system("cp /tmp/ConverterRotator.py %sConverter/ConverterRotator.py" % (componentspath))
			os.system("cp /tmp/CpuUsage.py %sConverter/CpuUsage.py" % (componentspath))
			os.system("cp /tmp/DiskInfo.py %sConverter/DiskInfo.py" % (componentspath))
			os.system("cp /tmp/EcmInfoLine.py %sConverter/EcmInfoLine.py" % (componentspath))
			os.system("cp /tmp/EmuName.py %sConverter/EmuName.py" % (componentspath))
			os.system("cp /tmp/EventName2.py %sConverter/EventName2.py" % (componentspath))
			os.system("cp /tmp/ExtraNumText.py %sConverter/ExtraNumText.py" % (componentspath))
			os.system("cp /tmp/FanTempInfo.py %sConverter/FanTempInfo.py" % (componentspath))
			os.system("cp /tmp/FlashingDotClock.py %sConverter/FlashingDotClock.py" % (componentspath))
			os.system("cp /tmp/FrontendInfo2.py %sConverter/FrontendInfo2.py" % (componentspath))
			os.system("cp /tmp/IsNet.py %sConverter/IsNet.py" % (componentspath))
			os.system("cp /tmp/MemoryInfo.py %sConverter/MemoryInfo.py" % (componentspath))
			os.system("cp /tmp/ModuleControl.py %sConverter/ModuleControl.py" % (componentspath))
			os.system("cp /tmp/MovieInfo2.py %sConverter/MovieInfo2.py" % (componentspath))
			os.system("cp /tmp/ProgressDiskSpaceInfo.py %sConverter/ProgressDiskSpaceInfo.py" % (componentspath))
			os.system("cp /tmp/RefString.py %sConverter/RefString.py" % (componentspath))
			os.system("cp /tmp/RouteInfo.py %sConverter/RouteInfo.py" % (componentspath))
			os.system("cp /tmp/ServiceInfo2.py %sConverter/ServiceInfo2.py" % (componentspath))
			os.system("cp /tmp/ServiceInfoEX.py %sConverter/ServiceInfoEX.py" % (componentspath))
			os.system("cp /tmp/ServiceName2.py %sConverter/ServiceName2.py" % (componentspath))
			os.system("cp /tmp/ServiceName2.ref %sConverter/ServiceName2.ref" % (componentspath))
			os.system("cp /tmp/ServiceOrbitalPosition2.py %sConverter/ServiceOrbitalPosition2.py" % (componentspath))
			os.system("cp /tmp/TunerBar.py %sConverter/TunerBar.py" % (componentspath))
			os.system("cp /tmp/WiFiInfo.py %sConverter/WiFiInfo.py" % (componentspath))
	# install renderer
			os.system("cp /tmp/AnimatedWeatherPixmap.py %sRenderer/AnimatedWeatherPixmap.py" % (componentspath))
			os.system("cp /tmp/AnimatedMoonPixmap.py %sRenderer/AnimatedMoonPixmap.py" % (componentspath))
			os.system("cp /tmp/LabelDuoColors.py %sRenderer/LabelDuoColors.py" % (componentspath))
			os.system("cp /tmp/MovieCover.py %sRenderer/MovieCover.py" % (componentspath))
			os.system("cp /tmp/MovieRating.py %sRenderer/MovieRating.py" % (componentspath))
			os.system("cp /tmp/PiconUni.py %sRenderer/PiconUni.py" % (componentspath))
			os.system("cp /tmp/RendVolumeText.py %sRenderer/RendVolumeText.py" % (componentspath))
			os.system("cp /tmp/RendVolumeTextP.py %sRenderer/RendVolumeTextP.py" % (componentspath))
			os.system("cp /tmp/RunningText.py %sRenderer/RunningText.py" % (componentspath))
			os.system("cp /tmp/Watches.py %sRenderer/Watches.py" % (componentspath))
	# end
			self.session.openWithCallback(self.restart, MessageBox,_("Do you want to restart the GUI now ?"), MessageBox.TYPE_YESNO)
		else:
			self.session.open(MessageBox,(_("Download failed, check your internet connection !!!")), MessageBox.TYPE_INFO, timeout = 10)

	def download_pl(self):
# download plugin
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-plugins/master/python/Plugins/Extensions/DownSkinLIB/plugin.py").text
		f = open("/tmp/plugin.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-plugins/master/python/Plugins/Extensions/DownSkinLIB/locale/ru/LC_MESSAGES/DownSkinLIB.mo").text
		f = open("/tmp/ruDownSkinLIB.mo", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-plugins/master/python/Plugins/Extensions/DownSkinLIB/locale/de/LC_MESSAGES/DownSkinLIB.mo").text
		f = open("/tmp/deDownSkinLIB.mo", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-plugins/master/python/Plugins/Extensions/DownSkinLIB/locale/uk/LC_MESSAGES/DownSkinLIB.mo").text
		f = open("/tmp/ukDownSkinLIB.mo", "w")
		f.write(file)
		f.close()
# end
		self.install_pl()


	def download_com(self):
	# download converter
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/AC3DownMixStatus.py").text
		f = open("/tmp/AC3DownMixStatus.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/AlwaysTrue.py").text
		f = open("/tmp/AlwaysTrue.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/Bitrate2.py").text
		f = open("/tmp/Bitrate2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/CaidBar.py").text
		f = open("/tmp/CaidBar.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/CaidInfo2.py").text
		f = open("/tmp/CaidInfo2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/CamdInfo3.py").text
		f = open("/tmp/CamdInfo3.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ConverterRotator.py").text
		f = open("/tmp/ConverterRotator.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/CpuUsage.py").text
		f = open("/tmp/CpuUsage.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/DiskInfo.py").text
		f = open("/tmp/DiskInfo.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/EcmInfoLine.py").text
		f = open("/tmp/EcmInfoLine.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/EmuName.py").text
		f = open("/tmp/EmuName.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/EventName2.py").text
		f = open("/tmp/EventName2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ExtraNumText.py").text
		f = open("/tmp/ExtraNumText.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/FanTempInfo.py").text
		f = open("/tmp/FanTempInfo.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/FlashingDotClock.py").text
		f = open("/tmp/FlashingDotClock.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/FrontendInfo2.py").text
		f = open("/tmp/FrontendInfo2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/IsNet.py").text
		f = open("/tmp/IsNet.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/MemoryInfo.py").text
		f = open("/tmp/MemoryInfo.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ModuleControl.py").text
		f = open("/tmp/ModuleControl.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/MovieInfo2.py").text
		f = open("/tmp/MovieInfo2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ProgressDiskSpaceInfo.py").text
		f = open("/tmp/ProgressDiskSpaceInfo.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/RefString.py").text
		f = open("/tmp/RefString.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/RouteInfo.py").text
		f = open("/tmp/RouteInfo.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ServiceInfo2.py").text
		f = open("/tmp/ServiceInfo2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ServiceInfoEX.py").text
		f = open("/tmp/ServiceInfoEX.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ServiceName2.py").text
		f = open("/tmp/ServiceName2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ServiceName2.ref").text
		f = open("/tmp/ServiceName2.ref", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/ServiceOrbitalPosition2.py").text
		f = open("/tmp/ServiceOrbitalPosition2.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/TunerBar.py").text
		f = open("/tmp/TunerBar.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Converter/WiFiInfo.py").text
		f = open("/tmp/WiFiInfo.py", "w")
		f.write(file)
		f.close()
# download renderer
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/AnimatedWeatherPixmap.py").text
		f = open("/tmp/AnimatedWeatherPixmap.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/AnimatedMoonPixmap.py").text
		f = open("/tmp/AnimatedMoonPixmap.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/LabelDuoColors.py").text
		f = open("/tmp/LabelDuoColors.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/MovieCover.py").text
		f = open("/tmp/MovieCover.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/MovieRating.py").text
		f = open("/tmp/MovieRating.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/PiconUni.py").text
		f = open("/tmp/PiconUni.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/RendVolumeText.py").text
		f = open("/tmp/RendVolumeText.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/RendVolumeTextP.py").text
		f = open("/tmp/RendVolumeTextP.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/RunningText.py").text
		f = open("/tmp/RunningText.py", "w")
		f.write(file)
		f.close()
		file = requests.get("https://raw.githubusercontent.com/Sirius0103/enigma2-components/master/python/Components/Renderer/Watches.py").text
		f = open("/tmp/Watches.py", "w")
		f.write(file)
		f.close()
# end
		self.install_com()

	def exit(self):
		self.close()

	def restart(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

	def about(self):
		self.session.open(MessageBox, _("Download SkinLIB \nDeveloper: Sirius0103 \nHomepage: www.gisclub.tv \nGithub: www.github.com/Sirius0103 \n\nDonate: \nR460680746216 \nZ395874509364 \nE284580190260"), MessageBox.TYPE_INFO)

def main(session, **kwargs):
	session.open(DownSkinLIB)

def Plugins(**kwargs):
	return PluginDescriptor(name=_("Download SkinLIB"),
	description=_("Download components skins library"),
	where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
	icon="plugin.png",
	fnc=main)
