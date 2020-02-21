import Anime_Scraper
import urllib.request
import ssl

directory = ""

def download() :
    global directory

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    print("Downloading started...")

    for episode in Anime_Scraper.episodes :
        print("Downloading", episode.episode)
        urllib.request.urlretrieve(episode.download_url, directory+episode.episode+".mp4")

def main() :
    global directory

    directory = input("Save Downloads To : ")
    if directory != "" :
        directory = directory.replace("\\", "/")
        if not directory.endswith("/") :
            directory+="/"

    Anime_Scraper.main()

    download()

if __name__ == "__main__":
    main()
