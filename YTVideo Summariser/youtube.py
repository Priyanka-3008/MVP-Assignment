from pytube import YouTube
import re
from transformers import pipeline
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from flask import Flask,request,jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter


app= Flask(__name__)


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

en_tokenizer=AutoTokenizer.from_pretrained("facebook/bart-large-cnn",legacy=False)
en_model=AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")


ar_tokenizer=AutoTokenizer.from_pretrained("malmarjeh/t5-arabic-text-summarization",legacy=False)
ar_model=AutoModelForSeq2SeqLM.from_pretrained("malmarjeh/t5-arabic-text-summarization")

def summarize_text(text,language='en'):
    tokenizer=en_tokenizer if language=='en' else ar_tokenizer
    model=en_model if language=='en' else ar_model 
    
    inputs=tokenizer.encode(text,return_tensors='pt',max_length=1024,truncation=True)
    summary_ids=model.generate(inputs,max_length=150,min_length=50,length_penalty=2.0,num_beams=4)
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
    if "Transcript not available" in transcript:
        return jsonify({"Transcript Error":"Transcripts are not available to this video"}),400
    formatted_transcript=format_transcript(transcript)
    transcript_text=clean_srt(formatted_transcript)
    max_length=150 if summary_type=='short' else 500
    summary_text=summarize_text(transcript_text,language)
    
    return jsonify({"Summary": summary_text})


if __name__=='__main__':
    app.run(debug=True)