# 9Anime anime downloader

There are two scripts (Anime_Downloader.py, Anime_Scraper.py) to download given anime to a directory and to extract direct download links.
Anime_Scraper.py scraper is used to collect and extract direct anime download links from 9anime.to (From its Mp4Upload server)

## Getting started

- Clone the project using to your local machine

### Prerequisites

- Make sure python3 and pip3 is installed

### Installing

Download the dependancies using requirements.txt file

```
pip3 install -r requirements.txt 
```

## Running the script

- Navigate to cloned directory
- Execute the script(s)

### To extract the direct download URLs
    ```
    python3 ./Anime_Scraper.py
    ```
    - When prompted :
        * Enter anime url (ex : https://9anime.to/watch/sword-art-online.5y9/7jm50n1)
        * Enter starting episode 
        * Enter end episode

### To extract direct URLs and download into a directory
    ```
    python3 ./Anime_Downloader.py
    ```
    - When prompted :
        * Enter directory to save files (ex : C:\Users\user\Desktop\)
        * Enter anime url (ex : https://9anime.to/watch/sword-art-online.5y9/7jm50n1)
        * Enter starting episode 
        * Enter end episode

## Authors

* **Oshan Mendis** - *Author* - [Oshan96](https://github.com/Oshan96)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Disclaimer

This software has been developed only for educational purposes by the [Author](https://github.com/Oshan96). By no means this encourage content piracy. Please support original content creators!