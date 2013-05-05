import xbmc, xbmcgui, dircache, random, math
# Python script to play an intro before the main movie
# Written by Maverick214 for Plexaeon

movie_title = xbmc.getInfoLabel( "ListItem.Title" )
movie_file = xbmc.getInfoLabel( "ListItem.Filenameandpath" )

path_to_files = xbmc.getInfoLabel( "Skin.String(CinemaPath)" )
fn = dircache.listdir( path_to_files )
r_num = int(math.floor( random.random() * len(fn) ))
IntroFile = path_to_files + fn[r_num]

pl=xbmc.PlayList(1)
pl.clear()
listitem = movie_file
trailitem = 'Movie Intro'
#IntroFile = xbmc.getInfoLabel( "Skin.String(CinemaPath)" )

xbmc.executebuiltin("Activate.Window(10006)")
pl.add(IntroFile, trailitem)
pl.add(movie_file, movie_title)
xbmc.Player().play(pl)