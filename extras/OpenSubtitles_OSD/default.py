import sys
import os
import xbmcgui
import xbmc
import string
#import xbmcplugin
from xml.dom import minidom
from xml.dom.minidom import Document
import platform
__scriptname__ = "OpenSubtitles_OSD"
__author__ = "Amet"
__url__ = ""
__svn_url__ = ""
__credits__ = ""
__version__ = "1.28_plex"
EXIT_SCRIPT = ( 6, 10, 247, 275, 61467, 216, 257, 61448, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)


import language
__language__ = language.Language().localized
_ = sys.modules[ "__main__" ].__language__

import unzip
import globals
import gui
from utilities import *



langugestrings = [ "Albanian","Arabic","Belarusian","Bosnian","Bulgarian","Catalan","Chinese","Croatian","Czech","Danish","Dutch","English","Estonian","Finnish","French","German","Greek","Hebrew","Hindi","Hungarian","Icelandic","Indonesian","Italian","Japanese","Korean","Latvian","Lithuanian","Macedonian","Norwegian","Polish","Portuguese","PortugueseBrazil","Romanian","Russian","SerbianLatin","Slovak","Slovenian","Spanish","Swedish","Thai","Turkish","Ukrainian","Vietnamese"]




#############-----------------Start Def -------------------------###############


def setings_menu (langugestrings):
	
	dialog = xbmcgui.Dialog()
	langugestrings.append('last item')
	selected1 = dialog.select((_( 503 ) + " 1"), langugestrings)
	selected2 = dialog.select((_( 503 ) + " 2"), langugestrings)
	if not (langugestrings[selected1] == "last item") and not (langugestrings[selected2] == "last item") :
		##dialog.ok("Language Selection", "You Have Selected" + " " + langugestrings[selected1] + " and " + langugestrings[selected2])
		lang1 = langugestrings[selected1]
		lang2 = langugestrings[selected2]
	else:
		dialog.ok( _( 502 ) , _( 500 ))
		lang1 = "English"
		lang2 = "English"
	
	selected = dialog.yesno("OpenSubtitles_OSD",_( 501 ))

	if selected == 1:
		path = dialog.browse( 0, "OpenSubtitles_OSD", "files")
		if path == "":
			path = "Default_folder"
	else:
		path = "Default_folder"
	
	dialog = xbmcgui.Dialog()
	possibleChoices = ["Sublight", "OpenSubtitles"]  
	choice = dialog.select( _( 505 ) , possibleChoices)
	if choice == 0:
		service = "Sublight"
	if choice == 1:
		service = "OpenSubtitles"
		
	set_lang = "1"
	save_languages (lang1,lang2, set_lang, path,service)
	return lang1,lang2, path ,service



def get_languages ():
	lang1 = ""
	lang2 = ""
	lang =  os.path.join( os.getcwd(), 'resources' , "languages.xml")
	xmldoc = minidom.parse(lang)
	lang_set = int(xmldoc.getElementsByTagName("lang_set")[0].firstChild.data)
	path = xmldoc.getElementsByTagName("folder")[0].firstChild.data
	if lang_set == 1:
		lang1 = xmldoc.getElementsByTagName("language1")[0].firstChild.data
		lang2 = xmldoc.getElementsByTagName("language2")[0].firstChild.data
		
	service = xmldoc.getElementsByTagName("service")[0].firstChild.data
	return lang1,lang2,lang_set,path,service




