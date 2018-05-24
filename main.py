from flask import Flask, request, jsonify
from werkzeug.contrib.fixers import ProxyFix
import speech_recognition as sr
import datetime
import requests
from search_algo import search_algo


app = Flask(__name__, static_url_path='/static')
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/api/speech_text',methods=['POST'])
def speech_text():
    IBM_USERNAME = '7572e178-a205-4ec1-bdb9-4023851065e2'   #7572e178-a205-4ec1-bdb9-4023851065e2 (NEW)     #68de1d92-305b-414b-a70f-ffa23f797c3e
    IBM_PASSWORD = 'ADUiTI8WfbGR'                           #ADUiTI8WfbGR                                   #73rNCowi21bv
    LANGUAGE = 'fr-FR'  #fr-FR ,en-US
    recognizer = sr.Recognizer()
    code = 200
    payload = ''

    try:
        file_storage = request.files['blob_stream']
        file_storage.save('blob.wav')
        with sr.WavFile('blob.wav') as source:
            audio = recognizer.record(source)
            speech_2_text = recognizer.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD, language=LANGUAGE)
            payload = speech_2_text
            #log
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("\r")
            print("[TRANSLATION]" + timestamp + " || SUCCESS ||" + "Translation Result:" + speech_2_text)
            print("\r")

    except Exception as ex:
            #log
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("\r")
            print("[TRANSLATION]" + timestamp + " || FAILED ||" + "Failed Reason:")
            print(ex)
            print("\r")
            code = 400

    feedback = {}
    feedback['code'] = code
    feedback['data'] = payload

    return jsonify(feedback)


@app.route('/api/search',methods=['POST'])
def search():
    payload = request.get_json(force=True)
    search_input = payload['search_input']
    # analyze to key words
    subscription_key = "b14971ee161d4a1496807d54936874ca"
    assert subscription_key
    text_analytics_base_url = "https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/"
    key_phrase_api_url = text_analytics_base_url + "keyPhrases"
    documents = {'documents' : [{'id': '1', 'language': 'fr', 'text': search_input}]}
    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(key_phrase_api_url, headers=headers, json=documents)
    key_phrases_row = response.json()
    key_words_arr = key_phrases_row['documents'][0]['keyPhrases']

    news_arr = search_algo(key_words_arr)

    feedback = {}
    feedback['data'] = news_arr
    return jsonify(feedback)






if __name__ == '__main__':
  app.run()
