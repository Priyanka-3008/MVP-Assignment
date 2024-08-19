from pytube import YouTube
import re
from transformers import pipeline
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from flask import Flask,request,jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import speech_recognition as sr


app= Flask(__name__)


en_tokenizer=AutoTokenizer.from_pretrained("facebook/bart-large-cnn",legacy=False)
en_model=AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")


ar_tokenizer=AutoTokenizer.from_pretrained("malmarjeh/t5-arabic-text-summarization",legacy=False)
ar_model=AutoModelForSeq2SeqLM.from_pretrained("malmarjeh/t5-arabic-text-summarization")


def get_video_transcript(video_id,language_code='en'):
    try:
        transcript=YouTubeTranscriptApi.get_transcript(video_id,languages=[language_code])
        return transcript
    except Exception as e:
        print(f'Error:{e}')
        return None


    
def format_transcript(transcript):
    formatter=SRTFormatter()
    return formatter.format_transcript(transcript)
  
def clean_srt(srt_text):
    clean_text=re.sub(r'\d+\n','',srt_text)
    clean_text=re.sub(r'\n\d{2}:\d{2}:\d{2},\d{3}--\d{2}:\d{2}:\d{2},\d{3}\n',' ',clean_text)
    return clean_text

def download_audio(youtube_url,output_path="/Users/mvp/Desktop/taskflask/YTvideoSummarizer/audio files"):
    yt=YouTube(youtube_url)
    audio_stream=yt.streams.filter(only_audio=True).first()
    audio_stream.download(file_name=output_path)

def convert_audio_to_text(audio_path):
    recognizer=sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio=recognizer.record(source)
    try:
        text=recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Audio is not proper to text extraction"
    except sr.RequestError as e:
        return "Error with speech recognition"



def summarize_text(text,language='en',max_length=50,min_length=150,length_penalty=2.0):
    tokenizer=en_tokenizer if language=='en' else ar_tokenizer
    model=en_model if language=='en' else ar_model 
    
    inputs=tokenizer.encode(text,return_tensors='pt',max_length=1024,truncation=True)
    summary_ids=model.generate(inputs,max_length=max_length,min_length=min_length,length_penalty=length_penalty,num_beams=4)
    summary=tokenizer.decode(summary_ids[0],skip_special_tokens=True)

    return summary

@app.route('/YouTubeSummarizer',methods=['POST'])
def generate_summary():
    data=request.json
    url=data.get('yt_url')
    
    if isinstance(url,list):
        if len(url)>0:
            url=url[0]
        else:
            return jsonify({"URL Error": "URL List is empty"}),400
    elif not isinstance(url,str):
        return jsonify({"Incorrect URL Format Error":{"Provide a valid url to process the output"}})
    
    if 'v=' not in url:
        return jsonify({"Error":"Invalid url error"})
    language=data.get('language','en').lower()
    summary_type=data.get('typeofsummary','short').lower()

    if language not in ['ar','en']:
        return jsonify({"Error in Language":"Invalid language specified. Use 'en' or 'ar' for getting the summary "}),400
    if summary_type not in ['detailed','short']:
        return jsonify({"Error in Summary type":"Invalid summary type specified. Use 'detailed' or 'short' for getting the summary "}),400
    
    try:
        video_id=url.split('v=')[-1].split('&')[0]
    except Exception as e:
        return jsonify({"Error":"Failed to extract video id from the url"}),400
    
    transcript=get_video_transcript(video_id,'ar' if language=='ar' else 'en')
    if transcript:
        formatted_transcript=format_transcript(transcript)
        transcript_text=clean_srt(formatted_transcript)
    else:
        download_audio(url)
        transcript_text=convert_audio_to_text('audio.mp4')
        if "Error" in transcript_text:
            return jsonify({"Transcript Error":"Transcripts are not available to this video"}),400
   
   
    if summary_type=='short':
        max_length=150
        min_length=50
        length_penalty=2.0
    else:
        max_length=500
        min_length=150
        length_penalty=1.0
    
    summary_text=summarize_text(transcript_text,language,max_length,min_length,length_penalty)
    
    return jsonify({"Summary": summary_text})


if __name__=='__main__':
    app.run(debug=True)