import sys

from transformers import AutoModelForSeq2SeqLM , AutoTokenizer

from video_summarizer.logger import logger
from video_summarizer.exception import CustomException

def summarize_text(transcript):
    try:
        tokenizer = AutoTokenizer.from_pretrained("philschmid/bart-large-cnn-samsum")
        model = AutoModelForSeq2SeqLM.from_pretrained("philschmid/bart-large-cnn-samsum")
        logger.info("tokenizer and model were downloaded and loaded from hugging face")

        inputs = tokenizer(transcript, max_length=1024, truncation=True, 
                            return_tensors='pt')
        
        summary_ids = model.generate(inputs["input_ids"], num_beams=2, max_length=1024)

        summary = tokenizer.batch_decode( summary_ids, skip_special_tokens=True, 
                            clean_up_tokenization_spaces=False)[0]
        return summary
    except Exception as e:
        raise CustomException(e, sys)