import logging
import json
from youtube_transcript_api import YouTubeTranscriptApi
from gensim.summarization.summarizer import summarize
import os, io
import re
import requests
from flask import *

app = Flask(__name__)

@app.route('/', method=['GET'])
def main() -> Response:
    logging.info('Python HTTP trigger function processed a request.')

    video_id = request.args.get('video_id')
    if not video_id:
        try:
            req_body = request.get_json()
        except ValueError:
            pass
        else:
            video_id = req_body.get('video_id')

    if video_id:
        try:
            transcripts = YouTubeTranscriptApi.get_transcript(video_id)
            textTranscripts = ""
            for t in transcripts: 
                text = re.sub("[\(\[].*?[\)\]]", " ", t['text']).replace("-", "")
                text = " ".join(text.splitlines())
                text = re.sub('\s{2,}', ' ', text).strip()

                if len(text.strip()) > 3 and len(text.strip().split(" ")) > 1:
                    print(text)
                    textTranscripts += text + " "

            punctuatedTranscripts = punctuate_online(textTranscripts)
            summary = summarize(punctuatedTranscripts, ratio=0.5, split=True, word_count=300)
            summary = " ".join(summary)
            results = {
                "transcripts": transcripts,
                "summary": summary
            }
            res = Response(json.dumps(results), status_code=200, mimetype="application/json")
            res.headers["Access-Control-Allow-Origin"] = "*"
            res.headers["Access-Control-Allow-Credentials"] =  "true"
            res.headers["Access-Control-Allow-Headers"] = "Origin, Accept, X-Requested-With, Content-Type, "\
                + "Access-Control-Request-Method, Access-Control-Request-Headers, Authorization"
            return res
        except Exception:
            res = Response("No subtitles", status_code=201)
            res.headers["Access-Control-Allow-Origin"] = "*"
            res.headers["Access-Control-Allow-Credentials"] =  "true"
            res.headers["Access-Control-Allow-Headers"] = "Origin, Accept, X-Requested-With, Content-Type, "\
                + "Access-Control-Request-Method, Access-Control-Request-Headers, Authorization"
            return res
        
    else:
        res = Response(
             "This HTTP triggered function executed successfully. Pass a video_id in the query string or in the request body for a personalized response.",
             status_code=201
        )

        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Credentials"] =  "true"
        res.headers["Access-Control-Allow-Headers"] = "Origin, Accept, X-Requested-With, Content-Type, "\
                + "Access-Control-Request-Method, Access-Control-Request-Headers, Authorization"
        return res

def punctuate_online(text):
    # defining the api-endpoint  
    API_ENDPOINT = "http://bark.phon.ioc.ee/punctuator"
    # data to be sent to api 
    data = dict(text=text)
    # sending post request and saving response as response object 
    r = requests.post(url = API_ENDPOINT, data = data) 

    # extracting response text  
    punctuatedText = r.text
    return punctuatedText