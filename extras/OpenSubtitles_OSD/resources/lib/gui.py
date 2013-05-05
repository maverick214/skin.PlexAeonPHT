import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import threading
import osdb
from osdb import OSDBServer
from utilities import *
import socket
import urllib
import unzip
import sublight_utils as SublightUtils
import xmlrpclib
import struct
import time
import base64
import zipfile
import re
import globals
from xbmcgui import Window
try: current_dlg_id = xbmcgui.getCurrentWindowDialogId()
except: current_dlg_id = 0

current_win_id = xbmcgui.getCurrentWindowId()

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

STATUS_LABEL = 100
LOADING_IMAGE = 110
SUBTITLES_LIST = 120
OSDB_SERVER = "http://api.opensubtitles.org/xml-rpc"




class GUI( xbmcgui.WindowXMLDialog ):
    socket.setdefaulttimeout(10.0) #seconds
	
    def __init__( self, *args, **kwargs ):
          
	  pass

    def set_lang(self,lang1,lang2):
	  
	  self.lang1 = toOpenSubtitlesId( lang1 )
	  LOG( LOG_INFO, "Language 1: [%s]" ,  self.lang1 )
	  self.lang2 = toOpenSubtitlesId( lang2 )
	  LOG( LOG_INFO, "Language 2: [%s]" ,  self.lang2 )
	  


    def set_session(self,session_id):
	  self.session_id = session_id

    def set_service(self,service):
	  self.service = service
	  
	  
	  LOG( LOG_INFO, "Service used: [%s]" ,  self.service )
    def set_temp( self, temp ):
        
        self.set_temp = temp

    def set_sub_folder( self, sub_folder ):
        
        self.sub_folder = sub_folder
        LOG( LOG_INFO, "Subtitle Folder: [%s]" ,  self.sub_folder )

    def set_filepath( self, path ):
        
        self.file_original_path = path
        if not (path.find("special://") > -1 ):
			self.file_path = path[path.find(os.sep):len(path)]
		
        else:
			self.file_path = path
        LOG( LOG_INFO, "File Path: [%s]" ,  self.file_path )

    def set_filehash( self, hash ):
        LOG( LOG_INFO, "File Hash: [%s]" , ( hash ) )
        self.file_hash = hash

    def set_filesize( self, size ):
        LOG( LOG_INFO, "File Size: [%s]" , ( size ) )
        self.file_size = size

    def set_searchstring( self, search ):
        LOG( LOG_INFO, "Search String: [%s]" , ( search ) )
        self.search_string = search

    def set_subtitles( self, subtitles ):
        self.subtitles = subtitles

    def onInit( self ):

	LOG( LOG_INFO, "onInit" )
        self.setup_all()
        if self.service == "OpenSubtitles":   
            self.connThread = threading.Thread( target=self.connect, args=() )
            self.connThread.start()
        else:
	    self.connect()
	    
        
    def setup_all( self ):
        self.setup_variables()
        self.getControl( 300 ).setLabel( _( 601 ) )
        self.getControl( 301 ).setLabel( _( 602 ) )
        
    def setup_variables( self ):
        #try: xbox = xbmc.getInfoLabel( "system.xboxversion")
        xbox = ""
        if xbox == "":
        	self.set_xbox = False
        else:
        	self.set_xbox = True
        LOG( LOG_INFO, "XBOX System: [%s]" ,  xbox )	
        self.controlId = -1
        self.allow_exception = False
        self.osdb_server = OSDBServer()
        self.osdb_server.Create()
        self.manuall = False
    def connect( self ):
		self.getControl( SUBTITLES_LIST ).reset()
		
		self.getControl( 110 ).setVisible( False )
		self.getControl( 111 ).setVisible( False )

		self.getControl( STATUS_LABEL ).setLabel( _( 646 ) )
		if self.service == "OpenSubtitles":
			
			self.getControl( 110 ).setVisible( True )
			
			ok,msg = self.osdb_server.connect( OSDB_SERVER, "", "" )
			if not ok:
				self.getControl( STATUS_LABEL ).setLabel( _( 653 ) )
				LOG( LOG_INFO, "Login Failed: [%s]" , msg )
