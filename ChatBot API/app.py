from flask import Flask,request,jsonify
from transformers import pipeline,AutoModelForCausalLM,AutoTokenizer,AutoModelForSeq2SeqLM

app=Flask(__name__)



english_model_name="facebook/blenderbot-400M-distill"
english_tokenizer=AutoTokenizer.from_pretrained(english_model_name,trust_remote_code=True)
english_model=AutoModelForSeq2SeqLM.from_pretrained(english_model_name,trust_remote_code=True)
english_pipeline=pipeline("text2text-generation",model=english_model_name)

arabic_model = AutoModelForCausalLM.from_pretrained("aubmindlab/aragpt2-large", trust_remote_code=True)
arabic_tokenizer=AutoTokenizer.from_pretrained("aubmindlab/aragpt2-large",trust_remote_code=True)
@app.route('/chat',methods=['POST'])
def chat():
    user_query=request.json.get('query','')
    if not user_query:
        return jsonify({"Error":"No query is provided"})
    
    if is_arabic(user_query):
        input_ids=arabic_tokenizer.encode(user_query,return_tensors='pt')
        response=arabic_model.generate(input_ids,max_length=100,num_return_sequences=1,pad_token_id=arabic_tokenizer.eos_token_id)
        answer=arabic_tokenizer.decode(response[0],skip_special_tokens=True)
    
    else:
        response=english_pipeline(user_query,max_length=100)
        answer=response[0]['generated_text']
    return jsonify({"Answer":answer.strip()})

def is_arabic(text):
    return any('\u0600'<=c<='\u06FF' for c in text)


if __name__=='__main__':
    app.run(debug=True)