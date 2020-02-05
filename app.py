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

from ibm_watson import NaturalLanguageClassifierV1

DEBUG = True
app = Flask(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
classifier_id = os.environ.get("CLASSIFIER_ID")

NLC_SERVICE = NaturalLanguageClassifierV1()


@app.route('/')
def default():
    classifier_info = "cannot detect classifier"
    if NLC_SERVICE:
        classifier_info = ("classifier detected, using API: " +
                           NLC_SERVICE.service_url)
    return render_template(
        'index.html',
        classifier_info=classifier_info,
        icd_code="",
        icd_output="",
        classifier_output="")


@app.route('/classifyhandler', methods=['GET', 'POST'])
def classify_text():
    inputtext = request.form['classifierinput']

    try:
        classifier_info = NLC_SERVICE.get_classifier(classifier_id)
        classifier_output = NLC_SERVICE.classify(classifier_id,
                                                 inputtext).get_result()
        icd_code, icd_output = _get_ICD_code_info(classifier_output)
        classifier_output = json.dumps(classifier_output, indent=4)
        icd_output = json.dumps(icd_output, indent=4)
    except Exception:
        classifier_info = ("error from classifier service, "
                           "check if credentials are set")
        classifier_output = ""
        icd_code = ""
        icd_output = ""

    return render_template(
        'index.html',
        classifier_info=classifier_info,
        icd_code=icd_code,
        icd_output=icd_output,
        classifier_output=classifier_output)


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
