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

from flask import Flask, jsonify, render_template, request
from watson_developer_cloud import NaturalLanguageClassifierV1

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.getenv('VCAP_SERVICES'))
    NLC_USERNAME = VCAP_SERVICES['natural_language_classifier'][0]['credentials']['username']
    NLC_PASSWORD = VCAP_SERVICES['natural_language_classifier'][0]['credentials']['username']
else:
    # Set these here for local development
    NLC_USERNAME = ""
    NLC_PASSWORD = ""

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
    classifier_output = json.dumps(classifier_output, indent=4)
    return render_template('index.html', classifier_info=classifier_info, classifier_output=classifier_output)


def _create_classifier():
    result = NLC_SERVICE.list_classifiers()
    if len(result['classifiers']) > 0:
        # for the purposes of this demo, we handle only one classifier
        return result['classifiers'][0]
    else:
        with open('weather_data_train.csv', 'rb') as training_data:
            metadata = '{"name": "My Classifier", "language": "en"}'
            classifier = NLC_SERVICE.create_classifier(
                metadata=metadata,
                training_data=training_data
            )
        return classifier


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
