import re
import requests
import json
from bs4 import BeautifulSoup

class Episode :
    def __init__(self, title, episode):
        self.title = title
        self.episode = episode
        self.id = None
        self.page_url = None
        self.download_url = None

nine_anime_url = "https://9anime.to"
download_9anime_url = None

episodes_url = "https://9anime.to/ajax/film/servers/"

server_name = "Mp4upload"
server_id = None
ts_no = None

session = requests.Session()

episodes = []


def get_mp4upload_index(servers_container) :
    
    global server_name, server_id

    server_names = servers_container.findAll("span", attrs={"class" : "tab"})

    for i in range(0, len(server_names)) :
        if server_names[i].text.lower() == server_name.lower() :
            server_id = server_names[i]["data-name"]
            return i
    
    return None

def extract_page_urls(start_episode, end_episode) :
    global session, episodes, nine_anime_url, download_9anime_url, ts_no, episodes

    anime_page = session.get(download_9anime_url).content
    soup_html = BeautifulSoup(anime_page, "html.parser")

    ts_no = soup_html.find("html")["data-ts"]

    eps_url = episodes_url+"?ts="+ts_no
    print(eps_url)

    epi_data = session.get(eps_url).json()["html"]

    soup = BeautifulSoup(epi_data, "html.parser")

    servers_container = soup.find("span", attrs={"class" : "tabs"}) 

    mp4upload_index = get_mp4upload_index(servers_container)

    if mp4upload_index is None :
        return None

    mp4upload_server = soup.findAll("div", attrs={"class" : "server"})[mp4upload_index]

    episode_ranges = mp4upload_server.findAll("ul", attrs={"class" : "episodes"})

    for episode_range in episode_ranges :
        eps = episode_range.findAll("a", href=True)
        for episode in eps :
            epi_number = int(episode.text)

            if epi_number < start_episode or epi_number > end_episode :
                continue

            # epi = get_episode(epi_number)
            # if epi == None :
            #     continue

            epi = Episode(str(epi_number), "Episode - "+str(epi_number))

            epi.page_url = nine_anime_url + episode["href"]
            epi.id = episode["data-id"]

            episodes.append(epi)

    return episodes

def extract_download_urls() :
    global session
    down_base = "https://9anime.to/ajax/episode/info?"

    for episode in episodes :
        if(episode.id is None) :
            episode.download_url = None
            continue

        url = down_base + "ts="+ts_no+"&id="+episode.id+"&server="+server_id
        target = session.get(url).json()["target"]

        episode.page_url = target

        video_page = session.get(target).content

        string = video_page.decode("utf-8")

        www_base = re.search("false\|(.*)\|devicePixelRatio",string).group(1)

        url_id = re.search("video\|(.*)\|282", string).group(1)

        download_url = "https://"+www_base+".mp4upload.com:282/d/"+url_id+"/video.mp4"

        episode.download_url = download_url

def main() : 
    global episodes, download_9anime_url, episodes_url

    download_9anime_url = input("Anime URL : ")
    start_episode = int(input("Enter Start Episode : "))
    end_episode = int(input("Enter End Episode : "))

    episodes_url = episodes_url + download_9anime_url.split(".")[2].split("/")[0]

    episodes = extract_page_urls(start_episode, end_episode)

    if episodes == None :
        return
    
    extract_download_urls()

    for episode in episodes :
        print(episode.episode, "-", episode.title,":", episode.download_url)

if __name__ == "__main__" :
    main()

