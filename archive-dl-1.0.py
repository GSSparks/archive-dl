#! /bin/python

import re
import argparse
import requests
from urllib.parse import unquote
from clint.textui import progress
from bs4 import BeautifulSoup

def determinePage(url):
    if url.find('@') >= 0: # Test for a userpage
        print('Found userpage: ' + url)
        userpage(url)
    else:
        getpage= requests.get(url, headers={'user-agent': 'archive-dl'}, stream=True)
        getpage_soup=BeautifulSoup(getpage.text, 'html.parser')
        items= getpage_soup.find('div', {'id':'theatre-ia-wrap'}) # Test for a videopage
        if items is not None:
            sronly= getpage_soup.find('div', {'class':'streamo'}) # Test for stream only
            if sronly is not None:
                print('Found Stream Only page: ' + url)
                streamonlypage(url)
            else:
                print('Found video page: ' + url)
                videopage(url)
        elif getpage_soup.find('div', {'class':'download-directory-listing'}) is not None:
            print('Found download page: ' + url)
            downloadpage(url)
        else:
            print('Maybe a collection? ' + url)
            userpage(url) # If it's not a userpage or videopage it's probably a collection
        
def downloadFile(name, dl_url):
    r=requests.get(dl_url, headers={'user-agent': 'archive-dl'}, stream=True)
    if r.status_code == 200:
        with open(name, 'wb') as f:
            print("Downloading %s" % name)
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
        f.close()
    else:
        print('File not found.')

def downloadpage(url):
    getpage = requests.get(url, headers={'user-agent': 'archive-dl'}, stream=True)
    getpage_soup = BeautifulSoup(getpage.text, 'html.parser')
    download = getpage_soup.findAll('a')    
    if verbose is True:
        print('Looking in ' + url)
    findFiles(url, download) # Find files on the download page
    findDirectories(url, download) # Look for directories
    
def findDirectories(url, download):
    loop = True # Create a loop to search through directories if they are found
    while loop is True:
        linksFound = False
        for links in download: # Looking for directories
            folder = links.get('href')
            if folder is not None and folder.endswith('/') and folder.endswith('create/') <= 0 and folder.endswith('web/') <= 0 and folder.endswith('about/') <= 0 and folder.endswith('.org/') <= 0 and folder.endswith('projects/') <= 0 and folder.endswith('donate/') <= 0 and folder.endswith('../') <= 0:
                upurl = url + folder
                if verbose is True:
                    print('Looking in ' + upurl)
                getpage = requests.get(upurl, headers={'user-agent': 'archive-dl'}, stream=True)
                getpage_soup = BeautifulSoup(getpage.text, 'html.parser')
                updownload = getpage_soup.findAll('a')
                findFiles(upurl, updownload) # Find files in the directory
                linksFound = True # Continue the loop if more links are found
        if linksFound is not False:
            loop = True
            download = updownload
            url = upurl
        else:
            loop = False
    
def findFiles(url, download):
    foundlist = []
    for i in download:
        dl= i.get('href')
        if dl is not None and verbose is True:
            print('Looking at ' + dl)
        if dl is not None and yesAudio is False and dl.find('.ia.mp4') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            foundlist.append(dl.rsplit('.ia',1)[0]) # .ia.mp4 files to compare against later
            if yesDownload == True:
                fileExists(name, dl_url)
            elif justList == True:
                print('Found ' + name)
            else:
                writeFile(dl_url)
    for i in download:
        dl = i.get('href')
        if dl is not None and yesAudio is False and dl.find('.mp4') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            test=dl.rsplit('.mp4',1)[0] # Test to see if file has already been grabbed
            if test not in foundlist:
                foundlist.append(test)
                if yesDownload == True:
                    fileExists(name, dl_url)
                elif justList == True:
                    print('Found ' + name)
                else:
                    writeFile(dl_url)
    for i in download:
        dl = i.get('href')
        if dl is not None and yesAudio is False and dl.find('.mkv') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            test=dl.rsplit('.mkv',1)[0] # Test to see if file has already been grabbed
            if test not in foundlist:
                foundlist.append(test)
                if yesDownload == True:
                    fileExists(name, dl_url)
                elif justList == True:
                    print('Found ' + name)
                else:
                    writeFile(dl_url)
    for i in download:
        dl = i.get('href')
        if dl is not None and yesAudio is False and dl.find('.m.k.v') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            test=dl.rsplit('.m.k.v',1)[0] # Test to see if file has already been grabbed
            if test not in foundlist:
                foundlist.append(test)
                if yesDownload == True:
                    fileExists(name, dl_url)
                elif justList == True:
                    print('Found ' + name)
                else:
                    writeFile(dl_url)
    for i in download:
        dl = i.get('href')
        if dl is not None and yesAudio is False and dl.find('.avi') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            test=dl.rsplit('.avi',1)[0] # Test to see if file has already been grabbed
            if test not in foundlist:
                foundlist.append(test)
                if yesDownload == True:
                    fileExists(name, dl_url)
                elif justList == True:
                    print('Found ' + name)
                else:
                    writeFile(dl_url)
    for i in download:
        dl = i.get('href')
        if dl is not None and yesAudio is True and dl.find('.mp3') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            test=dl.rsplit('.mp3',1)[0] # Test to see if file has already been grabbed
            if test not in foundlist:
                foundlist.append(test)
                if yesDownload == True:
                    fileExists(name, dl_url)
                elif justList == True:
                    print('Found ' + name)
                else:
                    writeFile(dl_url)
    for i in download:
        dl = i.get('href')
        if dl is not None and dl.find('.zip') >= 0:
            dl_url= url + dl
            name=unquote(dl.rsplit('/', 1)[-1]) # Grab the name from the url
            test=dl.rsplit('.zip',1)[0] # Test to see if file has already been grabbed
            if test not in foundlist:
                foundlist.append(test)
                if yesDownload == True:
                    fileExists(name, dl_url)
                elif justList == True:
                    print('Found ' + name)
                else:
                    writeFile(dl_url)
        
