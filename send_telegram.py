# -*- coding: UTF-8 -*-

import os
import re
import urllib.request
import json
import time


def parse_telegram_messages_id(issue_body:str):
    links = list(
        map(
            # trim symbols '<>' from links
            lambda link: re.sub('<|>', '', link),
            # find all links in <...>
            re.findall(r'<https://t.me/[a-zA-Z0-9/_]+>', issue_body)
        )
    )

    return list(
        map(
            lambda link: link[link.rfind('/')+1:],
            links
        )
    )


def telegram_send_message(
    chat_id:str,
    token:str,
    text:str,
    reply_to_message_id:int,
    allow_sending_without_reply:bool,
    parse_mode:str
    ):
    
    try:
        if parse_mode == "MarkdownV2":
            text = text.replace('-', '\\-')
            text = text.replace('+', '\\+')
            text = re.sub(r'\[(.*)\((.*)\)(.*)\]\((.*)\)', r'[\1\(\2\)\3](\4)', text)
        
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json.dumps(
                {
                    "chat_id": chat_id,
                    "text": text,
                    "reply_to_message_id": reply_to_message_id,
                    "allow_sending_without_reply": allow_sending_without_reply,
                    "parse_mode": parse_mode,
                }
            ).encode("utf-8"),
            {
                "Content-Type": "application/json"
            }
        )
        print(f"-> Request details (Message ID {reply_to_message_id}):")
        print(f"● URL (full): {request.get_full_url()}")
        print(f"● Method: {request.get_method()}")
        print(f"● Headers: {request.header_items()}")
        print(f"● Data: {request.data}")
        
        with urllib.request.urlopen(request) as f:
            response = f.read()
            print(f"● Status: {f.status}")
        return response
    except Exception as e:
        print(e)



messages_id = parse_telegram_messages_id(os.getenv('GITHUB_ISSUE_BODY'))
print("-> Parsed Messages ID's to reply:")
print(*messages_id, sep='\n')
print()

for id in messages_id:
    response = telegram_send_message(
        chat_id = os.getenv('TELEGRAM_CHAT_ID'),
        token = os.getenv('TELEGRAM_BOT_TOKEN'),
        text = os.getenv('TELEGRAM_MESSAGE_TEMPLATE'),
        reply_to_message_id = id,
        allow_sending_without_reply = os.getenv('TELEGRAM_ALLOW_SENDING_WITHOUT_REPLY'),
        parse_mode = os.getenv('TELEGRAM_PARSE_MODE'),
    )
    print("-> Response:")
    print(response.decode('utf-8'))
    print()
    time.sleep(1)
