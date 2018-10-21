import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slackclient import SlackClient
from watson_developer_cloud import ConversationV1
import requests
from bs4 import BeautifulSoup

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)
watson_username = getattr(settings, 'WATSON_USERNAME', None)
watson_password = getattr(settings, 'WATSON_PASSWORD', None)

conversation = ConversationV1(
    username=watson_username,
    password=watson_password,
    version='2017-04-21')

workspace_id = getattr(settings, 'WATSON_WORKSPACE_ID', None)


class Events(APIView):
    def post(self, request, *args, **kwargs):

        slack_message = request.data
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # verification challenge
        if slack_message.get('type') == 'url_verification':  #
            return Response(data=slack_message,  #
                            status=status.HTTP_200_OK)  #

        # responsing only if event present
        if 'event' in slack_message:
            event_message = slack_message.get('event')

            print event_message
            # ignore bot's own message
            if event_message.get('subtype') == 'bot_message':
                print "returning from here"
                return Response(status=status.HTTP_200_OK)
            else:
                user = event_message.get('user')
                text = event_message.get('text')
                response = conversation.message(workspace_id=workspace_id, message_input={
                    'text': text})
                # print(json.dumps(response, indent=2))
                watson_response = response['output']
                message_intent = response['intents']
                # print message_intent[0].get('intent')
                channel = event_message.get('channel')
                # reply to users message
                bot_text = ''
                if len(message_intent) == 0:
                    bot_text = ('<@{}>  ' + str(watson_response.get('text')[0])).format(user)
                else:
                    if (message_intent[0].get('intent') == 'hello') or (message_intent[0].get('intent') == 'bye'):
                        bot_text = ('<@{}>  ' + str(watson_response.get('text')[0])).format(user)
                    else:
                        bot_text = scrape_page(link=watson_response.get('text')[0])
                        bot_text = ('<@{}>  ' + bot_text).format(user)
                print bot_text
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text=bot_text)
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)


def scrape_page(link):
    print link
    headers = {"user-agent": "Mozilla/5.0", }
    solution = ''
    resp = requests.get(link, headers=headers)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
        ans = soup.find_all('div', {"class": "lia-component-solution-list"})
        ans = ans[0].find_all('div', {"class": "lia-message-body-content"})
        ans = ans[0].find_all('p')

        for sol in ans:
            solution = solution + sol.text + "\n"
    if solution != '':
        solution = solution + "\nFor more details visit:\n " + link
    else:
        solution = "Please visit:\n " + link
    return solution