def save_languages (lang1,lang2,set_lang,path,service):

	doc = Document()

	wml = doc.createElement("language")
	doc.appendChild(wml)

	maincard = doc.createElement("card")
	maincard.setAttribute("id", "main")
	wml.appendChild(maincard)

	paragraph1 = doc.createElement("language1")
	maincard.appendChild(paragraph1)
	ptext = doc.createTextNode(lang1)
	paragraph1.appendChild(ptext)

	paragraph1 = doc.createElement("language2")
	maincard.appendChild(paragraph1)
	ptext = doc.createTextNode(lang2)
	paragraph1.appendChild(ptext)

	paragraph1 = doc.createElement("lang_set")
	maincard.appendChild(paragraph1)
	ptext = doc.createTextNode(set_lang)
	paragraph1.appendChild(ptext)

	paragraph1 = doc.createElement("folder")
	maincard.appendChild(paragraph1)
	ptext = doc.createTextNode(path)
	paragraph1.appendChild(ptext)
	
	paragraph1 = doc.createElement("service")
	maincard.appendChild(paragraph1)
	ptext = doc.createTextNode(service)
	paragraph1.appendChild(ptext)
	
	wdoc = doc.toxml()

	lang =  os.path.join( os.getcwd(), 'resources' , "languages.xml")
	os.remove( lang )
	file = open(lang,"w") 
	file.write(wdoc)
	file.close()



#############-----------------Is script runing from OSD?---Reset to Defaults----------------------------###############

#try: check = sys.argv
#except : check = ""
if str(xbmc.getInfoLabel("System.CurrentWindow")) == "Home" or str(xbmc.getInfoLabel("System.CurrentWindow")) == "Scripts" :
 
#if xbmc.Player().isPlaying() == False :
	try: xbmc.Player().stop()
	except : Check = ""
	dialog = xbmcgui.Dialog()
	selected = dialog.yesno("OpenSubtitles_OSD", _( 506 ))

	if selected == 1:
		setings_menu( langugestrings )



else:

   skin = "MediaStream"


###-------------------Extract Media files -----------------------------------################


   if ( __name__ == "__main__" ):


###-------------------------- Set Search String and Path string -------------################
	temp = False
	search_string = ""
	path_string = ""
	season = xbmc.getInfoLabel("VideoPlayer.Season")
	episode = xbmc.getInfoLabel("VideoPlayer.Episode")
	tvtitle = xbmc.getInfoLabel("VideoPlayer.TVshowtitle")
	title = xbmc.getInfoLabel("VideoPlayer.Title")
	#from utilities import getMovieTitleAndYear
	if tvtitle == "":
		from utilities import getMovieTitleAndYear
		search_string, year = getMovieTitleAndYear( title )
		tmp_list = search_string.split()
		search_string = string.join( tmp_list, '+' )
	else:
		year = 0
		search_string = tvtitle
		if ( int( season ) < 10 ):
			search_string = search_string + " S0" + season
		else:
			search_string = search_string + " S" + season
		if ( int( episode ) < 10 ):
			search_string = search_string + "E0" + episode
		else:
			search_string = search_string + "E" + episode
	search_string = search_string.replace(" ","+")
	search_string = search_string.replace(".","")	

	movieFullPath = xbmc.Player().getPlayingFile()
	if (movieFullPath.find("http://") > -1 ) or (movieFullPath.find("smb://") > -1 ) or (movieFullPath.find("rar://") > -1 ):
		temp = True

#### ------------------------------ Get User Languages,Path and Service ---------------------------#####
	##system = xbmc.getInfoLabel( "System.BuildVersion" )

	
	lang1,lang2,lang_set,path,service = get_languages ()
	
	if lang_set == 0:
		lang1,lang2,path,service = setings_menu( langugestrings )
	
	if not path == "Default_folder":
		
		sub_folder = xbmc.translatePath(path)
	else:
		if temp:
			dialog = xbmcgui.Dialog()
			sub_folder = dialog.browse( 0, "Choose Subtitle folder", "files")
			##temp = True
		else:
			sub_folder = os.path.dirname( movieFullPath )

#### ------------------------------ Get the main window going ---------------------------#####
	#print os.getcwd()
	
	
	xbmc.Player().pause()
	ui = gui.GUI( "script-OpenSubtitles_OSD-main.xml", os.getcwd(), "Default")
	ui.set_service ( service )
	ui.set_filepath( movieFullPath )
	ui.set_searchstring( search_string )
	ui.set_temp( temp )
	ui.set_sub_folder( sub_folder )
	ui.set_lang(lang1,lang2)
	ui.doModal()
	xbmc.Player().pause()
	del ui

