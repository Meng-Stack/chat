import datetime
import random
import openai
import mongodbclass


class Message:
    def __init__(self, system_prompt, current_session, mongodb_link):
        self.current_session = current_session
        self.system_prompt = system_prompt
        self.mongodb_db = mongodbclass.MongoDBLink(link_str=mongodb_link)
        self.last_message = None
        self.messages = []
        self.No = 0

    def load_messages(self):
        chat_records = self.mongodb_db.get_messages(self.current_session)
        if chat_records:
            self.No = sorted(chat_records, key=lambda x: x['No'], reverse=True)[0]['No']
            for chat_record in chat_records:
                message = chat_record['message']
                self.messages.append({'role': message['role'], 'content': message['content']})
        else:
            self.messages.append({'role': 'system', 'content': self.system_prompt})
            self.mongodb_db.insert(
                {'key_id': self.current_session, 'No': self.No, 'created': int(datetime.datetime.now().timestamp()),
                 'message': {'role': 'system', 'content': self.system_prompt}})
        self.No += 1

    def dialog_length(self):
        system_message = 0
        user_message = 0
        assistant_message = 0
        for message in self.messages:
            if message['role'] == 'system':
                system_message += 1
            if message['role'] == 'user':
                user_message += 1
            if message['role'] == 'assistant':
                assistant_message += 1
        if user_message == assistant_message:
            return user_message + system_message
        else:
            return assistant_message + system_message

    def addAsk(self, message):
        self.messages.append({'role': 'user', 'content': message})
        self.mongodb_db.insert(
            {'key_id': self.current_session, 'No': self.No, 'created': int(datetime.datetime.now().timestamp()),
             'message': {'role': 'user', 'content': message}})
        self.No += 1
        return self.messages

    def addResponse(self, resp):
        if resp['type'] == 'error':
            return resp
        resp['key_id'] = self.current_session
        resp['No'] = self.No
        self.mongodb_db.insert(resp)
        self.messages.append(resp['message'])
        self.No += 1
        return resp


class OpenAI:
    def __init__(self, api_key, model="gpt-3.5-turbo", max_tokens=1000):
        openai.api_key = api_key
        self.current_cost = 0
        self.model = model
        self.max_tokens = max_tokens
        self.dialog_id = 0

    def askChatGPT(self, messages):
        if self.current_cost > self.max_tokens:
            return {'type': 'error', 'message': 'OpenAI API cost limit reached.'}
        else:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0)
            choice = response.choices[0]
            resp = {'type': 'normal', 'openai_id': response.openai_id, 'created': response.created,
                    'model': response.model,
                    'response_ms': response.response_ms, 'prompt_tokens': response.usage['prompt_tokens'],
                    'completion_tokens': response.usage['completion_tokens'],
                    'total_tokens': response.usage['total_tokens'],
                    'message': {'role': choice['message']['role'], 'content': choice['message']['content']}}
            self.current_cost += resp['total_tokens']
            return resp


class Dialog:
    def __init__(self, system_prompt, api_keys, model="gpt-3.5-turbo", max_tokens=1000, mongodb_link=None,
                 current_session=None):

        self.openai_api = [OpenAI(api_key=api_key, model=model, max_tokens=max_tokens) for api_key in api_keys]
        if current_session is None:
            self.current_session = datetime.datetime.now().strftime("%Y%m%d") + str(random.randint(0, 999999999)).zfill(
                9)
        else:
            self.current_session = current_session
        self.message = Message(system_prompt=system_prompt, current_session=self.current_session,
                               mongodb_link=mongodb_link)
        self.message.load_messages()

    def askChatGPT(self, message):
        current_message = self.message.addAsk(message)
        if self.message.dialog_length() % 2 == 0:
            return self.message.addResponse(self.openai_api[0].askChatGPT(current_message))
        else:
            return self.message.addResponse(self.openai_api[1].askChatGPT(current_message))
