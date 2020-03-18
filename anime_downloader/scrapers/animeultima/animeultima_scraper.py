import cloudscraper
from bs4 import BeautifulSoup


def get_anime_id(url, session) :
    page = session.get(url).content
    soup_html = BeautifulSoup(page, "html.parser")

    button_with_id = soup_html.find("button", attrs={"class" : "button"})

    if button_with_id :
        return button_with_id["data-id"]

    else :
        meta_tag = soup_html.find("meta", attrs={"property" : "og:image"})
        if meta_tag :
            content_data = meta_tag["content"].split("/")
            return content_data[-2]


def get_start_and_end_page(session, anime_id, start_epi=1, end_epi=50) :
    start_page = 0
    end_page = 0

    data = session.get("https://www1.animeultima.to/api/episodeList?animeId="+anime_id).json()

    last_page = data["last_page"]
    max_total_epis = last_page * 50

    if start_epi == 0 :
        start_epi = 1

    if end_epi == 0 :
        end_epi = 1

    if (max_total_epis - end_epi) % 50 == 0 :
        start_page = round((max_total_epis - end_epi) / 50) - 1
    else :
        start_page = round((max_total_epis - end_epi) / 50)

    if (max_total_epis - start_epi) % 50 == 0 :
        end_page = round((max_total_epis - start_epi) / 50) - 1
    else :
        end_page = round((max_total_epis - start_epi) / 50)

    return (start_page, end_page)

def collect_episodes(anime_id, start_epi, end_epi, start_page, end_page, session, isDub=False) :
    episodes = []
    base_url = "https://www1.animeultima.to/api/episodeList?animeId=" + anime_id + "&page="
    page_counter = start_page

    while(page_counter <= end_page) :
        url = base_url+str(page_counter)

        data = session.get(url).json()
        has_dub = data["anime"]["hasDub"]
        epis = data["episodes"]

        for epi in epis :
            epi_no = int(epi["episode_num"])

            if epi_no < start_epi or epi_no > end_epi:
                continue

            title = epi["title"]




#This will get called initially
#Not fully implemented yet
def extract_episodes(url,names_url,start_epi=1, end_epi=50, isFiller=True, isDub=False, gui=None) :
    session = cloudscraper.create_scraper()
    anime_id = get_anime_id(url, session)
    start_page, end_page = get_start_and_end_page(session, anime_id, start_epi, end_epi)


    # episodes_list = extract_episode_names(names_url, isFiller, start_epi, end_epi, gui)


if __name__ == "__main__":
    session = cloudscraper.create_scraper()
    # id = get_anime_id("https://www1.animeultima.to/a/naruto-shippuuden_395410", session)
    # print(id)
    # print(get_start_and_end_page(session, id, 20, 450))

    # print(get_anime_id("https://www1.animeultima.to/a/naruto-shippuuden_395410", session))
    # print(get_start_and_end_page(1,513))
    print(session.get("https://www1.animeultima.to/faststream/2336").text)


