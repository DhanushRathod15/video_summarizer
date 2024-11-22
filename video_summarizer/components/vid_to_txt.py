import whisper
import ffmpeg
import tempfile
import os
import sys
import warnings
from dataclasses import dataclass
from video_summarizer.logger import logger
from video_summarizer.exception import CustomException
import sys


@dataclass
class Config():
    acodec : str = "pcm_s16le"
    audio_channel: int = 1
    audio_rate: str = '16k'
    output_dir_name: str = 'transcript_text'


class VideoToText:
    def __init__(self, config: Config):
        try:
            self.acodec = config.acodec
            self.ac = config.audio_channel 
            self.ar = config.audio_rate
            self.output_dir = config.output_dir_name
        except Exception as e:
            raise CustomException(e, sys)

    def get_audio(self, paths) -> dict:
        try:
            temp_dir = tempfile.gettempdir()
            audio_paths= {}
            for path in paths:
                filename = os.path.basename(path).split('.')[0]
                logger.info(f"Extracting audio from {os.path.basename(path)}...")
                output_path = os.path.join(temp_dir, f"{filename}.wav")

                ffmpeg.input(path).output(
                    output_path,
                    acodec=self.acodec, ac=self.ac, ar=self.ar
                ).run(quiet=True, overwrite_output=True)
                audio_paths[path] = output_path
            return audio_paths
        except Exception as e:
            raise CustomException(e, sys)

    def write_transcript(self, audio_path, text_path, transcribe: callable):
        try:
            logger.info(f"Generating transcript for {os.path.basename(audio_path)} audio... This might take a while.")

            warnings.filterwarnings("ignore")
            result = transcribe(audio_path)
            warnings.filterwarnings("default")
            
            logger.info(f"Writing transcript for the video")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
            return result
        except Exception as e:
            raise CustomException(e, sys)

    def get_transcript(self, audio_paths: list, output_text: bool, output_dir: str, transcribe: callable):
        try:
            text_path = output_dir if output_text else tempfile.gettempdir()
            for path, audio_path in audio_paths.items():
                filename = os.path.basename(path).split('.')[0]
                text_path = os.path.join(text_path, f"{filename}.txt")

                result = self.write_transcript(audio_path, text_path, transcribe)
            return result
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_stt(self, video_path:str, model:str, srt:bool, verbose:bool, task:str):
        os.makedirs(self.output_dir, exist_ok=True)
        if model.endswith(".en"):
            print(f"{model} is a English model")
        model = whisper.load_model(model)
        audio = self.get_audio(video_path)
        subtitle = self.get_transcript(
                    audio, srt, self.output_dir, lambda audio_path: model.transcribe(audio_path, 
                                                    verbose=verbose, task=task))
        return subtitle    