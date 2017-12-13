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

from flask import Flask, jsonify, render_template, request
from watson_developer_cloud import NaturalLanguageClassifierV1

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.getenv('VCAP_SERVICES'))
    NLC_USERNAME = VCAP_SERVICES['natural_language_classifier'][0]['credentials']['username']
    NLC_PASSWORD = VCAP_SERVICES['natural_language_classifier'][0]['credentials']['username']
else:
    # Set these here for local development
    NLC_USERNAME = "fe430574-8a84-42c4-9748-bbd03c5368de"
    NLC_PASSWORD = "741DcPDcweIJ"

NLC_SERVICE = NaturalLanguageClassifierV1(
    username=NLC_USERNAME,
    password=NLC_PASSWORD
)
CLASSIFIER = None

@app.route('/')
def Welcome():
    global CLASSIFIER
    CLASSIFIER = _create_classifier()
    classifier_info = json.dumps(CLASSIFIER, indent=4)
    return render_template('index.html', classifier_info=classifier_info, classifier_output="")


@app.route('/classifyhandler', methods=['GET', 'POST'])
def classify_text():
    # send the text to the classifier and report back results
    inputtext = request.form['classifierinput']
    classifier_output = NLC_SERVICE.classify(CLASSIFIER['classifier_id'], inputtext)
    classifier_info = json.dumps(CLASSIFIER, indent=4)
    code, ret_text = _get_ICD_code_info(classifier_output)
    ret_text = json.dumps(ret_text, indent=4)
    classifier_output = json.dumps(classifier_output, indent=4)
    #return render_template('index.html', classifier_info=classifier_info, classifier_output=classifier_output)
    return render_template('index.html', classifier_info=classifier_info, code=code, ret_text=ret_text, classifier_output=classifier_output)


def _create_classifier():
    result = NLC_SERVICE.list_classifiers()
    if len(result['classifiers']) > 0:
        # for the purposes of this demo, we handle only one classifier
        return result['classifiers'][0]
    else:
        with open('data/ICD-10-GT-AA.csv', 'rb') as training_data:
            metadata = '{"name": "ICD_classifier", "language": "en"}'
            classifier = NLC_SERVICE.create_classifier(
                metadata=metadata,
                training_data=training_data
            )
        return classifier

def _get_ICD_code_info(result):
    base_url = "http://www.icd10api.com/?"
    code = result["top_class"]
    query_string = "s=" + code + "&desc=short&r=json"
    r = requests.get(base_url + query_string)
    return code, r.text

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