def fileExists(name, dl_url):
    try:
        file = open(name)
        file.close()
        return
        
        yes = set(['yes','y'])
        no = set(['no','n',''])
        
        while True:
            ans=input("File " + name + " already exists. Overwrite? N/y ").lower()
            if ans in yes:
                downloadFile(name, dl_url)
            elif ans in no:
                return
            else:
                print('Yes or No?')
    except FileNotFoundError:
        downloadFile(name, dl_url)

def getArguments():
    global url, textFile, yesDownload, justList, yesAudio, batchFile, verbose
    
    parser  =   argparse.ArgumentParser(description='Downloads media from Archive.org')
    group   =   parser.add_mutually_exclusive_group()

    group.add_argument('-w',
                        action='store',
                        dest='textFile',
                        default='video-dl.txt',
                        help='Create a list of the videos found with this name.',
                        required=False
                        )
    group.add_argument('-d',
                        action='store_true',
                        dest='yesDownload',
                        default=False,
                        help='Downloads videos',
                        required=False
                        )
    group.add_argument('-l',
                       action='store_true',
                       dest='justList',
                       default=False,
                       help='Just list the found videos.',
                       required=False
                       )
    parser.add_argument('-v',
                        action='store_true',
                        dest='verbose',
                        default=False,
                        help='Print detail info.',
                        required=False
                        )
    parser.add_argument('--audio',
                        action='store_true',
                        dest='yesAudio',
                        default=False,
                        help='Find audio files',
                        required=False
                        )

    parser.add_argument('--batch',
                        action='store_true',
                        dest='batchFile',
                        default=False,
                        help='Run using a batch of urls.',
                        required=False
                        )

    parser.add_argument('URL',
                        type=str,
                        help='<Required> url link'
                        )

    results     =   parser.parse_args()
    url         =   results.URL.strip().rstrip('/') + '/'
    textFile    =   results.textFile.strip()
    yesDownload =   results.yesDownload
    yesAudio    =   results.yesAudio
    justList    =   results.justList
    batchFile   =   results.batchFile
    verbose     =   results.verbose
    return

def main():
    getArguments()
    if batchFile is True:
        with open(url.rstrip('/'), "r") as f:
            for content in f.readlines():
                print('Finding files for ' + content.strip())
                determinePage(content.strip())
                print('\n')
    else:
        determinePage(url)

def streamonlypage(url):
    parseurl = url.split('/')
    game= parseurl[4]
    gameparsed= game.split('_')
    platform= gameparsed[0]
    xmlurl = 'https://archive.org/download/'+game+'/'+game+'_files.xml'
    findfile= requests.get(xmlurl, headers={'user-agent': 'archive-dl'}, stream=False)
    if findfile.status_code != 200:
        print('Unable to find file data')
        return
    findfile_soup= BeautifulSoup(findfile.text, 'xml')
    findfile_file= findfile_soup.find('file', {'name': re.compile(r'3ds$|a78$|bin$|chd$|cso$|gba$|gb$|gbc$|iso$|64$|nes$|sfc$|wad$|wbfs$|zip$')})
    if findfile_file == None:
        print('No file available for download')
        return

    filename = (findfile_file.get('name'))

    url = 'https://archive.org/download/'+game+'/'+filename

    if yesDownload == True:
        fileExists(filename, url)
    elif justList == True:
        print('Found ' + url)
    else:
        writeFile(url)

def userpage(url):
    getpage=requests.get(url, headers={'user-agent': 'archive-dl'}, stream=True)
    getpage_soup=BeautifulSoup(getpage.text, 'html.parser')
    items= getpage_soup.findAll('div', {'class':'item-ttl C C2'})
    for shows in items:
        show= shows.find('a').get('href')
        url= 'https://archive.org'+show+'/'
        videopage(url)

def videopage(url):
    parseurl = url.split('/')
    folderurl = '/'.join(parseurl[4:]).rstrip('/')
    url = 'https://archive.org/download/'+folderurl+'/'
    if verbose is True:
        print('Looking in ' + url)
    downloadpage(url)

def writeFile(dl_url):
    print('Writing ' + dl_url + ' to ' + textFile)
    f = open(textFile, "a")
    f.write(dl_url)
    f.write("\n")
    f.close()
            
if __name__ == "__main__":
    main()
