import requests
from bs4 import BeautifulSoup as bs4
import webbrowser
import re
import zipfile
import os


def download_zip_url(zip_url):
    page = requests.get(zip_url)
    soup = bs4(page.text, 'html.parser')
    download_link_partial = soup.find('a', {'class': 'btn btn-lg btn-success'})['href']
    download = requests.get('http://www.starfile.fun/download-7s-zip-new/' + download_link_partial)
    try:
        d = download.headers['content-disposition']
    except KeyError:
        if download.headers['Content-Type'] == 'text/html; charset=utf-8':
            print('Sorry, this download has been deleted due to DMCA complaints')
    filename = re.findall("filename=(.+)", d)[0]
    filename = filename[1:-1]
    with open(filename, 'wb') as file:
        file.write(download.content)
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall('.')  # location to extract to
    zip_ref.close()
    os.remove(filename)


def download_song_url(url, fname):
    page = requests.get(url)
    soup = bs4(page.text, 'html.parser')
    download_link_partial = soup.find('a', {'class': 'btn btn-lg btn-success'})['href']
    download = requests.get('http://www.musiqfile.fun/download-7s-sng-new/' + download_link_partial)
    if download.headers['Content-Type']=='text/html; charset=utf-8':
        print('Sorry, this song has been deleted due to DMCA complaints')
    with open(fname+'.mp3', 'wb') as file:
        file.write(download.content)


# Return value[0]: 1- download the album at the url in second return value
#                  2- download single song at the url in second return value
def display_results(links):
    choice_index = 0
    for i in range(len(links)):
        print('Result no. ' + str(i + 1))
        print("Album name: " + links[i]['title'])
        print(str(choice_index) + ": Download album")
        choice_index += 1
        print(str(choice_index) + ": Open Album")
        choice_index += 1
        print(str(choice_index) + ": Go to webpage")
        choice_index += 1
    choice = int(input('Enter the option: '))
    # todo: check for invalid choice
    link = links[choice // 3]
    if choice % 3 == 0:  # download album
        return 1, 'https://starmusiq.fun' + link['href']
    elif choice % 3 == 1:  # print song list
        song_url, song_name = print_song_list('https://starmusiq.fun' + link['href'])
        return 2, song_url,song_name
    elif choice % 3 == 2:  # go to webpage
        webbrowser.open('http://starmusiq.fun' + link['href'])
        q = input('Download this album? y/n: ')
        if q[0] == 'y' or q[0] == 'Y':
            return 1, 'https://starmusiq.fun' + link['href']
        else:
            return False, None


def print_song_list(song_url):
    album_page = requests.get(song_url)
    soup = bs4(album_page.text, 'html.parser')
    table = soup.find('table', {'class': 'table table-condensed table-hover small'})
    rows = table.findAll('tr')
    i = 0
    song_list = []
    while i < len(rows):
        song = {'name': rows[i].find('strong').string,
                'url': rows[i].find('a', {'class': 'label label-info'})['href']}
        song_list.append(song)
        i += 2
    for i in range(len(song_list)):
        print(str(i + 1) + ': ' + song_list[i]['name'])
    choice = int(input('Enter the song number to download: '))
    # todo: add choice to download entire album also
    # todo: check for invalid input
    choice -= 1
    return song_list[choice]['url'], song_list[choice]['name']


if __name__ == '__main__':
    url = 'https://www.starmusiq.fun/search/search-for-blocked-movies-starmusiq.html'
    query = input('Enter album name: ')
    search_result = requests.get(url, params={'query': query})
    soup = bs4(search_result.text, 'html.parser')
    albums_container = soup.find("div", {"id": "search_albums"})
    search_result_links = albums_container.findAll('a', {'class': 'label label-danger'})
    choice = display_results(search_result_links)
    while choice[0] != 1 and choice[0] != 2:
        choice = display_results(search_result_links)
    if choice[0] == 1:
        url = choice[1]
        album_page = requests.get(url)
        soup = bs4(album_page.text, 'html.parser')
        links = soup.findAll('a', {
            'style': 'background:#cb413f;color:#fff;line-height:39px;padding:8px 6px;text-decoration:' +
                     'none;border-radius:.25em; font-weight:700;'})
        download_zip_url(links[1]['href'])  # links[0] is 160kbps link and links[1] is for 320kbps
    elif choice[0] == 2:
        download_song_url(choice[1],choice[2])  # for a song returned value would be the starfile link
