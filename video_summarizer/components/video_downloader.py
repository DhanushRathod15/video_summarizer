import os 
import sys

import requests
import pytube
from video_summarizer.exception import CustomException
from video_summarizer.logger import logger

class VideoDownloader:
    def __init__(self, url: str, save_path: str):
        self.url = url
        self.save_path = save_path
    
    def download(self) -> str | None:
        try: 
            if 'youtu' in self.url:
              return self.__download_youtube()
            else:
                return self.__download_other()
        except Exception as e:
            raise CustomException(e, sys)

    def __download_youtube(self) -> str:
        try:
            yt = pytube.YouTube(self.url)
            video = yt.streams.first()
            video.download(self.save_path)
            logger.info(f"YouTube Video downloaded to {os.path.join(self.save_path,video.default_filename)}")
            return os.path.join(self.save_path, video.default_filename)
        except Exception as e:
            raise CustomException(e, sys)
    
    def __download_other(self) -> str:
        try:
            response = requests.get(self.url, stream=True)
            filename = self.url.split("/")[-1]
            with open(os.path.join(self.save_path, f"{filename}"), "wb") as f:
                for chunck in response.iter_content(chunk_size=4096):
                    f.write(chunck)
            logger.info(f"Video downloaded to {os.path.join(self.save_path,filename)}")
            return os.path.join(self.save_path, filename)
        except Exception as e:
            raise CustomException(e, sys)