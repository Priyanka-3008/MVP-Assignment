from flask import Flask, request,jsonify
import joblib
import string
import re
import sklearn as sk
from sklearn import * 
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def preprocess_text(text):
    def remove_url(text):
        url_pattern=re.compile(r'https?://\S+|www\.\S+|\.\w+', flags=re.IGNORECASE)
        return url_pattern.sub(r'',text)

    def striphtml(text):
        p=re.compile(r'<.*?>|\.')
        return p.sub('',text)
    
    def remove_punctuation(text):
        punctuation_free = "".join([i for i in text if i not in string.punctuation])
        return punctuation_free
    def remove_digits(text):
        result = ''.join([i for i in text if not i.isdigit()])
        return result
    def token_wordremoval(text):
        stop_words=set(stopwords.words('english'))
        word_tokens=word_tokenize(text)
        filtered_text=[word for word in word_tokens if word not in stop_words]
        return filtered_text
    def lemmatize_text(tokens):
        WNL = WordNetLemmatizer()
        return [WNL.lemmatize(word) for word in tokens]
    text=remove_url(text)
    text=striphtml(text)
    text=remove_punctuation(text)
    text=remove_digits(text)
    tokens=token_wordremoval(text)
    lemmatized_tokens=lemmatize_text(tokens)
    return ' '.join(lemmatized_tokens)

app=Flask(__name__)


model=joblib.load('/Users/mvp/Desktop/taskflask/news_classifier (3).pkl')
vectoriser=joblib.load('/Users/mvp/Desktop/taskflask/tfidf_vectorizer.pkl')
@app.route('/predict',methods=['POST'])
def predict():
    data=request.json.get('text')
    if not data:
        return jsonify({'Error':'No text provided'}),400
    processed_text=preprocess_text(data)
    vectorised_text=vectoriser.transform([processed_text])
    prediction=model.predict(vectorised_text)
    return jsonify({'Category':prediction[0]})



if __name__=='__main__':
    app.run(debug=True)
    