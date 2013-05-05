import sys
import os
import xbmc
import xbmcgui
import md5
import time
import array
import httplib
import xml.dom.minidom
import struct
DEBUG_MODE = 10

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

# comapatble versions
SETTINGS_VERSIONS = ( "1.0", )
# base paths
BASE_DATA_PATH = os.path.join( "special://temp", "script_data", __scriptname__ )
BASE_SETTINGS_PATH = os.path.join( "special://profile", "script_data", __scriptname__ )

BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
# special action codes
SELECT_ITEM = ( 11, 256, 61453, )
EXIT_SCRIPT = ( 6, 10, 247, 275, 61467, 216, 257, 61448, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
GET_EXCEPTION = ( 216, 260, 61448, )
SELECT_BUTTON = ( 229, 259, 261, 61453, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )
# Log status codes
LOG_INFO, LOG_ERROR, LOG_NOTICE, LOG_DEBUG = range( 1, 5 )

def _create_base_paths():
    """ creates the base folders """
    ##if ( not os.path.isdir( BASE_DATA_PATH ) ):
    ##    os.makedirs( BASE_DATA_PATH )
    ##if ( not os.path.isdir( BASE_SETTINGS_PATH ) ):
    ##    os.makedirs( BASE_SETTINGS_PATH )
_create_base_paths()

def get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

def get_numeric_dialog( default="", heading="", type=3 ):
    """ shows a numeric dialog and returns a value
        - 0 : ShowAndGetNumber		(default format: #)
        - 1 : ShowAndGetDate		(default format: DD/MM/YYYY)
        - 2 : ShowAndGetTime		(default format: HH:MM)
        - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
    """
    dialog = xbmcgui.Dialog()
    value = dialog.numeric( type, heading, default )
    return value

def get_browse_dialog( default="", heading="", type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

def LOG( status, format, *args ):
    if ( DEBUG_MODE >= status ):
        xbmc.output( "%s: %s\n" % ( ( "INFO", "ERROR", "NOTICE", "DEBUG", )[ status - 1 ], format % args, ) )

def hashFile(name): 
      try: 
                 
                longlongformat = 'q'  # long long 
                bytesize = struct.calcsize(longlongformat) 
                    
                f = open(name, "rb") 
                    
                filesize = os.path.getsize(name) 
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash 
    
      except(IOError): 
                return "IOError"




def calculateVideoHash(filename, isPlaying = True):
    #
    # Check file...
    #
    if not os.path.isfile(filename) :
        return ""
    
    if os.path.getsize(filename) < 5 * 1024 * 1024 :
        return ""

    #
    # Init
    #
    sum = 0
    hash = ""
    
    #
    # Byte 1 = 00 (reserved)
    #
    number = 0
    sum = sum + number
    hash = hash + dec2hex(number, 2) 
    
    #
    # Bytes 2-3 (video duration in seconds)
    #
    
    # Playing video...
    if isPlaying == True :
        seconds = int( xbmc.Player().getTotalTime() )
    # Selected video...
    else :
        player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)
        player.play(filename)
        counter = 0
        while not player.isPlaying() and counter < 3 :
            time.sleep(1)
            counter = counter + 1
        seconds = int(player.getTotalTime())
        player.stop()
    
    # 
    sum = sum + (seconds & 0xff) + ((seconds & 0xff00) >> 8)
    hash = hash + dec2hex(seconds, 4)
    
    #
    # Bytes 4-9 (video length in bytes)
    #
    filesize = os.path.getsize(filename)
    
    sum = sum + (filesize & 0xff) + ((filesize & 0xff00) >> 8) + ((filesize & 0xff0000) >> 16) + ((filesize & 0xff000000) >> 24)
    hash = hash + dec2hex(filesize, 12) 
    
    #
    # Bytes 10-25 (md5 hash of the first 5 MB video data)
    #
    f = open(filename, mode="rb")
    buffer = f.read( 5 * 1024 * 1024 )
    f.close()
    
    md5hash = md5.new()
    md5hash.update(buffer)
    
    array_md5 = array.array('B')
    array_md5.fromstring(md5hash.digest())
    for b in array_md5 :
        sum = sum + b

    hash = hash + md5hash.hexdigest()
    
    #
    # Byte 26 (control byte)
    # 
    hash = hash + dec2hex(sum % 256, 2)
    hash = hash.upper()
    
    return hash

#
# Integer => Hexadecimal
#
def dec2hex(n, l=0):
    # return the hexadecimal string representation of integer n
    s = "%X" % n
    if (l > 0) :
        while len(s) < l:
            s = "0" + s 
    return s

#
# Hexadecimal => integer
#
def hex2dec(s):
    # return the integer value of a hexadecimal string s
    return int(s, 16)

#
# String => Integer
#
def toInteger (string):
    try:
        return int( string )
    except :
        return 0

#
# Detect movie title and year from file name...
#
def getMovieTitleAndYear( filename ):
    name = os.path.splitext( filename )[0]

    cutoffs = ['dvdrip', 'dvdscr', 'cam', 'r5', 'limited',
               'xvid', 'h264', 'x264', 'h.264', 'x.264',
               'dvd', 'screener', 'unrated', 'repack', 'rerip', 
               'proper', '720p', '1080p', '1080i', 'bluray']

    # Clean file name from all kinds of crap...
    for char in ['[', ']', '_', '(', ')']:
        name = name.replace(char, ' ')
    
    # if there are no spaces, start making beginning from dots...
    if name.find(' ') == -1:
        name = name.replace('.', ' ')
    if name.find(' ') == -1:
        name = name.replace('-', ' ')
    
    # remove extra and duplicate spaces!
    name = name.strip()
    while name.find('  ') != -1:
        name = name.replace('  ', ' ')
        
    # split to parts
    parts = name.split(' ')
    year = ""
    cut_pos = 256
    for part in parts:
        # check for year
        if part.isdigit():
            n = int(part)
            if n>1930 and n<2050:
                year = part
                if parts.index(part) < cut_pos:
                    cut_pos = parts.index(part)
                
        # if length > 3 and whole word in uppers, consider as cutword (most likelly a group name)
        if len(part) > 3 and part.isupper() and part.isalpha():
            if parts.index(part) < cut_pos:
                cut_pos = parts.index(part)
                
        # check for cutoff words
        if part.lower() in cutoffs:
            if parts.index(part) < cut_pos:
                cut_pos = parts.index(part)
        
    # make cut
    name = ' '.join(parts[:cut_pos])
    return name, year



def toOpenSubtitles_two( id ):
        languages = { "None"  		: "none",
                      "Albanian"  	: "sq",
                      "Arabic"  	: "ar",
                      "Belarusian"  	: "hy",
                      "Bosnian"  	: "bs",
                      "Bulgarian"  	: "bg",
                      "Catalan"  	: "ca",
                      "Chinese"  	: "zh",
                      "Croatian" 	: "hr",
                      "Czech"  		: "cs",
                      "Danish" 		: "da",
                      "Dutch" 		: "nl",
                      "English" 	: "en",
                      "Esperanto" 	: "eo",
                      "Estonian" 	: "et",
                      "Farsi" 		: "fo",
                      "Finnish" 	: "fi",
                      "French" 		: "fr",
                      "Galician" 	: "gl",
                      "Georgian" 	: "ka",
                      "German" 		: "de",
                      "Greek" 		: "el",
                      "Hebrew" 		: "he",
                      "Hindi" 		: "hi",
                      "Hungarian" 	: "hu",
                      "Icelandic" 	: "is",
                      "Indonesian" 	: "id",
                      "Italian" 	: "it",
                      "Japanese" 	: "ja",
                      "Kazakh" 		: "kk",
                      "Korean" 		: "ko",
                      "Latvian" 	: "lv",
                      "Lithuanian" 	: "lt",
                      "Luxembourgish" 	: "lb",
                      "Macedonian" 	: "mk",
                      "Malay" 		: "ms",
                      "Norwegian" 	: "no",
                      "Occitan" 	: "oc",
                      "Polish" 		: "pl",
                      "Portuguese" 	: "pt",
                      "PortugueseBrazil" 	: "pb",
                      "Romanian" 	: "ro",
                      "Russian" 	: "ru",
                      "SerbianLatin" 	: "sr",
                      "Slovak" 		: "sk",
                      "Slovenian" 	: "sl",
                      "Spanish" 	: "es",
                      "Swedish" 	: "sv",
                      "Syriac" 		: "syr",
                      "Thai" 		: "th",
                      "Turkish" 	: "tr.",
                      "Ukrainian" 	: "uk",
                      "Urdu" 		: "ur",
                      "Vietnamese" 	: "vi",
		      "English (US)" 	: "en",
		      "All" 		: "all"
                    }
        return languages[ id ]

def toOpenSubtitlesId( id ):
        languages = { "None"  		: "none",
                      "Albanian"  	: "alb",
                      "Arabic"  	: "ara",
                      "Belarusian"  	: "arm",
                      "Bosnian"  	: "bos",
                      "Bulgarian"  	: "bul",
                      "Catalan"  	: "cat",
                      "Chinese"  	: "chi",
                      "Croatian" 	: "hrv",
                      "Czech"  		: "cze",
                      "Danish" 		: "dan",
                      "Dutch" 		: "dut",
                      "English" 	: "eng",
                      "Esperanto" 	: "epo",
                      "Estonian" 	: "est",
                      "Farsi" 		: "per",
                      "Finnish" 	: "fin",
                      "French" 		: "fre",
                      "Galician" 	: "glg",
                      "Georgian" 	: "geo",
                      "German" 		: "ger",
                      "Greek" 		: "ell",
                      "Hebrew" 		: "heb",
                      "Hindi" 		: "hin",
                      "Hungarian" 	: "hun",
                      "Icelandic" 	: "ice",
                      "Indonesian" 	: "ind",
                      "Italian" 	: "ita",
                      "Japanese" 	: "jpn",
                      "Kazakh" 		: "kaz",
                      "Korean" 		: "kor",
                      "Latvian" 	: "lav",
                      "Lithuanian" 	: "lit",
                      "Luxembourgish" 	: "ltz",
                      "Macedonian" 	: "mac",
                      "Malay" 		: "may",
                      "Norwegian" 	: "nor",
                      "Occitan" 	: "oci",
                      "Polish" 		: "pol",
                      "Portuguese" 	: "por",
                      "PortugueseBrazil" 	: "pob",
                      "Romanian" 	: "rum",
                      "Russian" 	: "rus",
                      "SerbianLatin" 	: "scc",
                      "Slovak" 		: "slo",
                      "Slovenian" 	: "slv",
                      "Spanish" 	: "spa",
                      "Swedish" 	: "swe",
                      "Syriac" 		: "syr",
                      "Thai" 		: "tha",
                      "Turkish" 	: "tur",
                      "Ukrainian" 	: "ukr",
                      "Urdu" 		: "urd",
                      "Vietnamese" 	: "vie",
		      "English (US)" 	: "eng",
		      "All" 		: "all"
                    }
        return languages[ id ]