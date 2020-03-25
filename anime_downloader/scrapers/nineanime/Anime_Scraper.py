import cloudscraper
import json
import sys
import os
from util import Color
from bs4 import BeautifulSoup
from time import sleep
from util.Episode import Episode
from util.Episode import extract_episode_names
from extractors.mp4upload_extractor import Mp4UploadExtractor

title_url = None
isFiller = False

nine_anime_url = "https://9anime.to"
download_9anime_url = None

episodes_url = "https://9anime.to/ajax/film/servers/"

server_name = "Mp4upload"
server_id = None
ts_no = None

site_key = "6LfEtpwUAAAAABoJ_595sf-Hh0psstoatwZpLex1"
api_key = None

cookies = None
gui = None

session = cloudscraper.create_scraper()

episodes = []


def get_token(url):
    global session, site_key, api_key, gui

    try:
        captcha_id = \
        session.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}&invisible=1"
                     .format(api_key, site_key, url)).text.split('|')[1]

        recaptcha_answer = session.get(
            "http://2captcha.com/res.php?key={}&action=get&id={}".format(api_key, captcha_id)).text

        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            sleep(5)
            recaptcha_answer = session.get(
                "http://2captcha.com/res.php?key={}&action=get&id={}".format(api_key, captcha_id)).text

        recaptcha_answer = recaptcha_answer.split('|')[1]

        # print("[Recaptcha answer] : {",recaptcha_answer,"}")
        return recaptcha_answer

    except Exception:
        Color.printer("ERROR", 'Failed to solve ReCaptcha!', gui)
        return None


def get_mp4upload_index(servers_container):
    global server_name, server_id

    server_names = servers_container.findAll("span", attrs={"class": "tab"})

    for i in range(0, len(server_names)):
        if server_names[i].text.lower() == server_name.lower():
            server_id = server_names[i]["data-name"]
            return i

    return None


def verify(token):
    global session
    payload = {
        "g-recaptcha-response": token
    }

    session.post("https://9anime.to/waf-verify", data=payload)


def extract_page_urls(start_episode, end_episode, token):
    global session, episodes, nine_anime_url, download_9anime_url, ts_no, episodes, api_key, cookies, gui

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    })

    if token is None:
        if api_key is None:
            Color.printer("ERROR", "No API Key Provided!", gui)
            sys.exit(0)

        if api_key != "" and api_key != "insert_2captcha_api_key":
            Color.printer("INFO", "Solving recaptcha...", gui)

            token = get_token("https://9anime.to/waf-verify")
            if not token:
                Color.printer("ERROR", "Captcha solving failed!", gui)
                Color.printer("INFO", "Trying to continue ...", gui)
                # sys.exit(0)

    if token:
        verify(token)
    else:
        Color.printer("INFO", "No API key or token given, trying to continue...", gui)
        # cookies = bc.load()         #collect all browser cookies
        # session.cookies = cookies   #set browser cookies for requests

    Color.printer("INFO", "Extracting page URLs...", gui)

    anime_page = session.get(download_9anime_url).content
    soup_html = BeautifulSoup(anime_page, "html.parser")

    ts_no = soup_html.find("html")["data-ts"]

    eps_url = episodes_url + "?ts=" + ts_no

    epi_data = session.get(eps_url).json()["html"]

    soup = BeautifulSoup(epi_data, "html.parser")

    servers_container = soup.find("span", attrs={"class": "tabs"})

    mp4upload_index = get_mp4upload_index(servers_container)

    if mp4upload_index is None:
        return None

    mp4upload_server = soup.findAll("div", attrs={"class": "server"})[mp4upload_index]

    episode_ranges = mp4upload_server.findAll("ul", attrs={"class": "episodes"})

    for episode_range in episode_ranges:
        eps = episode_range.findAll("a", href=True)
        for episode in eps:
            epi_number = int(episode.text)

            if epi_number < start_episode or epi_number > end_episode:
                continue

            # epi = get_episode(epi_number)
            # if epi == None :
            #     continue

            epi = Episode(str(epi_number), "Episode - " + str(epi_number))

            epi.page_url = nine_anime_url + episode["href"]
            epi.id = episode["data-id"]

            episodes.append(epi)

    return episodes


def extract_download_urls():
    global session, gui
    down_base = "https://9anime.to/ajax/episode/info?"

    Color.printer("INFO", "Extracting download URLs...", gui)
    for episode in episodes:
        if (episode.id is None):
            episode.download_url = None
            continue

        url = down_base + "ts=" + ts_no + "&id=" + episode.id + "&server=" + server_id
        target = session.get(url).json()["target"]

        episode.page_url = target

        download_url = Mp4UploadExtractor(target, session).extract_direct_url()

        # video_page = session.get(target).content
        #
        # string = video_page.decode("utf-8")
        #
        # www_base = re.search("false\|(.*)\|devicePixelRatio",string).group(1)
        # url_id = re.search("video\|(.*)\|282", string).group(1)
        #
        # download_url = "https://"+www_base+".mp4upload.com:282/d/"+url_id+"/video.mp4"

        episode.download_url = download_url


def get_epi(eps, num):
    for epi in eps:
        if epi.episode == num:
            return epi

    return None


def set_titles(start_episode, end_episode):
    global episodes, title_url, isFiller

    if not title_url:
        return

    eps = extract_episode_names(title_url, isFiller, start_episode, end_episode)

    for episode in episodes:
        epi = get_epi(eps, episode.episode)
        if epi:
            episode.title = epi.title
            eps.remove(epi)


def write_data():
    global episodes, gui

    Color.printer("INFO", "Writing results to results.csv file...", gui)
    data_file = open("results.csv", "w")
    for episode in episodes:
        data_file.write(episode.episode + "," + episode.download_url + "\n")

    data_file.close()


def main(start_episode=-1, end_episode=-1, token=None):
    global episodes, download_9anime_url, episodes_url, api_key, gui

    start_episode = int(start_episode)
    end_episode = int(end_episode)

    if not token:
        with open("settings.json") as (json_file):
            data = json.load(json_file)
            api_key = data["api_key"]

    if not download_9anime_url:
        download_9anime_url = input("Anime URL : ")

    if start_episode == -1:
        start_episode = int(input("Enter Start Episode : "))

    if end_episode == -1:
        end_episode = int(input("Enter End Episode : "))

    episodes_url = episodes_url + download_9anime_url.split(".")[2].split("/")[0]

    episodes = extract_page_urls(start_episode, end_episode, token)

    if episodes is None:
        return

    if title_url:
        set_titles(start_episode, end_episode)
    else:
        Color.printer("INFO", "animefiller.com URL not provided to collect episode names...", gui)
        Color.printer("INFO", "Skipping collecting episode names...", gui)

    extract_download_urls()

    write_data()


if __name__ == "__main__":
    if sys.platform.lower() == "win32":
        os.system("color")
    main()
