# coding: utf-8
# Meant to be run with Python 3

import logging
import os
import subprocess

# Define environment variable names
MUSIC_DIR_VAR = 'MUSIC'

# Misc
LOG_FILE = 'getSongs.log'
SONG_FILE = 'songs.txt'

MUSIC_DIR = ''
YMP3 = 'youtube-dl -w --no-post-overwrites --extract-audio --audio-format mp3 --no-mtime -i -o '
YUPDATE = 'sudo youtube-dl -U'


def getEnvVars():
  global MUSIC_DIR
  
  try:
    MUSIC_DIR = os.environ[MUSIC_DIR_VAR]
    logging.debug('Env ' + MUSIC_DIR_VAR + ': \'' + MUSIC_DIR + '\'')
  except KeyError as e:
    raise KeyError("Could not get environment variable: %s" % e)
  except BaseError as e:
    raise BaseError("Unexpected error while getting environment variables: %s" % e)
  

def setEnvDependentVars():
  global YMP3
  YMP3 += MUSIC_DIR + '/%(title)s.%(ext)s'


def initLog():
    format = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")

    fileHandler = logging.FileHandler(LOG_FILE)
    screenHandler = logging.StreamHandler()

    fileHandler.setFormatter(format)
    screenHandler.setFormatter(format)

    fileHandler.setLevel(logging.DEBUG)
    screenHandler.setLevel(logging.DEBUG)

    logging.getLogger('').addHandler(fileHandler)
    logging.getLogger('').addHandler(screenHandler)
    logging.getLogger('').setLevel(logging.DEBUG)
    
    logging.debug('Logging initialized')


# Skip blank lines and comments (lines beginning with '#')
# Stop when reach line of 'end'; this allows previous tracks
# to accumulate without downloading the same ones multiple times
def getSongLinks(songFilename):
  songLinks = []
  lines = []
  
  try:
    with open(songFilename, 'r') as songFile:
      lines = songFile.readlines()
    songFile.close()
  except FileNotFoundError as e:
    raise FileNotFoundError("Song file '%s' not found" % songFilename)
  except BaseError as e:
    raise BaseError("Unexpected error while getting song list: %s" % e)
      
  for line in lines:
    line = line.strip()

    if len(line) > 0 and '#' != line[0]:
      if 'end' == line:
        logging.info('Reached \'end\' line. Stopping adding songs.')
        break
      else:
        logging.info("Adding song %d: '%s'" % (len(songLinks) + 1, line))
        songLinks.append(line)
      
  return songLinks



def updateDownloader():
  subprocess.call(YUPDATE.split(' '))


def downloadSongs(songLinks):
  numSongs = len(songLinks)
  count = 0
  
  try:    
    for song in songLinks:
      count += 1
      logging.info("Downloading track %d/%d: '%s'" % (count, numSongs, song))
      subprocess.call(str(YMP3 + ' ' + song).split(' '))
  except BaseException as e:
    raise RuntimeError("Error downloading tracks: %s" % e)
    
  logging.info('--------- Finished downloading tracks ---------')



# --- MAIN ---
if '__main__' == __name__:
  try:
    initLog()
    getEnvVars()
    setEnvDependentVars()
    
    # Update to latest version, as not doing so can end in failure
    updateDownloader()

    downloadSongs(getSongLinks(SONG_FILE))
    logging.info('------- Run Complete -------')
    logging.info('')
    
  except BaseException as e:
    logging.error(e)
