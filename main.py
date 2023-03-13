import json
import openchat
import speech


def main():
    # read config file
    global user_input
    with open('./config.json', 'r') as f:
        config = json.load(f)
        api_keys = config['openai_api_keys']
        speech_key = config['speechKey']
        speech_region = config['speechRegion']
        link_str = config['mongodb_link_str']

    system_prompt = input("please input prompt: ")
    openai_chat = openchat.Dialog(system_prompt, api_keys, mongodb_link=link_str, current_session=None,
                                  max_tokens=10000)
    azure_speech = speech.AzureSpeech(speech_key, speech_region)
    while True:
        result = azure_speech.recognize_from_microphone()
        if result['success']:
        response = openai_chat.askChatGPT(user_input)
        if response['type'] == 'normal':
            print("Bot: {}".format(response['message']['content']))
            azure_speech.text_to_speech(response['message']['content'])
        elif response['type'] == 'error':
            print("Error: {}".format(response))
            return


if __name__ == "__main__":
    main()
