import socket
import re
import csv
import os
import requests
import json
import random
import Command
from datetime import datetime



class Bot():
    def __init__(self, server, port, token, username, channel):
        self.server = server
        self.port = port
        self.oauth_token = token
        self.username = username
        self.channel = channel
        self.commands = {s.command_name: s for s in (c(self) for c in Command.CommandBase.__subclasses__())}


    def connect_to_channel(self):
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.username}")
        self.irc_command(f"JOIN #{self.channel}")        
        self.send_message(self.channel, "I AM ALIVE!!")
        self.check_for_messages()

    
    # execute IRC commands
    def irc_command(self, command):
        self.irc.send((command + "\r\n").encode())


    # send privmsg's, which are normal chat messages
    def send_message(self, channel, message):
        self.irc_command(f"PRIVMSG #{channel} :{message}")


    # decode incoming messages
    def check_for_messages(self):
        while True:
            messages = self.irc.recv(1024).decode()
            for m in messages.split("\r\n"):
                self.parse_message(m)


    # write message author to csv
    def write_message_data(self, user):
        entry = {
            "time": str(datetime.now()),
            "user": user,
        }
        if os.path.isfile("./data/chat_count.csv"):
            with open("./data/chat_count.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow([v for k,v in entry.items()])
            
        else:
            with open("./data/chat_count.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow(entry.keys())
                writer.writerow([v for k,v in entry.items()])


    # check for command being executed
    def parse_message(self, message):
        try:
            # regex pattern
            pat_message = re.compile(r":(?P<user>.+)!.+#mitchsworkshop :(?P<text>.+)", flags=re.IGNORECASE)
            # pull user and text from each message
            user = re.search(pat_message, message).group("user")
            text = re.search(pat_message, message).group("text")

            self.write_message_data(user)

            # check for commands being used
            if text.startswith("!"):
                command = text.split()[0]
                self.execute_command(user, command)
        except:
            pass

    
    # write command usage data to CSV
    def write_command_data(self, user, command):
        entry = {
            "time": str(datetime.now()),
            "user": user,
            "command": command
        }
        if os.path.isfile("./data/command_data.csv"):
            with open("./data/command_data.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow([v for k,v in entry.items()])
            
        else:
            with open("./data/command_data.csv", "a") as file:
                writer = csv.writer(file)
                writer.writerow(entry.keys())
                writer.writerow([v for k,v in entry.items()])
            
    
    # pull joke from Jokes API
    def get_joke(self, user) -> str:
        url = "https://geek-jokes.sameerkumar.website/api?format=json"
        for _ in range(10):
            result = requests.get(url).json()
            joke = result["joke"]
            if len(joke) <= 500:
                return joke
        return f"Sorry @{user}, I couldn't find a short enough joke. :("


    # pull poem from PoetryDB
    def get_poem(self, user) -> str:
        num_lines = 4
        url = f"https://poetrydb.org/linecount/{num_lines}/lines"
        result = requests.get(url)
        poems = json.loads(result.text)
        num_poems = len(poems)
        for _ in range(5):
            idx = random.randint(0, num_poems)
            lines = poems[idx]["lines"]
            poem = "; ".join(lines)
            if len(poem) <= 500:
                return poem
        return f"I couldn't find a short enough poem. Sorry @{user} :("


    # define and execute each command
    def execute_command(self, user, command):
        if command in self.commands.keys():
            self.commands[command].execute(user)   
            # if command == "!love":
            #     self.send_message(
            #         channel = self.channel, 
            #         message = f"I love you, @{user}"
            #     )

            # if command == "!github":
            #     self.send_message(
            #         channel = self.channel, 
            #         message = "See past on-stream projects on Mitch's GitHub here! https://github.com/MitchellHarrison"
            #     )

            # if command == "!discord":
            #     self.send_message(
            #         channel = self.channel, 
            #         message = "Give or receive help or engage in nerdy debauchery in The Workshop discord server! https://discord.gg/9yFFNpP"
            #     )

            # if command == "!theme":
            #     self.send_message(
            #         channel = self.channel,
            #         message = "Current VSCode theme is Monokai Vibrant!"
            #     )

            # if command == "!specs":
            #     self.send_message(
            #         channel = self.channel,
            #         message = "CPU - i7 9700k; GPU - RTX 2080; RAM - 16GB Trident Z DDR4"
            #     )

            # if command == "!twitter":
            #     self.send_message(
            #         channel = self.channel, 
            #         message = "Twitter is your one-stop-shop for streams of consciousness and Macswell pics!  https://twitter.com/MitchsWorkshop"
            #     )

            # if command == "!dataquest":
            #     self.send_message(
            #         channel = self.channel, 
            #         message = "I use a service called DataQuest to learn data science. Join here! app.dataquest.io/referral-signup/iz2u2cab/"
            #     )

            # if command == "!poem":
            #     self.send_message(
            #         channel = self.channel,
            #         message = self.get_poem(user=user)
            #     )

            # if command == "!joke":
            #     self.send_message(
            #         channel = self.channel,
            #         message = self.get_joke(user=user)
            #     )

            self.write_command_data(user, command)
