import json
import os
import argparse
from utils.Agent import Agent
from utils.Function import *

class MultiDabate:
    def __init__(self,
                 model_name='deepseek-chat',
                 temperature=0,
                 config=None,  # path
                 output=None,  # path
                 api_key=None,
                 sleep_time=0,
                 base_url='https://api.deepseek.com'
                 ):
        """Create a SingleDabate

          Args:
              model_name (str): openai model name
              temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
              num_players (int): num of players
              api_key (str): As the parameter name suggests
              sleep_time (float): sleep because of rate limits
              base_url (str): base URL for non-OpenAI models
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.sleep_time = sleep_time
        self.base_url = base_url
        self.output = output

        self.config = config


        self.meta = self.meta_init()
        #
        self.Affirmative, self.Negative, self.Judge = self.multi_agents_debate()

    def meta_init(self):
        ...

    def multi_agents_init(self):
        ...


    def multi_agents_debate(self):
        ...

        return Affirmative, Negative, Judge

    def load_json(self, id):
        ...