import time
import sys
import json
from slackclient import SlackClient
from slacker import Slacker

class SimpleSlack():
    
    def __init__(self, token):
        # RESTful API 
        self.slack_REST = Slacker(token)

        # Real time API
        self.slack_real_time = SlackClient(token)

        self.user_name_map = {}
        self.channel_name_map = {}
        self.update_name_maps()

    def read_channel(self, channel):
        """
        Reads a slack channel from the real time API
        and prints its formatted output to stdout
        """
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if self.slack_real_time.rtm_connect():
            while True:
                events = self.slack_real_time.rtm_read()
                for ev in events:
                    if 'channel' not in ev:
                        continue 
                    if self.channel_name_map[ev['channel']] != channel:
                        continue
                    if 'text' not in ev:
                        continue
                    self.format_message(ev['channel'], ev['user'], ev['text'])
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print "Failed to connect"

    def format_message(self, channel_id, user_id, text):
        """
        Formats and prints a message
        """
        user = self.user_name_map[user_id]
        channel = self.channel_name_map[channel_id]
        print '(' + channel + ') ' + user + ": "+text 

    def update_name_maps(self):
        """
        Updates the user and channel name maps
        """
        response = self.slack_REST.users.list()
        users = response.body['members']
        for user in users:
            self.user_name_map[user['id']] = user['name']

        response = self.slack_REST.channels.list()
        channels = response.body['channels']
        for channel in channels:
            self.channel_name_map[channel['id']] = channel['name']
        

def main():
    with open('conf.json') as f:    
        conf = json.loads(f.read())
        channel = sys.argv[1]
        simpleslack = SimpleSlack(conf['SLACK_API_TOKEN'])
        simpleslack.read_channel(channel)

if __name__ == "__main__":
    main()