#				label = ""
#				label2 = "[COLOR=FFFF0000]%s[/COLOR]" % (  _( 611 ) )
#				listitem = xbmcgui.ListItem( label,label2 )
#				self.getControl( SUBTITLES_LIST ).addItem( listitem )
#				label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
#				listitem = xbmcgui.ListItem( label,label2 )
#				self.getControl( SUBTITLES_LIST ).addItem( listitem )
				
				self.getControl( STATUS_LABEL ).setLabel( _( 635 ) )
				self.search_subtitles()
				self.getControl( STATUS_LABEL ).setVisible( True )
			else:
				self.getControl( STATUS_LABEL ).setLabel( _( 635 ) )
				LOG( LOG_INFO, "Login Sucessful: [%s]" , msg )

				##self.osdb_server.getlanguages()
				self.search_subtitles()
				self.getControl( STATUS_LABEL ).setVisible( True )
		else:
				self.getControl( 111 ).setVisible( True )
				self.getControl( STATUS_LABEL ).setLabel( _( 646 ) )
				self.search_subtitles_sub()




    def search_subtitles( self ):
        ok = False
	ok2 = False
	ok3 = False
	msg = ""

	self.getControl( STATUS_LABEL ).setLabel( _( 646 ) )	

	try:
            if ( len( self.file_path ) > 0 ) and not self.file_original_path.find("http") > -1 and not self.set_xbox:
                LOG( LOG_INFO, "Search by hash " +  os.path.basename( self.file_original_path ) )
                self.getControl( STATUS_LABEL ).setLabel( _( 642 ) % ( "...", ) )
                self.set_filehash( hashFile( self.file_original_path ) )
                self.set_filesize( os.path.getsize( self.file_original_path ) )    
                try : ok,msg = self.osdb_server.searchsubtitles( self.file_original_path, self.file_hash, self.file_size,self.lang1,self.lang2 )#, "en" )
                except: ok = False
                LOG( LOG_INFO, "Hash Search: " + msg )        
            if ( len( self.search_string ) > 0 ):
                LOG( LOG_INFO,"Search by name " +  self.search_string )
                self.getControl( STATUS_LABEL ).setLabel( _( 642 ) % ( "......", ) )
                ok2,msg2 = self.osdb_server.searchsubtitlesbyname( self.search_string, self.lang1 )#, "en" )
                LOG( LOG_INFO, "Name Search: " + msg2 )
                ok3,msg3 = self.osdb_server.searchsubtitlesbyname_alt( self.search_string, self.lang2 , self.lang1 )#, "en" )
                LOG( LOG_INFO, "Name 2 Search: " + msg3 )
            self.osdb_server.mergesubtitles()
            if not ok and not ok2 and not ok3:
                self.getControl( STATUS_LABEL ).setLabel( _( 634 ) % ( msg, ) )
            if self.osdb_server.subtitles_list:
                label = ""
                label2 = "[COLOR=FFFF0000]%s[/COLOR]" % (  _( 611 ) )
                listitem = xbmcgui.ListItem( label,label2 )
                self.getControl( SUBTITLES_LIST ).addItem( listitem )
                label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
                listitem = xbmcgui.ListItem( label,label2 )
                self.getControl( SUBTITLES_LIST ).addItem( listitem )
                for item in self.osdb_server.subtitles_list:
		    
                    listitem = xbmcgui.ListItem( label=item["language_name"], label2=item["filename"], iconImage=item["rating"], thumbnailImage=item["language_flag"] )
                    

                    if item["sync"]:
                        listitem.setProperty( "sync", "true" )
                    else:
                        listitem.setProperty( "sync", "false" )
                    self.getControl( SUBTITLES_LIST ).addItem( listitem )
            else:
		    
					label = ""
					label2 = "[COLOR=FFFF0000]%s[/COLOR]" % (  _( 611 ) )
					listitem = xbmcgui.ListItem( label,label2 )
					self.getControl( SUBTITLES_LIST ).addItem( listitem )
					label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
					listitem = xbmcgui.ListItem( label,label2 )
					self.getControl( SUBTITLES_LIST ).addItem( listitem )
		    



            movie_title1 = self.search_string.replace("+"," ")
            self.getControl( STATUS_LABEL ).setLabel( _( 744 ) % ( str( len ( self.osdb_server.subtitles_list ) ), movie_title1, ) )
	    
            self.setFocus( self.getControl( SUBTITLES_LIST ) )
            self.getControl( SUBTITLES_LIST ).selectItem( 0 )
	    
        except Exception, e:
            error = _( 634 ) % ( "search_subtitles:" + str ( e ) ) 
            LOG( LOG_ERROR, error )
            return False, error
        
    def search_subtitles_sub( self ):
        self.getControl( 111 ).setVisible( True )
	self.getControl( 110 ).setVisible( False )
	self.getControl( STATUS_LABEL ).setLabel( _( 642 ) % ( "...", ) )
	sublightWebService = SublightUtils.SublightWebService()
	session_id = sublightWebService.LogInAnonymous()
	self.set_session(session_id)
	
	videoInfoTag = xbmc.Player().getVideoInfoTag()
        movie_year  = ( videoInfoTag.getYear(), "" ) [ videoInfoTag.getYear() == 0 ]
	movie_title = self.search_string.replace ("+"," ")
	
	video_hash = "0000000000000000000000000000000000000000000000000000"
	#if not self.set_temp:
	##md5_video_hash = SublightUtils.calculateMD5VideoHash( self.file_original_path )
	##video_hash     = sublightWebService.GetFullVideoHash( session_id, md5_video_hash )
	if not self.set_xbox and not self.file_original_path.find("http") > -1:
		md5_video_hash = SublightUtils.calculateMD5VideoHash( self.file_original_path )
		video_hash     = sublightWebService.GetFullVideoHash( session_id, md5_video_hash )
	if video_hash == "":
		video_hash = "0000000000000000000000000000000000000000000000000000"
	
	subtitles = []
        language1 = SublightUtils.toSublightLanguage( self.lang1 )
        language2 = SublightUtils.toSublightLanguage(  self.lang2 )
        language3 = SublightUtils.toSublightLanguage( "0" )
	
	season = xbmc.getInfoLabel("VideoPlayer.Season")
	episode = xbmc.getInfoLabel("VideoPlayer.Episode")
	title = xbmc.getInfoLabel("VideoPlayer.TVshowtitle")

	
	if (len(episode) > -1):
		movie_year = ""
	
	if not (len(title) > 0) or self.manuall:	
		movie_title = self.search_string.replace ("+"," ")
		episode = ""
		season = ""
		movie_year = ""
	else:
		movie_title = title	

	LOG( LOG_INFO, "Sublight Hash [%s]" , str(video_hash) )
	LOG( LOG_INFO, "Sublight Languages: [%s]" , language1 +" & "+ language2 )
	LOG( LOG_INFO, "Sublight Search String [%s]" , movie_title+season+episode )
	self.getControl( STATUS_LABEL ).setLabel( _( 642 ) % ( "......", ) )
	subtitles, requestXML = sublightWebService.SearchSubtitles(session_id, video_hash, movie_title, movie_year,season, episode, language2, language1, language3 )
	self.set_subtitles(subtitles)
	if len(subtitles) == 0 :
                label = ""
                label2 = "[COLOR=FFFF0000]%s[/COLOR]" % (  _( 610 ) )
                listitem = xbmcgui.ListItem( label,label2 )
                self.getControl( SUBTITLES_LIST ).addItem( listitem )
                label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
                listitem = xbmcgui.ListItem( label,label2 )
                self.getControl( SUBTITLES_LIST ).addItem( listitem )
						


	else:
                label = ""
                label2 = "[COLOR=FFFF0000]%s[/COLOR]" % (  _( 610 ) )
                listitem = xbmcgui.ListItem( label,label2 )
                self.getControl( SUBTITLES_LIST ).addItem( listitem )
                label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
                listitem = xbmcgui.ListItem( label,label2 )
                self.getControl( SUBTITLES_LIST ).addItem( listitem )
                for subtitle in subtitles:


					release       =                          subtitle[ "release" ]
					language      =                          subtitle[ "language" ]
					isLinked      =                          subtitle[ "isLinked" ]
					rate          =                          subtitle[ "rate" ]
					icon_flag     = toOpenSubtitles_two(language) + ".png"
					#print str(subtitle[ "isLinked" ])
					listitem = xbmcgui.ListItem( label=language, label2=release, thumbnailImage=str(icon_flag), iconImage=str(int(round(rate*2))) )
					if str(subtitle[ "isLinked" ]) == "true":
						listitem.setProperty( "sync", "true" )
					else:
						listitem.setProperty( "sync", "false" )
						
					print str(isLinked)	
					self.getControl( SUBTITLES_LIST ).addItem( listitem )
		
	movie_title1 = self.search_string.replace("+"," ")
	self.getControl( STATUS_LABEL ).setLabel( _( 744 ) % ( str( len ( self.subtitles ) ), movie_title1, ) )
	self.setFocus( self.getControl( SUBTITLES_LIST ) )
	self.getControl( SUBTITLES_LIST ).selectItem( 0 )
    
    
    def show_control( self, controlId ):
        self.getControl( STATUS_LABEL ).setVisible( controlId == STATUS_LABEL )
        self.getControl( SUBTITLES_LIST ).setVisible( controlId == SUBTITLES_LIST )
        page_control = ( controlId == STATUS_LABEL )
        try: self.setFocus( self.getControl( controlId + page_control ) )
        except: self.setFocus( self.getControl( controlId ) )


    def file_download(self, url, dest):
        dp = xbmcgui.DialogProgress()
        try:
            urllib.urlretrieve( url, dest, lambda nb, bs, fs, url=url: self._pbhook( nb, bs, fs, url, dp ) )
            LOG( LOG_INFO, "download succesfull" )
            return True, "Downloaded"
        except Exception, e:
            error = _( 634 ) % ( str ( e ) ) 
            LOG( LOG_ERROR, error )
            return False, error

    def _pbhook(self, numblocks, blocksize, filesize, url=None, dp=None):
        try:
            percent = min( ( numblocks*blocksize*100 ) / filesize, 100 )
            LOG( LOG_INFO, "download precent %s" % ( precent, ) )
        except:
            percent = 100
        if dp.iscanceled(): 
            LOG( LOG_INFO, "Subtitle download cancelled" )  
            

    def download_subtitles(self, pos):
        LOG( LOG_INFO, "download_subtitles" )
        if self.osdb_server.subtitles_list:
            

            filename = self.osdb_server.subtitles_list[pos]["filename"]
            subtitle_format = self.osdb_server.subtitles_list[pos]["format"]
            url = self.osdb_server.subtitles_list[pos]["link"]
            local_path = self.sub_folder
            zip_filename = xbmc.translatePath( os.path.join( local_path, "zipsubs.zip" ) )
            
            sub_filename = os.path.basename( self.file_path )
            form = self.osdb_server.subtitles_list[pos]["format"]
            lang = self.osdb_server.subtitles_list[pos]["language_id"]
            subName1 = sub_filename[0:sub_filename.rfind(".")] 
            if subName1 == "":
				subName1 = self.search_string.replace("+", " ")
            if self.set_temp:
				subName1 = self.search_string.replace("+", " ")
            LOG( LOG_INFO, url+"   " + zip_filename)  
            self.file_download( url, zip_filename )
	    self.extract_subtitles( filename, form, lang,subName1, subtitle_format, zip_filename, local_path )

    def download_subtitles_sub(self, pos):
        subtitle_id   =                          self.subtitles[pos][ "subtitleID" ]
        title         =                          self.subtitles[pos][ "title" ]
        year          = SublightUtils.toInteger( self.subtitles[pos][ "year" ] )
        release       =                          self.subtitles[pos][ "release" ]
        language      =                          self.subtitles[pos][ "language" ]
        mediaType     =                          self.subtitles[pos][ "mediaType" ]
        numberOfDiscs = SublightUtils.toInteger( self.subtitles[pos][ "numberOfDiscs" ] )
 
	self.getControl( STATUS_LABEL ).setLabel(  _( 649 ) )
	sublightWebService = SublightUtils.SublightWebService()
        ticket_id, download_wait = sublightWebService.GetDownloadTicket(self.session_id, subtitle_id)
	if ticket_id != "" :
	    if download_wait > 0 :
		time.sleep(float(download_wait))

            subtitle_b64_data = sublightWebService.DownloadByID(self.session_id, subtitle_id, ticket_id)
            
            base64_file_path = os.path.join(  self.sub_folder, "subtitle.b64" )
            base64_file      = open(base64_file_path, "wb")
            base64_file.write( subtitle_b64_data )
            base64_file.close()
            
            base64_file = open(base64_file_path, "r")
             
            zip_file_path = os.path.join( self.sub_folder , "subtitle.zip" )
            zip_file      = open(zip_file_path, "wb")
                     
            base64.decode(base64_file, zip_file)

            base64_file.close()
            zip_file.close()

            filename = ""
            subtitle_format = "srt"
            local_path = self.sub_folder
            zip_filename = zip_file_path
            sub_filename = os.path.basename( self.file_path )
            form = "srt"
            lang = str(toOpenSubtitles_two(language))
            subtitle_lang = lang
            subName1 = sub_filename[0:sub_filename.rfind(".")] 
            if subName1 == "":
				subName1 = self.search_string.replace("+", " ")

            movie_files     = []
            number_of_discs = int(numberOfDiscs)
            if number_of_discs == 1 :
                movie_files.append(sub_filename)
            elif number_of_discs > 1 and not self.set_temp:

                regexp = movie_file
                regexp = regexp.replace( "\\", "\\\\" )
                regexp = regexp.replace( "^", "\^" )
                regexp = regexp.replace( "$", "\$" )
                regexp = regexp.replace( "+", "\+" )
                regexp = regexp.replace( "*", "\*" )
                regexp = regexp.replace( "?", "\?" )
                regexp = regexp.replace( ".", "\." )
                regexp = regexp.replace( "|", "\|" )
                regexp = regexp.replace( "(", "\(" )
                regexp = regexp.replace( ")", "\)" )
                regexp = regexp.replace( "{", "\{" )
                regexp = regexp.replace( "}", "\}" )
                regexp = regexp.replace( "[", "\[" )
                regexp = regexp.replace( "]", "\]" )
                regexp = re.sub( "\d+", "\\d+", regexp )
                regex  = re.compile( regexp, re.IGNORECASE )
                
                
                movie_dir  = os.path.dirname  (self.file_path)
                movie_file = os.path.basename (self.file_path)
                
                files = os.listdir( movie_dir )
                for file in files :
                    if regex.match( self.file_path ) != None:
                        movie_files.append(self.file_path)
                

                movie_files.sort()
                

            if not zipfile.is_zipfile( zip_file_path ) :

				self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
				label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
				listitem = xbmcgui.ListItem( label,label2 )
				self.getControl( SUBTITLES_LIST ).addItem( listitem )
            else :

                self.getControl( STATUS_LABEL ).setLabel(  _( 652 ) )
                zip = zipfile.ZipFile (zip_file_path, "r")
                i   = 0
                for zip_entry in zip.namelist():

                    file_name = zip_entry
                    i         = i + 1
                    if i <= len( movie_files ) :
                    
						sub_ext  = os.path.splitext( file_name )[1]
						sub_name = os.path.splitext( movie_files[i - 1] )[0]
						if self.set_temp:
							sub_name = self.search_string.replace("+", " ")
							
						file_name = "%s.%s%s" % ( sub_name, subtitle_lang, sub_ext )   
                    
                    file_path = os.path.join(self.sub_folder, file_name)
                    ##LOG( LOG_INFO, "File Path "+ file_name )
                    outfile   = open(file_path, "wb")
                    outfile.write( zip.read(zip_entry) )
                    outfile.close()
                zip.close()
                xbmc.Player().setSubtitles(xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib','dummy.srt' ) ) )
                time.sleep(2)
                xbmc.Player().setSubtitles(file_path)

            os.remove(base64_file_path)
            os.remove(zip_file_path)
            self.exit_script()            
            


	     
    def extract_subtitles(self, filename, form, lang, subName1, subtitle_format, zip_filename, local_path ):
        LOG( LOG_INFO, "extract_subtitles" )
        
        try:
            un = unzip.unzip()
            files = un.get_file_list( zip_filename )
            if not zipfile.is_zipfile( zip_filename ) :
            	self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
            	subtitle_set = False
            	label = ""
            	label2 = "[COLOR=FFFF0000]%s[/COLOR]" % ( _( 610 ) )
            	listitem = xbmcgui.ListItem( label,label2 )
            	self.getControl( SUBTITLES_LIST ).addItem( listitem )
            	label2 = "[COLOR=FF00FF00]%s[/COLOR]" % ( _( 612 ) )
            	listitem = xbmcgui.ListItem( label,label2 )
            	self.getControl( SUBTITLES_LIST ).addItem( listitem )
			
	    else:
	    	self.getControl( STATUS_LABEL ).setLabel( _( 650 ) )
            LOG( LOG_INFO, _( 631 ) % ( zip_filename, local_path ) )
            un.extract( zip_filename, local_path )
            LOG( LOG_INFO, _( 644 ) % ( local_path ) )
            self.getControl( STATUS_LABEL ).setLabel( _( 651 ) )
            LOG( LOG_INFO, "Number of subs in zip:[%s]" ,str(len(files)) )


#            for item in files:
#			if ( item.find( "srt" )  < 0 ) and ( item.find( "sub" )  < 0 ) and ( item.find( "txt" )  < 0 ):
#			        os.remove ( os.path.join( local_path, item ) )

#			if ( item.find( "srt" )  > 0 ) or ( item.find( "sub" )  > 0 ) or ( item.find( "txt" )  > 0 ):
#				sub_filenameOrig = globals.EncodeLocale(subName1 + "." + lang  + "." + "srt")
#				if os.path.exists(os.path.join( local_path, sub_filenameOrig )):
#					os.remove ( os.path.join( local_path, sub_filenameOrig ))
#				
#				os.rename (( os.path.join( local_path, item ) ),( os.path.join( local_path, sub_filenameOrig ) ))
#				name_change = 1
#				xbmc.Player().setSubtitles( os.path.join( os.getcwd(), 'resources', 'lib','dummy.srt' ) ) 
#				LOG( LOG_INFO, "Dummy Subtitle" )
#				time.sleep(2)
#				xbmc.Player().setSubtitles( os.path.join( local_path, sub_filenameOrig ) )
#				LOG( LOG_INFO, "Subtitle Renamed to " + sub_filenameOrig )
#				subtitle_set = True
            movie_files     = []
            number_of_discs = 1
            sub_filename = os.path.basename( self.file_path )
            if number_of_discs == 1 :
                movie_files.append(sub_filename)
            elif number_of_discs > 1 and not self.set_temp:

                regexp = movie_file
                regexp = regexp.replace( "\\", "\\\\" )
                regexp = regexp.replace( "^", "\^" )
                regexp = regexp.replace( "$", "\$" )
                regexp = regexp.replace( "+", "\+" )
                regexp = regexp.replace( "*", "\*" )
                regexp = regexp.replace( "?", "\?" )
                regexp = regexp.replace( ".", "\." )
                regexp = regexp.replace( "|", "\|" )
                regexp = regexp.replace( "(", "\(" )
                regexp = regexp.replace( ")", "\)" )
                regexp = regexp.replace( "{", "\{" )
                regexp = regexp.replace( "}", "\}" )
                regexp = regexp.replace( "[", "\[" )
                regexp = regexp.replace( "]", "\]" )
                regexp = re.sub( "\d+", "\\d+", regexp )
                regex  = re.compile( regexp, re.IGNORECASE )
                
                
                movie_dir  = os.path.dirname  (self.file_path)
                movie_file = os.path.basename (self.file_path)
                
                files = os.listdir( movie_dir )
                for file in files :
                    if regex.match( self.file_path ) != None:
                        movie_files.append(self.file_path)
                

                movie_files.sort()
                
            if not zipfile.is_zipfile( zip_filename ) :

				self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
				label2 = "[COLOR=FF00FF00]%s[/COLOR]" % (  _( 612 ) )
				listitem = xbmcgui.ListItem( label,label2 )
				self.getControl( SUBTITLES_LIST ).addItem( listitem )
            else :
                self.getControl( STATUS_LABEL ).setLabel(  _( 652 ) )
                zip = zipfile.ZipFile (zip_filename, "r")
                i   = 0
                for zip_entry in zip.namelist():
                    LOG( LOG_INFO, "Zip [%s]" , self.sub_folder )
                    if (zip_entry.find( "srt" ) < 0)  and (zip_entry.find( "sub" ) < 0)  and (zip_entry.find( "txt" )< 0) :
                		LOG( LOG_INFO, "Brisi " + os.path.join( self.sub_folder, zip_entry ) )
                		os.remove ( os.path.join( self.sub_folder, zip_entry ) )

                    
                    
                    if ( zip_entry.find( "srt" )  > 0 ) or ( zip_entry.find( "sub" )  > 0 ) or ( zip_entry.find( "txt" )  > 0 ):
                    
						if i == 0 :
						
							i         = i + 1
							file_name = zip_entry
							sub_ext  = os.path.splitext( file_name )[1]
							sub_name = os.path.splitext( movie_files[i - 1] )[0]
							if self.set_temp:
								sub_name = self.search_string.replace("+", " ")
									
							file_name = "%s.%s%s" % ( sub_name, str(lang), ".srt" )
							file_path = os.path.join(self.sub_folder, file_name)
							outfile   = open(file_path, "wb")
							outfile.write( zip.read(zip_entry) )
							outfile.close()
							os.remove ( os.path.join( self.sub_folder, zip_entry ) )
                zip.close()
                xbmc.Player().setSubtitles(xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib','dummy.srt' ) ) )
                LOG( LOG_INFO, "Dummy set")
                time.sleep(2)
                xbmc.Player().setSubtitles(file_path)


            os.remove(zip_filename)
            self.getControl( STATUS_LABEL ).setLabel( _( 652 ) )
            self.exit_script()            



	except Exception, e:
            error = _( 634 ) % ( str ( e ) )
            LOG( LOG_ERROR, error )
            


    def keyboard(self):
		sep = xbmc.translatePath(os.path.dirname(self.file_original_path))
		default = sep.split(os.sep)
		dir = default.pop()
		if str(dir) == "":
			default = sep.split("/")
			dir = default.pop()
		kb = xbmc.Keyboard(dir, 'Enter The Search String', False)
		
		LOG( LOG_INFO, "Directory: [%s] " , dir + str(default) )
		text = self.search_string
		kb.doModal()
		if (kb.isConfirmed()):
			text = kb.getText()
    		
    		self.search_string = text.replace(" ","+")
    		LOG( LOG_INFO, "Keyboard Entry: [%s]" ,  self.search_string )
    		self.manuall = True
    		self.connect()
    		
    def exit_script( self, restart=False ):
        ##if self.service == "OpenSubtitles":
	    	##self.connThread.join()
        self.close()

    def onClick( self, controlId ):

        if ( self.controlId == SUBTITLES_LIST ) and (self.getControl( SUBTITLES_LIST ).getSelectedPosition() > 1):
            if self.service == "OpenSubtitles":
            	self.download_subtitles( (self.getControl( SUBTITLES_LIST ).getSelectedPosition())-2 )
            	LOG( LOG_INFO, "Position: [%s]" ,  "Open "+ str(self.getControl( SUBTITLES_LIST ).getSelectedPosition()) )
            	LOG( LOG_INFO, "Control Id: [%s]" ,  "open "+str(controlId) )
            else:
            	self.download_subtitles_sub( (self.getControl( SUBTITLES_LIST ).getSelectedPosition())-2 )
            	LOG( LOG_INFO, "Position: [%s]" ,  "Sub "+str(self.getControl( SUBTITLES_LIST ).getSelectedPosition()) )
	
            	LOG( LOG_INFO, "Control Id: [%s]" ,  "Sub "+str(controlId) )
		
    	if ( self.controlId == SUBTITLES_LIST ) and (self.getControl( SUBTITLES_LIST ).getSelectedPosition() == 0):
    		
    		if (self.service == "OpenSubtitles"):
				self.service = "Sublight"
				self.connect()
    		else:
    			self.service = "OpenSubtitles"
    			self.connect()
    	if ( self.controlId == SUBTITLES_LIST ) and (self.getControl( SUBTITLES_LIST ).getSelectedPosition() == 1):    
				self.keyboard()  
    
    def onFocus( self, controlId ):
    	self.controlId = controlId
	
def onAction( self, action ):
	if ( action.getButtonCode() in CANCEL_DIALOG ):
            self.exit_script()


