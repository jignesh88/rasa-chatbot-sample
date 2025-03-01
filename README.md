## Description

- Chatbot using RASA NLU

## How to run

Install rasa using 

```pip install rasa```

Make sure you are using python 3.10

Run following command to train the rasa model

```rasa train```

Run following commadn to run the model locally

```rasa run  -m models --enable-api --cors "*" ```

Run following command to run actions

```rasa run actions```

Run following command to run main-api.py using flask

```python run main-api.py```

It will run the flask server locally on 8000 port. Use folloing curl command to test the chat application.

```
curl --location 'localhost:8000/chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "I would like to book an appointment?"
}'
```