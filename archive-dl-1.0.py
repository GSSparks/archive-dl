#! /bin/python
# archive-dl.py

import re
import argparse
import requests
from urllib.parse import unquote
from clint.textui import progress
from bs4 import BeautifulSoup


def determinePage(url):
    if '@' in url:
        print('Found userpage: ' + url)
        userpage(url)
    else:
        getpage = requests.get(
            url,
            headers={'user-agent': 'archive-dl'},
            stream=True
        )
        getpage_soup = BeautifulSoup(getpage.text, 'html.parser')
        items = getpage_soup.find('div', {'id': 'theatre-ia-wrap'})
        if items:
            sronly = getpage_soup.find('div', {'class': 'streamo'})
            if sronly:
                print('Found Stream Only page: ' + url)
                streamonlypage(url)
            else:
                print('Found video page: ' + url)
                videopage(url)
        elif getpage_soup.find('div', {'class': 'download-directory-listing'}):
            print('Found download page: ' + url)
            downloadpage(url)
        else:
            print('Maybe a collection? ' + url)
            userpage(url)


def downloadFile(name, dl_url):
    r = requests.get(dl_url, headers={'user-agent': 'archive-dl'}, stream=True)
    if r.status_code == 200:
        with open(name, 'wb') as f:
            print("Downloading %s" % name)
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(
                r.iter_content(chunk_size=1024),
                expected_size=(total_length / 1024) + 1
            ):
                if chunk:
                    f.write(chunk)
                    f.flush()
    else:
        print('File not found.')


def downloadpage(url):
    getpage = requests.get(url, headers={'user-agent': 'archive-dl'}, stream=True)
    getpage_soup = BeautifulSoup(getpage.text, 'html.parser')
    download = getpage_soup.findAll('a')
    if verbose:
        print('Looking in ' + url)
    findFiles(url, download)
    findDirectories(url, download)


def findDirectories(url, download):
    loop = True
    while loop:
        linksFound = False
        for links in download:
            folder = links.get('href')
            if (
                folder and folder.endswith('/') and
                not any(folder.endswith(suffix) for suffix in (
                    'create/', 'web/', 'about/', '.org/', 'projects/', 'donate/', '../'
                ))
            ):
                upurl = url + folder
                if verbose:
                    print('Looking in ' + upurl)
                getpage = requests.get(upurl, headers={'user-agent': 'archive-dl'}, stream=True)
                getpage_soup = BeautifulSoup(getpage.text, 'html.parser')
                updownload = getpage_soup.findAll('a')
                findFiles(upurl, updownload)
                linksFound = True
        loop = linksFound
        if loop:
            download = updownload
            url = upurl


def findFiles(url, download):
    foundlist = []
    extensions = [
        ('.ia.mp4', False), ('.mp4', False), ('.mkv', False), ('.m.k.v', False),
        ('.avi', False), ('.mp3', True), ('.zip', None)
    ]
    for ext, audio_required in extensions:
        for i in download:
            dl = i.get('href')
            if dl:
                if verbose:
                    print('Looking at ' + dl)
                if audio_required is not None and yesAudio != audio_required:
                    continue
                if ext.replace('.', '') in dl:
                    dl_url = url + dl
                    name = unquote(dl.rsplit('/', 1)[-1])
                    test = dl.rsplit(ext, 1)[0]
                    if test not in foundlist:
                        foundlist.append(test)
                        if yesDownload:
                            fileExists(name, dl_url)
                        elif justList:
                            print('Found ' + name)
                        else:
                            writeFile(dl_url)


def fileExists(name, dl_url):
    try:
        with open(name):
            pass
        yes = {'yes', 'y'}
        no = {'no', 'n', ''}
        while True:
            ans = input("File {} already exists. Overwrite? N/y ".format(name)).lower()
            if ans in yes:
                downloadFile(name, dl_url)
                break
            elif ans in no:
                return
            else:
                print('Yes or No?')
    except FileNotFoundError:
        downloadFile(name, dl_url)


def getArguments():
    global url, textFile, yesDownload, justList, yesAudio, batchFile, verbose

    parser = argparse.ArgumentParser(description='Downloads media from Archive.org')
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-w', action='store', dest='textFile', default='video-dl.txt',
                       help='Create a list of the videos found with this name.')
    group.add_argument('-d', action='store_true', dest='yesDownload', default=False,
                       help='Downloads videos')
    group.add_argument('-l', action='store_true', dest='justList', default=False,
                       help='Just list the found videos.')

    parser.add_argument('-v', action='store_true', dest='verbose', default=False,
                        help='Print detail info.')
    parser.add_argument('--audio', action='store_true', dest='yesAudio', default=False,
                        help='Find audio files')
    parser.add_argument('--batch', action='store_true', dest='batchFile', default=False,
                        help='Run using a batch of urls.')
    parser.add_argument('URL', type=str, help='<Required> url link')

    results = parser.parse_args()
    url = results.URL.strip().rstrip('/') + '/'
    textFile = results.textFile.strip()
    yesDownload = results.yesDownload
    yesAudio = results.yesAudio
    justList = results.justList
    batchFile = results.batchFile
    verbose = results.verbose


def main():
    getArguments()
    if batchFile:
        with open(url.rstrip('/'), "r") as f:
            for content in f.readlines():
                print('Finding files for ' + content.strip())
                determinePage(content.strip())
                print('\n')
    else:
        determinePage(url)


def streamonlypage(url):
    parseurl = url.split('/')
    game = parseurl[4]
    xmlurl = f'https://archive.org/download/{game}/{game}_files.xml'
    findfile = requests.get(xmlurl, headers={'user-agent': 'archive-dl'}, stream=False)
    if findfile.status_code != 200:
        print('Unable to find file data')
        return
    findfile_soup = BeautifulSoup(findfile.text, 'xml')
    findfile_file = findfile_soup.find(
        'file', {
            'name': re.compile(
                r'3ds$|a78$|bin$|chd$|cso$|gba$|gb$|gbc$|'
                r'iso$|64$|nes$|sfc$|wad$|wbfs$|zip$'
            )
        }
    )
    if not findfile_file:
        print('No file available for download')
        return

    filename = findfile_file.get('name')
    url = f'https://archive.org/download/{game}/{filename}'

    if yesDownload:
        fileExists(filename, url)
    elif justList:
        print('Found ' + url)
    else:
        writeFile(url)


def userpage(url):
    getpage = requests.get(url, headers={'user-agent': 'archive-dl'}, stream=True)
    getpage_soup = BeautifulSoup(getpage.text, 'html.parser')
    items = getpage_soup.findAll('div', {'class': 'item-ttl C C2'})
    for shows in items:
        show = shows.find('a').get('href')
        url = 'https://archive.org' + show + '/'
        videopage(url)


def videopage(url):
    parseurl = url.split('/')
    folderurl = '/'.join(parseurl[4:]).rstrip('/')
    url = f'https://archive.org/download/{folderurl}/'
    if verbose:
        print('Looking in ' + url)
    downloadpage(url)


def writeFile(dl_url):
    print('Writing ' + dl_url + ' to ' + textFile)
    with open(textFile, "a") as f:
        f.write(dl_url + "\n")


if __name__ == "__main__":
    main()
