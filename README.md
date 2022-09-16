# archive-dl
archive.org media downloader

I wrote this python script to make it easier to download all the videos or music from a user or collection on archive.org from the terminal.

The default behavior of this script is to look for videos, mp4's first, followed by mkv's, and finally avi's and write the list of found videos urls in a text file where you can go over them and download them with wget or someother utility. If the --audio flag is set it will look instead for mp3's and do the same. If the -d flag is set it will automatically download the video files in the directory that the script is ran from. 

Other features are the --batch flag which will allow you to download from a batch of user and collection urls listed in a plain text file. The -w flag allows you to name the textfile, and the -l flag will simply list the found videos in the terminal.

Usage: archive-dl [-h] [-w TEXTFILE | -d | -l] [-v] [--audio] [--batch] URL

Downloads media from Archive.org

positional arguments:
  URL          <Required> url link

options:
  -h, --help   show this help message and exit
  -w TEXTFILE  Create a list of the videos found with this name.
  -d           Downloads videos
  -l           Just list the found videos.
  -v           Print detail info.
  --audio      Find audio files
  --batch      Run using a batch of urls.
