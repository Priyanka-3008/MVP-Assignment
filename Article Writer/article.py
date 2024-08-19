import os
from PyPDF2 import PdfReader
from langdetect import detect
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, MarianMTModel, MarianTokenizer
from googletrans import Translator
from flask import Flask, request, jsonify
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)

# English summarization setup
en_tokenizer = AutoTokenizer.from_pretrained("t5-small")
en_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
en_summarizer = pipeline("summarization", model=en_model, tokenizer=en_tokenizer)

# Arabic translation setup
ar_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-ar")
ar_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-ar")
ar_translator = pipeline('translation_en_to_ar', model=ar_model, tokenizer=ar_tokenizer)

def split_text(text, max_length):
    sentences = text.split('.')
    current_chunk = ""
    chunks = []
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + '.'
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '.'
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def detect_language(text):
    return detect(text)

def summarize_text(text, summarizer):
    chunks = split_text(text, 500)  # Ensure chunks don't split sentences awkwardly
    summaries = []
    for chunk in chunks:
        result = summarizer(chunk)
        if result and 'summary_text' in result[0]:
            summaries.append(result[0]['summary_text'])
        else:
            summaries.append("No summary available")
    full_summary = ' '.join(summaries)
    return full_summary

def translate_text(text, src, dest):
    translator = Translator()
    try:
        translation = translator.translate(text, src=src, dest=dest)
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def generate_article(text, topic, target_language):
    detected_topic_language = detect_language(topic)
    detected_text_language = detect_language(text)

    # Translate topic to target language if needed
    if detected_topic_language != target_language:
        topic = translate_text(topic, src=detected_topic_language, dest=target_language)
        if topic is None:
            return "Error in translating topic"

    text_with_topic = f'Topic: {topic}, {text}'

    if target_language.lower() == 'ar':
        # Summarize in English and then translate
        summary_text_en = summarize_text(text_with_topic, en_summarizer)  # Summarize in English
        summary_text = translate_text(summary_text_en, src='en', dest='ar')  # Translate to Arabic
    else:
        summary_text = summarize_text(text_with_topic, en_summarizer)  # Summarize in English directly

    if summary_text and len(summary_text.strip()) > 0:
        return summary_text
    else:
        return "Error: Unable to generate a coherent article."



   

@app.route('/generate_article', methods=['POST'])
def generate_article_endpoint():
    topic = request.form.get('topic')
    target_language = request.form.get('language')
    pdf_file = request.files.get('document')

    if not target_language:
        return jsonify({"Error": "No Language is provided"}), 400
    if not topic:
        return jsonify({"Error": "No topic is provided"}), 400
    if not pdf_file:
        return jsonify({"Error": "No document is provided"}), 400
    if pdf_file.filename == '':
        return jsonify({"Error": "No file is selected"}), 400

    save_directory = "/Users/mvp/Desktop/taskflask/Articlewriter/Saved Docs"
    os.makedirs(save_directory, exist_ok=True)  # This will create the directory if it does not exist
    save_path = os.path.join(save_directory, pdf_file.filename)
    pdf_file.save(save_path)

    document_text = extract_text_from_pdf(save_path)
    if not document_text.strip():
        return jsonify({"Error": "No text extracted from the document"}), 400

    article = generate_article(document_text, topic, target_language)
    return jsonify({"Article": article if article else "Article generation failed"})

if __name__ == "__main__":
    app.run(debug=True)
