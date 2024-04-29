## Sleep Information Chatbot showcase
This project is a chatbot designed to provide valuable information about sleep, based on the knowledge from Huberman Lab podcasts. 
The chatbot is accessible via Telegram [link](https://t.me/SleepHbrChat_bot).

## Functionality

The core functionality of the chatbot is implemented using a `query_engine`:

```python
query_engine = loaded_index.as_query_engine(streaming=False, text_qa_template=text_qa_template,)
```

The `query_engine` is a key component of our chatbot. It is responsible for processing user queries and generating appropriate responses. The specifics of how this is achieved are part of our proprietary business logic.

When a user sends a message to the chatbot, the `query_engine` processes the user's message and generates a response. The response is then sent back to the user via Telegram.

## Acknowledgements

We would like to thank the [LlamaIndexCourse](https://github.com/jbergant/LlamaIndexCourse) repository for providing the initial data to create the index based on the Huberman Lab sleep podcasts.

## Potential Clients

If you are a potential client looking at this project, we would love to hear from you. We are always open to new opportunities and collaborations. Please feel free to reach out to us on UpWork.

