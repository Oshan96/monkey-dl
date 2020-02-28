# 9Anime anime downloader

There are two scripts (Anime_Downloader.py, Anime_Scraper.py) to download given anime to a directory and to extract direct download links.
Anime_Scraper.py scraper is used to collect and extract direct anime download links from 9anime.to (From its Mp4Upload server)

## Getting started

- Clone the project using to your local machine

### Prerequisites

- Make sure python3 and pip3 is installed

### Installing

1) Download the dependancies using requirements.txt file

```
    pip3 install -r requirements.txt 
```
2) Rename settings_example.json as settings.json

3) Open settings.json and set [2captcha](https://2captcha.com/) API key in "api_key"

```json
    "api_key":"insert_2captcha_api_key"
```

> If you don't have a 2captcha API key purchased, you can manually set the needed information by feeding a specific webpage to the application and this functionality will be added sooner.

## Usage

Anime Downloader is a CLI application which takes command line arguments in execution time

To see the full available commands, run

```bash
python3 ./Anime_Downloader.py --help
```

```
usage: Anime_Downloader.py [-h] -u <URL> -n <TITLE_URL> [-d <DIR>] [-s <START>]
                           [-e <END>] [-c <TS_NO>] [-t <THREADS>] [-f <ISFILLER>]

Anime Downloader Command Line Tool

optional arguments:
  -h, --help            show this help message and exit
  -u <URL>, --url <URL> 9Anime.to URL for the anime to be downloaded
  -n <TITLE_URL>, --names <TITLE_URL>
                        https://www.animefillerlist.com/ URL to retrieve
                        episode titles
  -d <DIR>, --directory <DIR>
                        Download destination. Will use the current directory
                        if not provided
  -s <START>, --start <START>
                        Starting episode
  -e <END>, --end <END> End episode
  -c <TS_NO>, --code <TS_NO>
                        data-ts tag value of the given url webpage. Insert
                        this if you don't have 2captcha captcha bypass api_key
  -t <THREADS>, --threads <THREADS>
                        Number of parrallel downloads. Will download
                        sequencially if not provided
  -f <ISFILLER>, --filler <ISFILLER>
                        Whether fillers needed (True/False)

```
## Examples

Download One Piece episodes from 130 to 180 without filler episodes into "K:\Anime\One-Piece" folder with episode names (3 simultanious downloads a time)

```bash
    python3 ./Anime_Downloader -u https://9anime.to/watch/one-piece.ov8/169lyx -s 130 -e 180 -f False -d "F:\Anime\One-Piece" -n https://www.animefillerlist.com/shows/one-piece -t 3
```
![Result](https://i.imgur.com/gRUhQdS.png)

## Authors

* **Oshan Mendis** - *Author* - [Oshan96](https://github.com/Oshan96)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Disclaimer

This software has been developed only for educational purposes by the [Author](https://github.com/Oshan96). By no means this encourage content piracy. Please support original content creators!