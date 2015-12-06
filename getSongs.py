# coding: utf-8
# Meant to be run with Python 3

import copy
import logging
import os
import subprocess

# Define environment variable names
MUSIC_DIR_VAR = 'MUSIC'

# Misc
LOG_FILE = 'getSongs.log'
SONG_FILE = 'songs.txt'

# These commands must be in list format (hence the split()), as subprocess.command() expects it
YMP3 = 'youtube-dl -w --n-post-overwrites --extract-audio --audio-format mp3 --no-mtime -l'
YUPDATE = 'youtube-dl -U'


def getEnvVars():
  try:
    MUSIC_DIR = os.environ[MUSIC_DIR_VAR]
    logging.debug('Env ' + MUSIC_DIR_VAR + ': \'' + MUSIC_DIR + '\'')
  except KeyError as e:
    raise KeyError("Could not get environment variable: %s" % e)


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
def getSongLinks():
  songLinks = []
  lines = []
  
  try:
    with open(SONG_FILE, 'r') as songFile:
      lines = songFile.readlines()
    songFile.close()
  except FileNotFoundError as e:
      raise FileNotFoundError("Song file '%s' not found" % SONG_FILE)
      
  for line in lines:
    line = line.strip()

    if len(line) != 0 and '#' != line[0]:
      if 'end' == line:
        logging.info('Reached \'end\' of song file. Stopping adding songs.')
        break
      else:
        songLinks.append(line)
      
  return songLinks
    


def updateDownloader():
  subprocess.call(YUPDATE.split(' '))


def downloadSongs():
  # for each link in songs.txt
  #   run YMP3 <SONG>, saving to <MUSIC>
  try:
    # Update to latest version, as not doing so can end in failure
    updateDownloader()
    
    for song in getSongLinks():
      commandList = copy.deepcopy(YMP3)
      commandList.append(song)
      
      logging.info("Downloading link '%s'" % song)
      subprocess.call(str(YMP3 + ' ' + song).split(' '))
  except BaseException as e:
    raise RuntimeError("Error downloading tracks: %s" % e)



# --- MAIN ---
if '__main__' == __name__:
  try:
    initLog()
    getEnvVars()
    downloadSongs()
  except BaseException as e:
    logging.error(e)
  