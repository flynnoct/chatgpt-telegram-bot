import openai

def list_assistants(openai_api_key):
    openai.api_key = openai_api_key
    assistants = openai.beta.assistants.list()
    for assistant in assistants.data:
        print(assistant.id, assistant.name)

def delete_all_assistants(openai_api_key):
    openai.api_key = openai_api_key
    assistants = openai.beta.assistants.list()
    for assistant in assistants.data:
        openai.beta.assistants.delete(assistant.id)

def list_threads(openai_api_key):
    openai.api_key = openai_api_key
    thread = openai.beta.threads.retrieve("thread_MAqvtUZMW53Mq31CzvkljbHy")
    print(thread)

if __name__ == "__main__":
    key = input("OpenAI API Key: ")
    # list_threads(key)
    # delete_all_assistants(key)
    list_assistants(key)