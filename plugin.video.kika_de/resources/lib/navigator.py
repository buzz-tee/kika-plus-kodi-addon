# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import time
from datetime import datetime
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
	kikaninchen_brand = '/api/brands/ebb32e6f-511f-450d-9519-5cbf50d4b546'
	kikaninchen_and_friends_brand = '/api/brands/9ed5cf37-2e09-4074-9935-f51ae06e45b1'
	sesamstrasse_brand = '/api/brands/3e3e70b3-62a2-40cb-856d-a46d3e210e9c'
	lollywood_brand = '/api/brands/a4b0918c-0d21-4160-afb0-2dc789534a8e'

	if Newest: addDir(translation(30601), icon, {'mode': 'listEpisodes', 'url': '/api/videos?offset=0&limit=100&orderBy=appearDate&orderDirection=desc', 'extras': 'nopager'})
	if Mostviewed: addDir(translation(30602), icon, {'mode': 'listEpisodes', 'url': '/api/videos?offset=0&limit=100&orderBy=viewCount&orderDirection=desc', 'extras': 'nopager'})
	if Lastchance: addDir(translation(30603), icon, {'mode': 'listEpisodes', 'url': '/api/videos?offset=0&limit=100&orderBy=expirationDate&orderDirection=asc', 'extras': 'nopager'})
	if kikaninchen: 
		addDir(translation(30604), getIdentImageUrl(kikaninchen_brand), {'mode': 'listEpisodes', 'url': kikaninchen_brand + '/videos'})
		addDir(translation(30605), getIdentImageUrl(kikaninchen_and_friends_brand), {'mode': 'listEpisodes', 'url': kikaninchen_and_friends_brand + '/videos', 'transmit': 'Kikaninchen und Freunde'})
	if sesamstrasse: addDir(translation(30606), getIdentImageUrl(sesamstrasse_brand), {'mode': 'listEpisodes', 'url': sesamstrasse_brand + '/videos', 'transmit': 'Sesamstrasse'})
	if lollywood: addDir(translation(30616), getIdentImageUrl(lollywood_brand), {'mode': 'listEpisodes', 'url': lollywood_brand + '/videos', 'transmit': 'Lollywood'})
	if since03: addDir(translation(30607), icon, {'mode': 'listAlphabet', 'url': '/api/brands?offset=0&limit=100&orderBy=title&orderDirection=asc&userAge=3'})
	if since06: addDir(translation(30608), icon, {'mode': 'listAlphabet', 'url': '/api/brands?offset=0&limit=100&orderBy=title&orderDirection=asc&userAge=6'})
	if since10: addDir(translation(30609), icon, {'mode': 'listAlphabet', 'url': '/api/brands?offset=0&limit=100&orderBy=title&orderDirection=asc&userAge=10'})
	if sinceAll: addDir(translation(30610), icon, {'mode': 'listAlphabet', 'url': '/api/brands?offset=0&limit=100&orderBy=title&orderDirection=asc'})
	if Userspecial:
		addDir(translation(30611), icon, {'mode': 'listEpisodes', 'url': '/api/videos?offset=0&limit=100&videoTypes=dgsContent'})
		addDir(translation(30612), icon, {'mode': 'listEpisodes', 'url': '/api/videos?offset=0&limit=100&videoTypes=adContent'})
	addDir(translation(30613), artpic+'livestream.png', {'mode': 'playLIVE', 'url': BASE_LIVE}, folder=False)
	if enableADJUSTMENT:
		addDir(translation(30614), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30615), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def getIdentImageUrl(brand_url):
	content = getUrl(BASE_API + brand_url)
	return content.get('largeIdentImageUrl', icon)

def listAlphabet(url, EXTRA):
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	debug_MS("(navigator.listAlphabet) ### URL : {0} ### EXTRA : {1} ###".format(url, EXTRA))
	content = { '_links': { 'next': { 'href': url } } }
	while 'next' in content['_links']:
		content = getUrl(BASE_API + content['_links']['next']['href'])
		for item in content['_embedded']['items']:
			addDir(item['title'], item['brandImageUrl'], params={'mode': 'listEpisodes', 'url': item['_links']['videos']['href']},
				plot=item['description'], fanart=item['largeBackgroundImageUrl'])
		if EXTRA == 'nopager':
			break
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDAlphabet+')')

def listEpisodes(url, EXTRA, TRANS):
	debug_MS("(navigator.listEpisodes) ------------------------------------------------ START = listEpisodes -----------------------------------------------")
	debug_MS("(navigator.listEpisodes) ### URL : {0} ### EXTRA : {1} ### SERIE : {2} ###".format(url, EXTRA, TRANS))
	COMBI_EPISODE, COMBI_THIRD, COMBI_FOURTH = ([] for _ in range(3))
	SingleENTRY = set()
	pos1 = 0
	content = { '_links': { 'next': { 'href': url } } }
	while 'next' in content['_links']:
		content = getUrl(BASE_API + content['_links']['next']['href'])
		for item in content['_embedded']['items']:
			debug_MS("(navigator.listEpisodes[1]) no.01 ### ITEM-01 : {0} ###".format(str(item)))
			SERIE_1, VIEWS, startTIMES, endTIMES, STUDIO_1 = (None for _ in range(5))
			DESC_1, canPLAY_1 = "", True
			TITLE_1 = cleaning(item['title'])
			if item.get('_embedded', '') and item.get('_embedded', {}).get('brand', '') and item.get('_embedded', []).get('brand', {}).get('title', ''):
				TITLE_1, SERIE_1 = cleaning(item['_embedded']['brand']['title']) + ' - ' + TITLE_1, cleaning(item['_embedded']['brand']['title'])
			if item['videoType'] != 'mainContent' and not Userspecial:
				continue
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
		if EXTRA == 'nopager':
			break

	if COMBI_EPISODE or (COMBI_FOURTH and COMBI_THIRD) or (not COMBI_FOURTH and COMBI_THIRD):
		if COMBI_THIRD:
			COMBI_EPISODE = [a + b for a in COMBI_THIRD for b in COMBI_FOURTH if a[1] == b[1]] # Zusammenführung von Liste1 und Liste2 - wenn der WLINK überein stimmt !!!
			COMBI_EPISODE += [c for c in COMBI_THIRD if all(d[1] != c[1] for d in COMBI_FOURTH)] # Der übriggebliebene Rest von Liste1 - wenn der WLINK nicht in der Liste2 vorkommt !!!
			#log("++++++++++++++++++++++++")
			#log("(navigator.listEpisodes[5]) no.05 XXXXX RESULT-05 : {0} XXXXX".format(str(COMBI_EPISODE)))
			#log("++++++++++++++++++++++++")
		for da in COMBI_EPISODE: # 0-9 = Liste1 || 10-20 = Liste2
			debug_MS("---------------------------------------------")
			debug_MS("(navigator.listEpisodes[6]) no.06 ### Anzahl = {0} || Eintrag : {1} ###".format(str(len(da)), str(da)))
			playMARKER = ""
			PLAYLINK, studio, name, seriesname, season, episode, photo, plot, tagline, duration, CANPLAY = da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11]
			TYPE = 'videoAPI'
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

def addDir(name, image, params={}, plot=None, seriesname=None, folder=True, fanart=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Tvshowtitle': seriesname, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': fanart if fanart else defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': fanart if fanart else image})
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
