import os
from flask import Flask, render_template, request

from video_summarizer.components.vid_to_txt import Config, VideoToText
from video_summarizer.components.vid_summarizer import summarize_text
from video_summarizer.components.video_downloader import VideoDownloader


app = Flask(__name__)
app.config['upload_dir'] = os.path.join('uploads/')
os.makedirs(app.config['upload_dir'], exist_ok=True)

@app.route('/' , methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        video_file = request.files['video_file']
        transcript_generator = VideoToText(config=Config)
        if video_file:
            filename = video_file.filename
            video_path = os.path.join(os.path.join(app.config['upload_dir'], filename))
            video_file.save(video_path)
            task = 'transcribe'
            option = request.form.get('options')
            if option == 'translate':
                task = 'translate'
                print("translate task is selected by user")
            print ("task selected:", task)
            transcript = transcript_generator.initiate_stt(video_path=[video_path],
                                                            model='tiny',
                                                            srt='True',
                                                            task=task, verbose=False)
        else:
            video_link = request.form['link-input']
            downloader = VideoDownloader(url=video_link, save_path=app.config['upload_dir'])
            video_path = downloader.download()
            task = 'transcribe'
            option = request.form.get('options')
            if option == 'translate':
                task = 'translate'
                print("translate task is selected by user")
            print ("task selected:", task)
            transcript = transcript_generator.initiate_stt(video_path=[video_path],
                                                            model='tiny',
                                                            srt='True',
                                                            task=task, verbose=False)
        transcript_text = transcript['text']
        summary = summarize_text(transcript_text)
        return render_template('index.html', transcript = transcript_text, summary=summary)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)