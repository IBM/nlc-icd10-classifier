# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, request
from watson_developer_cloud import NaturalLanguageClassifierV1

app = Flask(__name__)

# The data set we want to use
DATA_SET = 'data/ICD-10-GT-AA.csv'

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

nlc_username = os.environ.get("NATURAL_LANGUAGE_CLASSIFIER_USERNAME")
nlc_password = os.environ.get("NATURAL_LANGUAGE_CLASSIFIER_PASSWORD")

NLC_SERVICE = NaturalLanguageClassifierV1(
    username=nlc_username,
    password=nlc_password
)
CLASSIFIER = None


@app.route('/')
def Welcome():
    global CLASSIFIER
    # create classifier if it doesn't exist, format the json
    CLASSIFIER = _create_classifier()
    classifier_info = json.dumps(CLASSIFIER, indent=4)
    # update the UI, but only the classifier info box
    return render_template(
        'index.html',
        classifier_info=classifier_info,
        icd_code="",
        icd_output="",
        classifier_output="")


@app.route('/classifyhandler', methods=['GET', 'POST'])
def classify_text():
    # get the text from the UI
    inputtext = request.form['classifierinput']
    # get info about the classifier
    classifier_info = json.dumps(CLASSIFIER, indent=4)
    # send the text to the classifier, get back an ICD code
    classifier_output = NLC_SERVICE.classify(
        CLASSIFIER['classifier_id'], inputtext)
    # get the ICD name based on ICD code
    icd_code, icd_output = _get_ICD_code_info(classifier_output)
    # format results
    classifier_output = json.dumps(classifier_output, indent=4)
    icd_output = json.dumps(icd_output, indent=4)
    # fill in the text boxes
    return render_template(
        'index.html',
        classifier_info=classifier_info,
        icd_code=icd_code,
        icd_output=icd_output,
        classifier_output=classifier_output)


def _create_classifier():
    # fetch all classifiers associated with the NLC instance
    result = NLC_SERVICE.list_classifiers()
    # for the purposes of this demo, we handle only one classifier
    # return the first one found
    if len(result['classifiers']) > 0:
        return result['classifiers'][0]
    else:
        # if none found, create a new classifier, change this value
        with open(DATA_SET, 'rb') as training_data:
            metadata = '{"name": "ICD_classifier", "language": "en"}'
            classifier = NLC_SERVICE.create_classifier(
                metadata=metadata,
                training_data=training_data
            )
        return classifier


def _get_ICD_code_info(result):
    # handy third-party service to convert the ICD code
    # to a name and description
    base_url = "http://www.icd10api.com/?"
    code = result["top_class"]
    query_string = "s=" + code + "&desc=short&r=json"
    resp = requests.get(base_url + query_string)
    return code, resp.json()


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
