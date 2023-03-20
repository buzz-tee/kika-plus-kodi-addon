# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import time
from datetime import datetime, timedelta
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode  # Python 2.X
	from urllib2 import urlopen  # Python 2.X
else: 
	from urllib.parse import urlencode  # Python 3.X
	from urllib.request import urlopen  # Python 3.X
	from functools import reduce  # Python 3.X

from .common import *


def mainMenu():
	if Newest: addDir(translation(30601), icon, {'mode': 'listEpisodes', 'url': BASE_API+'/api/videos?offset=0&limit=100&orderBy=appearDate&orderDirection=desc', 'extras': 'baseDROID'})
	if Mostviewed: addDir(translation(30602), icon, {'mode': 'listEpisodes', 'url': BASE_API+'/api/videos?offset=0&limit=100&orderBy=viewCount&orderDirection=desc', 'extras': 'baseDROID'})
	if Lastchance: addDir(translation(30603), icon, {'mode': 'listEpisodes', 'url': BASE_API+'/api/videos?offset=0&limit=100&orderBy=expirationDate&orderDirection=asc', 'extras': 'baseDROID'})
	if kikaninchen: 
		addDir(translation(30604), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/kikaninchen/sendungen/videos-kikaninchen-100.html', 'extras': 'excluded'})
		addDir(translation(30605), icon, {'mode': 'listEpisodes', 'url': BASE_URL+'/kikaninchen-und-freunde/videos-kikaninchen-und-freunde-102.html', 'transmit': 'Kikaninchen und Freunde'})
	if sesamstrasse: addDir(translation(30606), icon, {'mode': 'listEpisodes', 'url': BASE_URL+'/sesamstrasse/sendungen/videos-sesamstrasse-100.html', 'transmit': 'Sesamstrasse'})
	if since03: addDir(translation(30607), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/videos-ab-drei-buendel100.html'})
	if since06: addDir(translation(30608), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/videosabsechs-buendel100.html'})
	if since10: addDir(translation(30609), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/videosabzehn-buendel102.html'})
	if sinceAll: addDir(translation(30610), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/uebersicht-alle-videos-100.html'})
	if Userspecial:
		addDir(translation(30611), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/videos-dgs-100.html', 'extras': 'excluded'})
		addDir(translation(30612), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/videos-ad-100.html', 'extras': 'excluded'})
	addDir(translation(30613), artpic+'livestream.png', {'mode': 'playLIVE', 'url': BASE_LIVE}, folder=False)
	if enableADJUSTMENT:
		addDir(translation(30614), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30615), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet(url, EXTRA):
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	debug_MS("(navigator.listAlphabet) ### URL : {0} ### EXTRA : {1} ###".format(url, EXTRA))
	COMBI_ALPHA, COMBI_LINKS = ([] for _ in range(2))
	counter = 0
	content = getUrl(url, 'LOAD', url)
	result = re.findall(r'class="bundleNaviWrapper"(.+?)class="modCon"', content, re.S)[0]
	match = re.findall(r'<a href="([^"]+)" class="pageItem".*?>(.+?)</a>', result, re.S)
	for endURL, title in match:
		counter += 1
		endURL = endURL if endURL.startswith('http') else BASE_URL+endURL
		title = cleaning(title).replace('...', '#')
		debug_MS("(navigator.listAlphabet[1]) XXX TITLE = {0} || endURL = {1} XXX".format(str(title), endURL))
		action = 'listEpisodes' if EXTRA == 'excluded' else 'listShows'
		COMBI_ALPHA.append([int(counter), endURL, title, action])
		COMBI_LINKS.append({'uno': int(counter), 'due': endURL, 'tre': endURL})
	if COMBI_LINKS and EXTRA != 'excluded':
		provide = json.dumps(COMBI_LINKS)
		addDir(translation(30621), alppic+'ABC.png', {'mode':'listShows', 'url': provide, 'extras': 'SHOWS_LIST'})
	if COMBI_ALPHA:
		for num, endURL, title, action in sorted(COMBI_ALPHA, key=lambda k: int(k[0]), reverse=False):
			newTRANS = title if len(title) > 4 else 'Kikaninchen'
			newIMG = alppic+py2_uni(title).upper()+'.png' if xbmcvfs.exists(alppic+py2_uni(title).upper()+'.png') else icon
			addDir(title, newIMG, {'mode': action, 'url': endURL, 'extras': 'excluded', 'transmit': newTRANS})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDAlphabet+')')

def listShows(url, EXTRA):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(navigator.listShows) ------------------------------------------------ START = listShows -----------------------------------------------")
	debug_MS("(navigator.listShows) ### URL : {0} ### EXTRA : {1} ###".format(url, EXTRA))
	Isolated = set()
	if EXTRA == 'SHOWS_LIST':
		COMBI_SHOWS = [(elem['uno'], elem['due'], elem['tre']) for elem in json.loads(url)]
		COMBI_SECOND = getMultiData(COMBI_SHOWS)
		results = [s[3] for s in COMBI_SECOND[:]]
	else:
		results = [getUrl(url, 'LOAD', url)]
	for chtml in results:
		part = chtml.split('class="teaser teaserStandard  teaserMultigroup')
		for i in range(1, len(part), 1):
			entry = part[i]
			image = re.compile(r"data-ctrl-image=.*?'urlScheme':'(.+?)'}", re.S).findall(entry)
			photo = image[0].split('-resimage_v-')[0]+'-resimage_v-tlarge169_w-1280.jpg' if image else ""
			match = re.compile(r'<h4 class="headline">.*?href="([^"]+)" title=.*?>([^<]+)</a>', re.S).findall(entry)
			endURL = match[0][0] if match[0][0].startswith('http') else BASE_URL+match[0][0]
			title = cleaning(match[0][1])
			if 'kikaninchen' in title.lower(): continue
			if endURL in Isolated:
				continue
			Isolated.add(endURL)
			debug_MS("(navigator.listShows[1]) no.01 ### TITLE = {0} || endURL = {1} || PHOTO = {2} ###".format(str(title), endURL, photo))
			addDir(title, photo, {'mode': 'listEpisodes', 'url': endURL, 'transmit': title}, seriesname=title)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDShows+')')

def listEpisodes(url, EXTRA, TRANS):
	debug_MS("(navigator.listEpisodes) ------------------------------------------------ START = listEpisodes -----------------------------------------------")
	debug_MS("(navigator.listEpisodes) ### URL : {0} ### EXTRA : {1} ### SERIE : {2} ###".format(url, EXTRA, TRANS))
	COMBI_EPISODE, COMBI_PAGES, COMBI_SECOND, COMBI_THIRD, COMBI_LINKS, COMBI_DETAILS, COMBI_FOURTH = ([] for _ in range(7))
	Isolated = set()
	SingleENTRY = set()
	if EXTRA == 'baseDROID':
		pos1 = 0
		DATA = getUrl(url)
		for item in DATA['_embedded']['items']:
			debug_MS("(navigator.listEpisodes[1]) no.01 ### ITEM-01 : {0} ###".format(str(item)))
			SERIE_1, VIEWS, startTIMES, endTIMES, STUDIO_1 = (None for _ in range(5))
			DESC_1, canPLAY_1 = "", True
			TITLE_1 = cleaning(item['title'])
			if item.get('_embedded', '') and item.get('_embedded', {}).get('brand', '') and item.get('_embedded', []).get('brand', {}).get('title', ''):
				TITLE_1, SERIE_1 = cleaning(item['_embedded']['brand']['title']) + ' - ' + TITLE_1, cleaning(item['_embedded']['brand']['title'])
			JSURL_1 = '{0}/api/videos/{1}/player-assets'.format(BASE_API, str(item['id']))
			THUMB_1 = (item.get('largeTeaserImageUrl', '') or icon)
			VIEWS = (item.get('viewCount', None) or None)
			SEAS_1 = (item.get('seasonNumber', 0) or 0)
			EPIS_1 = (item.get('episodeNumber', 0) or 0)
			TAGLINE_2 = translation(30622).format(str(SEAS_1).zfill(2), str(EPIS_1).zfill(2)) if SEAS_1 != 0 and EPIS_1 != 0 else translation(30623).format(str(EPIS_1).zfill(2)) if SEAS_1 == 0 and EPIS_1 != 0 else None
			if SERIE_1 and VIEWS: DESC_1 += translation(30624).format(str(SERIE_1), str(VIEWS))
			elif SERIE_1 and VIEWS is None: DESC_1 += translation(30625).format(str(SERIE_1))
			if str(item.get('appearDate'))[:4].isdigit(): # 2020-05-08T07:45:00+02:00
				try:
					startDates = datetime(*(time.strptime(item['appearDate'][:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2022-03-28T19:50:00+02:00
					startTIMES = startDates.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
				except: pass
			if str(item.get('expirationDate'))[:4].isdigit(): # 2020-05-08T07:45:00+02:00
				try:
					endDates = datetime(*(time.strptime(item['expirationDate'][:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2023-03-28T19:50:00+02:00
					endTIMES = endDates.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
				except: pass
			if startTIMES and endTIMES: DESC_1 += translation(30626).format(str(startTIMES), str(endTIMES))
			elif startTIMES and endTIMES is None: DESC_1 += translation(30627).format(str(startTIMES))
			if item.get('description', ''): DESC_1 += '[CR]'+cleaning(item['description'])
			if item.get('broadcaster', ''):
				DESC_1 += translation(30628).format(cleaning(item['broadcaster'])) if item.get('description', '') else translation(30629).format(cleaning(item['broadcaster']))
				STUDIO_1 = cleaning(item['broadcaster'])
			DURATION_1 = (item.get('duration', 0) or 0)
			pos1 += 1
			COMBI_EPISODE.append([int(pos1), JSURL_1, STUDIO_1, TITLE_1, SERIE_1, SEAS_1, EPIS_1, THUMB_1, DESC_1, TAGLINE_2, DURATION_1, canPLAY_1])
	else:
		counter = 0
		html = getUrl(url, 'LOAD', url)
		if '<div class="bundleNaviItem' in html and EXTRA != 'excluded':
			NaviItem = re.findall(r'<div class="bundleNaviItem.*?href="([^"]+)" class="pageItem" title=.*?>([^<]+)</a>', html, re.S)
		else:
			NaviItem = [(url, 'only_page_1')]
		for link, name in NaviItem:
			if link in Isolated:
				continue
			Isolated.add(link)
			counter += 1
			WLINK_1 = link if link.startswith('http') else BASE_URL+link
			debug_MS("(navigator.listEpisodes[2]) SERIES-PAGES XXX POS = {0} || URL = {1} XXX".format(str(counter), WLINK_1))
			COMBI_PAGES.append([int(counter), WLINK_1, WLINK_1])
		if COMBI_PAGES:
			COMBI_SECOND = getMultiData(COMBI_PAGES)
			if COMBI_SECOND:
				#log("++++++++++++++++++++++++")
				#log("(navigator.listEpisodes[3]) no.03 XXXXX COMBI_SECOND-03 : {0} XXXXX".format(str(COMBI_SECOND)))
				#log("++++++++++++++++++++++++")
				pos2, pos3 = (0 for _ in range(2))
				for num, WLINK_2, DDURL_2, item in sorted(COMBI_SECOND, key=lambda k: int(k[0]), reverse=False):
					if item is not None:
						content = re.findall(r'<!--Header Area for the Multigroup -->(.+?)<!--The bottom navigation -->', item, re.S)[0]
						part = content.split('class="teaser teaserStandard')
						for i in range(1, len(part), 1):
							entry = part[i]
							playSYMBOL, XMLURL_1, newSERIE, TEXT = (None for _ in range(4))
							EPIS_1 = 0
							debug_MS("(navigator.listEpisodes[3]) no.03 ### ENTRY-03 : {0} ###".format(str(entry)))
							image = re.compile(r"data-ctrl-image=.*?'urlScheme':'(.+?)'}", re.S).findall(entry)
							THUMB_1 = image[0].split('-resimage_v-')[0]+'-resimage_v-tlarge169_w-1280.jpg' if image else ""
							THUMB_1 = BASE_URL+THUMB_1 if THUMB_1 != "" and THUMB_1[:4] != "http" else THUMB_1
							playSYMBOL = re.compile(r'<span class="icon-font">([^<]+)</', re.S).findall(entry)
							canPLAY_1 = True if playSYMBOL and playSYMBOL[0] == '&#xf01d;' else False
							endURL = re.compile(r'<h4 class="headline">.*?href="([^"]+)"', re.S).findall(entry)[0].replace('sendereihe', 'buendelgruppe')
							WLINK_3 = endURL if endURL.startswith('http') else BASE_URL+endURL
							data = re.compile(r'dataURL:\'(https?://.*?.xml)', re.S).findall(entry)
							XMLURL_1 = re.sub(r'-avCustom_parent.*?-true.xml', '-avCustom.xml', data[0]) if data else None # evtl. falschen Link bereinigen
							# falsch: video43402-avCustom_parent-1c9f0499-dd61-4a94-81ad-54d3f0542138_useMgVideos-true.xml // richtig: video43402-avCustom.xml
							newSERIE = re.compile('<meta property="og:title" content="(.+?)"/>', re.S).findall(content)
							DESC_1 = TRANS if TRANS != 'unknown' else translation(30630).format(cleaning(newSERIE[0])) if newSERIE else ""
							SERIE_1 = TRANS if TRANS != 'unknown' else cleaning(newSERIE[0]) if newSERIE else ""
							TITLE_1 = cleaning(re.compile(r'(?:class="linkAll js-broadcast-link"|class="linkAll") title="([^"]+)"', re.S).findall(entry)[0])
							TEXT = re.compile(r'<img title=.*?alt="([^"]+?)"', re.S).findall(entry)
							if TEXT: DESC_1 += '[CR][CR]'+cleaning(TEXT[0])
							pos2 += 1
							if TITLE_1[:1].isdigit() or 'Folge ' in TITLE_1:
								try: EPIS_1 = re.findall('([0-9]+)', TITLE_1, re.S)[0].strip()
								except: pass
							else: pos3 += 1
							COMBI_THIRD.append([int(pos2), WLINK_3, XMLURL_1, TITLE_1, SERIE_1, EPIS_1, THUMB_1, DESC_1, canPLAY_1, pos3])
							if XMLURL_1:
								COMBI_LINKS.append([int(pos2), WLINK_3, XMLURL_1])
		if COMBI_THIRD:
			COMBI_DETAILS = getMultiData(COMBI_LINKS)
			if COMBI_DETAILS:
				#log("++++++++++++++++++++++++")
				#log("(navigator.listEpisodes[4]) no.04 XXXXX COMBI_DETAILS-04 : {0} XXXXX".format(str(COMBI_DETAILS)))
				#log("++++++++++++++++++++++++")
				pos4, pos5 = (0 for _ in range(2))
				for num, WLINK_4, XMLURL_2, elem in COMBI_DETAILS:
					if elem is not None:
						TOPLINE, PROGRAM, PLOT, TEASER, RIGHTS, startTIMES, endTIMES, STUDIO_2 = (None for _ in range(8))
						EPIS_2 = 0
						debug_MS("(navigator.listEpisodes[4]) no.04 ### ELEM-04 : {0} ###".format(str(elem)))
						TOPLINE = re.compile(r'<topline>([^<]+)</topline>', re.S).findall(elem)
						PROGRAM = re.compile(r'<program>([^<]+)</program>', re.S).findall(elem)
						SERIE_2 = cleaning(TOPLINE[0]) if TOPLINE else cleaning(PROGRAM[0]) if PROGRAM else ""
						TITLE_2 = cleaning(re.compile(r'<title>([^<]+)</title>', re.S).findall(elem)[0])
						pos4 += 1
						if TITLE_2[:1].isdigit() or 'Folge ' in TITLE_2:
							try: EPIS_2 = re.findall('([0-9]+)', TITLE_2, re.S)[0].strip()
							except: pass
						else: pos5 += 1
						TAGLINE_2 = translation(30623).format(str(EPIS_2).zfill(2)) if EPIS_2 != 0 else None
						PLOT = re.compile(r'<broadcastDescription>([^<]+)</broadcastDescription>', re.S).findall(elem)
						TEASER = re.compile(r'<teaserText>([^<]+)</teaserText>', re.S).findall(elem)
						RIGHTS = re.compile(r'<rights>([^<]+)</rights>', re.S).findall(elem)
						DESC_2 = translation(30630).format(SERIE_2)+'[CR]' if SERIE_2 != "" else ""
						START = re.compile(r'<webTime>([^<]+)</webTime>', re.S).findall(elem)
						if START and str(START[0])[:10].replace('.', '').replace('-', '').replace('/', '').isdigit():
							try:
								startDates = datetime(*(time.strptime(START[0][:16], '%d{0}%m{0}%Y %H{1}%M'.format('.', ':'))[0:6])) # 26.03.2022 10:05
								startTIMES = startDates.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
							except: pass
						ENDE = re.compile(r'<effectiveEndDate>([^<]+)</effectiveEndDate>', re.S).findall(elem)
						if ENDE and str(ENDE[0])[:10].replace('.', '').replace('-', '').replace('/', '').isdigit():
							try:
								endDates = datetime(*(time.strptime(ENDE[0][:16], '%d{0}%m{0}%Y %H{1}%M'.format('.', ':'))[0:6])) # 26.03.2024 10:05
								endTIMES = endDates.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
							except: pass
						if startTIMES and endTIMES: DESC_2 += translation(30626).format(str(startTIMES), str(endTIMES))
						elif startTIMES and endTIMES is None: DESC_2 += translation(30627).format(str(startTIMES))
						if PLOT: DESC_2 += '[CR]'+cleaning(PLOT[0])
						elif not PLOT and TEASER: DESC_2 += '[CR]'+cleaning(TEASER[0])
						if RIGHTS:
							DESC_2 += translation(30628).format(cleaning(RIGHTS[0])) if PLOT or TEASER else translation(30629).format(cleaning(RIGHTS[0]))
							STUDIO_2 = cleaning(RIGHTS[0])
						DUR_2 = re.compile(r'<length>([^<]+)</length>', re.S).findall(elem)
						DURATION_2 = DUR_2[0] if DUR_2 else 0
						THUMB_2 = re.findall(r'<teaserimage>.*?<url>([^<]+)</url>.*?</teaserimage>', elem, re.S)[0].split('-resimage_v-')[0]+'-resimage_v-tlarge169_w-1280.jpg'
						COMBI_FOURTH.append([int(pos4), WLINK_4, STUDIO_2, TITLE_2, SERIE_2, EPIS_2, THUMB_2, DESC_2, TAGLINE_2, DURATION_2, pos5])
	if COMBI_EPISODE or (COMBI_FOURTH and COMBI_THIRD) or (not COMBI_FOURTH and COMBI_THIRD):
		if COMBI_THIRD:
			COMBI_EPISODE = [a + b for a in COMBI_THIRD for b in COMBI_FOURTH if a[1] == b[1]] # Zusammenführung von Liste1 und Liste2 - wenn der WLINK überein stimmt !!!
			COMBI_EPISODE += [c for c in COMBI_THIRD if all(d[1] != c[1] for d in COMBI_FOURTH)] # Der übriggebliebene Rest von Liste1 - wenn der WLINK nicht in der Liste2 vorkommt !!!
			#log("++++++++++++++++++++++++")
			#log("(navigator.listEpisodes[5]) no.05 XXXXX RESULT-05 : {0} XXXXX".format(str(COMBI_EPISODE)))
			#log("++++++++++++++++++++++++")
		if EXTRA != 'baseDROID':
			for sign in COMBI_EPISODE:
				COURSE = True if SORTING == '0' else False
				if int(sign[9]) <= 5:
					COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda k: int(k[5]), reverse=COURSE)
				else:
					COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda k: int(k[0]), reverse=False)
		for da in COMBI_EPISODE: # 0-9 = Liste1 || 10-20 = Liste2
			debug_MS("---------------------------------------------")
			debug_MS("(navigator.listEpisodes[6]) no.06 ### Anzahl = {0} || Eintrag : {1} ###".format(str(len(da)), str(da)))
			playMARKER = ""
			if EXTRA == 'baseDROID':
				PLAYLINK, studio, name, seriesname, season, episode, photo, plot, tagline, duration, CANPLAY = da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11]
				TYPE = 'videoAPI'
			else:
				if len(da) > 10: ### Liste2 beginnt mit Nummer:10 ###
					### num1, link1, PLAYLINK, name, seriesname, episode, photo, plot, CANPLAY, num3 = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9]
					### num4, link2, studio, name, seriesname, episode, photo, plot, tagline, duration, num5 = da[10], da[11], da[12], da[13], da[14], da[15], da[16], da[17], da[18], da[19], da[20]
					link1, PLAYLINK, CANPLAY, studio, name, seriesname, episode, photo, plot, tagline, duration = da[1], da[2], da[8], da[12], da[13], da[14], da[15], da[16], da[17], da[18], da[19]
					season, TYPE = 0, 'videoXML'
				else:
					link1, PLAYLINK, name, seriesname, episode, photo, plot, CANPLAY = da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8]
					studio, season, tagline, duration, TYPE = 'KiKA', 0, None, 0, 'videoXML'
			if PLAYLINK is not None and PLAYLINK in SingleENTRY:
				continue
			SingleENTRY.add(PLAYLINK)
			if CANPLAY is False and not showMASK:
				continue
			elif showMASK: 
				playMARKER = '[COLOR lime]> [/COLOR]' if CANPLAY is True else '[COLOR orangered]¤ [/COLOR]'
			debug_MS("(navigator.listEpisodes[6]) no.06 ##### TITLE : {0} || SERIE : {1} || THUMB : {2} #####".format(str(name), str(seriesname), photo))
			debug_MS("(navigator.listEpisodes[6]) no.06 ##### VIDLINK : {0} || EPISODE : {1} || STUDIO : {2} #####".format(str(PLAYLINK), str(episode), str(studio)))
			addLink(playMARKER+name, photo, {'mode': 'playVideo', 'url': PLAYLINK, 'extras': TYPE}, plot, tagline, duration, seriesname, season, episode, studio)
	else:
		dialog.notification(translation(30525), translation(30526).format(TRANS), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')

def playVideo(videoURL, EXTRA):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	debug_MS("(navigator.playVideo) ### videoURL : {0} ### EXTRA : {1} ###".format(str(videoURL), EXTRA))
	Xml_QUALITIES = ['1920x1080', '1280x720', '1024x576', '960x540', '852x480', '720x576', '640x360', '512x288', '480x272', '480x270', '320x180', '320x176']
	All_QUALITIES = [4, 3, 2, 1, 0, 'hd', 'veryhigh', 'high', 'med', 'low', '1920', '1280', '1024', '960', '852', '720', '640', '512', '480', '320']
	M3U8_Url, finalURL, QUALITY, STREAM = (False for _ in range(4))
	MEDIAS, BestMEDIAS = ([] for _ in range(2))
	if EXTRA == 'DEFAULT':
		content = getUrl(videoURL, 'LOAD')
		data = re.compile(r'class="av-playerContainer".*?dataURL:\'(https?://.*?.xml)', re.S).findall(content)
		videoURL = data[0] if data else None
	if videoURL not in [None, 'None']:
		if EXTRA == 'videoAPI':
			DATA = getUrl(videoURL)
			for entry in DATA['assets']:
				if entry.get('quality').lower() == 'auto' and 'm3u8' in entry.get('url'):
					M3U8_Url = entry.get('url')
			for item in DATA['hbbtvAssets']:
				MP4 = item['url']
				TYPE = (item.get('delivery', 'Unknown') or 'Unknown')
				try: QUAL = item.get('quality').split('|')[-1].strip()
				except: QUAL = item.get('quality')
				MEDIAS.append({'url': MP4, 'delivery': TYPE, 'quality': QUAL, 'document': 'API_URL'})
		else:
			xmlUrl =getUrl(videoURL, 'LOAD')
			HLS_Redirect = re.findall(r'<asset>.*?<csmilHlsStreamingRedirectorUrl>([^<]+)</csmilHlsStreaming.*?</asset>', xmlUrl, re.S)
			HTTP_Redirect = re.findall(r'<asset>.*?<adaptiveHttpStreamingRedirectorUrl>([^<]+)</adaptiveHttpStreaming.*?</asset>', xmlUrl, re.S)
			M3U8_Url = HLS_Redirect[-1] if HLS_Redirect else HTTP_Redirect[-1] if HTTP_Redirect else None
			part = xmlUrl.split('<asset>')
			for i in range(1, len(part), 1):
				entry = part[i]
				WIDTH = re.compile(r'<frameWidth>([^<]+)</frameWidth>', re.S).findall(entry)
				QUAL = WIDTH[0] if WIDTH else None
				if QUAL is None:
					QUAL = re.compile(r'<profileName>([^<]+)</profileName>', re.S).findall(entry)[0]
					try: QUAL = QUAL.split('|')[-1].replace('quality =', '').strip().split('x')[0]
					except: pass
				MP4 = re.compile(r'<progressiveDownloadUrl>([^<]+)</progressiveDownloadUrl>', re.S).findall(entry)[0]
				MEDIAS.append({'url': MP4, 'delivery': 'progressive', 'quality': QUAL, 'document': 'XML_URL'})
	if MEDIAS:
		debug_MS("(navigator.playVideo[1]) ORIGINAL_MP4 ##### unsorted_LIST : {0} ###".format(str(MEDIAS)))
		order_dict = {qual: index for index, qual in enumerate(All_QUALITIES)}
		BestMEDIAS = sorted(MEDIAS, key=lambda x: order_dict.get(x['quality'], float('inf')))
		debug_MS("(navigator.playVideo[1]) SORTED_LIST | MP4 ### sorted_LIST : {0} ###".format(str(BestMEDIAS)))
	if (prefSTREAM == '0' or enableINPUTSTREAM) and M3U8_Url:
		debug_MS("(navigator.playVideo[2]) ~~~~~ TRY NUMBER ONE TO GET THE FINALURL (m3u8) ~~~~~")
		STREAM = 'HLS' if enableINPUTSTREAM else 'M3U8'
		MIME, QUALITY, finalURL = 'application/vnd.apple.mpegurl', 'AUTO', M3U8_Url
	if not finalURL and BestMEDIAS:
		debug_MS("(navigator.playVideo[3]) ~~~~~ TRY NUMBER TWO TO GET THE FINALURL (mp4) ~~~~~")
		MP4_Url = BestMEDIAS[0]['url'] if BestMEDIAS[0]['url'].startswith('http') else 'https:'+BestMEDIAS[0]['url']
		STREAM, MIME, QUALITY, finalURL = 'MP4', 'video/mp4', str(BestMEDIAS[0]['quality'])+'p', VideoBEST(MP4_Url) # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	if finalURL and STREAM:
		LSM = xbmcgui.ListItem(path=finalURL)
		LSM.setMimeType(MIME)
		if ADDON_operate('inputstream.adaptive') and STREAM in ['HLS', 'MPD']:
			LSM.setProperty(INPUT_APP, 'inputstream.adaptive')
			LSM.setProperty('inputstream.adaptive.manifest_type', STREAM.lower())
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		log("(navigator.playVideo) [{0}] {1}_stream : {2} ".format(QUALITY, STREAM, finalURL))
	else:
		failing("(navigator.playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Stream-Eintrag auf der Webseite von *kika.de* gefunden !!! ##########".format(str(videoURL)))
		return dialog.notification(translation(30521).format('STREAM'), translation(30527), icon, 8000)

def playLIVE(url):
	debug_MS("(navigator.playLIVE) ------------------------------------------------ START = playLIVE -----------------------------------------------")
	LTM = xbmcgui.ListItem(path=url, label=translation(30613))
	LTM.setMimeType('application/vnd.apple.mpegurl')
	if ADDON_operate('inputstream.adaptive'):
		LTM.setProperty(INPUT_APP, 'inputstream.adaptive')
		LTM.setProperty('inputstream.adaptive.manifest_type', 'hls')
		LTM.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
	xbmc.Player().play(item=url, listitem=LTM)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def VideoBEST(best_url):
	# *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	standards = [best_url, '', '']
	first_repls = (('808k_p11v15', '2360k_p35v15'), ('1628k_p13v15', '2360k_p35v15'), ('1456k_p13v11', '2328k_p35v11'), ('1456k_p13v12', '2328k_p35v12'), ('1496k_p13v13', '2328k_p35v13'),
								('1496k_p13v14', '2328k_p35v14'), ('2256k_p14v11', '2328k_p35v11'), ('2256k_p14v12', '2328k_p35v12'), ('2296k_p14v13', '2328k_p35v13'), ('2296k_p14v14', '2328k_p35v14'))
	second_repls = (('2328k_p35v12', '3328k_p36v12'), ('2328k_p35v13', '3328k_p36v13'), ('2328k_p35v14', '3328k_p36v14'), ('2360k_p35v15', '3360k_p36v15'))
	standards[1] = reduce(lambda a, kv: a.replace(*kv), first_repls, standards[0])
	standards[2] = reduce(lambda b, kv: b.replace(*kv), second_repls, standards[1])
	if standards[0] not in [standards[1], standards[2]]:
		for xy, element in enumerate(reversed(standards), 1):
			try:
				code = urlopen(element, timeout=6).getcode()
				if str(code) == '200':
					return element
			except: pass
	return best_url

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, seriesname=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Tvshowtitle': seriesname, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, tagline=None, duration=None, seriesname=None, season=None, episode=None, studio=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	cineType = 'episode' if episode and episode != 0 else 'movie'
	if season and season != 0:
		info['Season'] = season
	if episode and episode != 0:
		info['Episode'] = episode
	info['Tvshowtitle'] = seriesname
	info['Title'] = name
	info['Tagline'] = tagline
	info['Plot'] = plot
	info['Duration'] = duration
	info['Genre'] = 'Kinder'
	info['Studio'] = studio
	info['Mpaa'] = None
	info['Mediatype'] = cineType
	liz.setInfo(type='Video', infoLabels=info)
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	liz.addContextMenuItems([(translation(30654), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, 'mode=AddToQueue'))])
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)
