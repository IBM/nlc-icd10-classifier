# Tips about this code pattern

#### Using the cURL command to create the classifier model

Instead of using Watson Studio, the NLC model can be created by calling the API directly. See the steps below on how to do this:

1. Export the username and password as environment variables and then load the data using the command below. If you have an API key, use `apikey` for the username and the API key for the password. This will take around 4.5 hours.

   ```bash
   export USERNAME=<username_from_credentials>
   export PASSWORD=<pasword_from_credentials>
   export FILE=data/ICD-10-GT-AA.csv

   curl -i --user "$USERNAME":"$PASSWORD" -F training_data=@$FILE -F training_metadata="{\"language\":\"en\",\"name\":\"ICD-10Classifier\"}" "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers"
   ```

2. After running the command to create the classifier, note the `classifier_id` in the json that is returned:

   ```JSON
   {
       "classifier_id" : "ab2aa6x341-nlc-1176",
       "name" : "ICD-10Classifier",
       "language" : "en",
       "created" : "2018-04-18T14:09:28.403Z",
       "url" : "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/ab2aa6x341-nlc-1176",
       "status" : "Training",
       "status_description" : "The classifier instance is in its training phase, not yet ready to accept classify requests"
   }
   ```

3. Export the classifier ID as an environment variable:

   ```bash
   export CLASSIFIER_ID=<my_classifier_id>
   ```

4. Now you can check the status for training your classifier:

   ```bash
   curl --user "$USERNAME":"$PASSWORD" "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/$CLASSIFIER_ID"
   ```
