from dataclasses import dataclass
import requests
from requests.exceptions import Timeout
import re

class Scout:
  
  def __init__(self, player_name:str, search_type: str):
    
    self.player = player_name.lower()
    urls_dict, type_of_games_dict = self.prepare_url_and_type_dicts()
    if search_type in urls_dict:
      url = urls_dict[search_type]
      type_of_games = type_of_games_dict[search_type]
    else:
      url = urls_dict["rated"]
      type_of_games = type_of_games_dict["rated"]

    self.scouting_report = ScoutingReport(player_name,url, type_of_games)
    

  
  def prepare_url_and_type_dicts(self):
    urls_dict = {}
    type_of_games_dict = {}
    raw_url_data = load_urls_from_file()
    if raw_url_data:
      classical_url = re.search(r'classical_url = (.+)\b', raw_url_data).group(1)
      all_games_url = re.search(r'all_games_url = (.+)\b', raw_url_data).group(1)
      fast_games_url = re.search(r'fast_games_url = (.+)\b', raw_url_data).group(1)
  
      classical_url = re.sub("PLAYERGOESHERE", self.player, classical_url)
      all_games_url = re.sub("PLAYERGOESHERE", self.player, all_games_url)
      fast_games_url = re.sub("PLAYERGOESHERE", self.player, fast_games_url)
  
  
  
      
      classical_words = ['classical',"c", "classic", "long", "slow"]
      all_games_words = ["rated","all"]
      fast_games_words = ['fast', 'rapid', 'blitz', 'quick', 'speed']
      
      self.add_to_url_and_type_dicts(classical_words,classical_url,urls_dict, type_of_games_dict)
      self.add_to_url_and_type_dicts(all_games_words,all_games_url,urls_dict, type_of_games_dict)
      self.add_to_url_and_type_dicts(fast_games_words,fast_games_url,urls_dict, type_of_games_dict)

      return urls_dict, type_of_games_dict



  def add_to_url_and_type_dicts(self,word_list,url, urls_dict, type_of_games_dict):
    for word in word_list:
      urls_dict[word] = url
      type_of_games_dict[word] = word_list[0]
    
  def scout(self):
   
    white_pattern = re.compile(r'\[White "(\w+-*\w*)"')
    result_pattern = re.compile(r'\[Result "(\d(-|/)\d)')
    pgn_pattern = re.compile(r'1\. \w+ \w+ 2\. \w+ \w+')

    data = self.download_data_from_lichess()
    games = self.split_data_into_games(data)
    
    for game in games[1:]:     
      self.set_player_color(game,white_pattern)
      self.set_result(game,result_pattern)
      self.scouting_report.pgn = pgn_pattern.search(game).group()
      game_score = self.scouting_report.make_game_score()
      self.scouting_report.all_games.append(game_score)
      if game_score.color == "White":
        self.scouting_report.white_games.append(game_score)
      else:
        self.scouting_report.black_games.append(game_score)
    

  def download_data_from_lichess(self):
    try:
      response = requests.get(self.scouting_report.url, timeout=2)
      data = response.text
      return data
    except Timeout:
      print("No reponse for that user")
      return None

  def split_data_into_games(self,data):
    games = data.split("[Event")
    return games  

  def set_player_color(self, game, pattern):
    p = pattern.search(game).group(1).lower()
    if p == self.player:
      self.scouting_report.player_color = "White"
    else:
      self.scouting_report.player_color = "Black"

  def set_result(self, game, pattern):
    result = pattern.search(game).group(1)
    if result == "1/2":
      self.scouting_report.result = "Draw"
    elif result == "1-0":
      if self.scouting_report.player_color == "White":
        self.scouting_report.result = "Win"
      else:
        self.scouting_report.result = "Loss"
    elif result == "0-1":
      if self.scouting_report.player_color == "Black":
        self.scouting_report.result = "Win"
      else:
        self.scouting_report.result = "Loss"
      
  

  
@dataclass
class ChessGameScore:
  player: str
  color: str
  pgn: str
  result: str

class ScoutingReport:
  def __init__(self, player_name, url, type_of_game):
    self.player_color: str
    self.player: str = player_name
    self.pgn: str
    self.white_games = []
    self.black_games = []
    self.all_games = []
    self.url = url
    self.type_of_games = type_of_game

  def make_game_score(self):
    score = ChessGameScore(player=self.player, color=self.player_color, pgn=self.pgn,result=self.result)

    return score

  def print_output(self):
   
    white_wins = 0
    white_losses = 0
    black_wins = 0
    black_losses = 0
    
    if self.all_games:
      for game in self.all_games:
        if game.color == "White":
          if game.result == "Win":
            white_wins += 1
          elif game.result == "Loss":
            white_losses += 1
        elif game.color == "Black":
          if game.result == "Win":
            black_wins += 1
          elif game.result == "Loss":
            black_losses += 1
      print(f"\nIn the last {len(self.all_games)} of {self.player}'s {self.type_of_games} games:")
      print(f"{self.player} had {white_wins+black_wins} wins and {white_losses+black_losses} losses\n")
      print(f"as White \n they had {white_wins} wins and {white_losses} losses playing:")
      for game in self.white_games:
        print(f'{game.pgn} for a {game.result}')
      print(f"\nas Black \n they had {black_wins} wins and {black_losses} losses playing:")
      for game in self.black_games:
        print(f'{game.pgn} for a {game.result}')
    else:
      print(f"{self.player} hasn't played any games... or doesn't exist yet")

    print("\n")



def load_urls_from_file():
    with open("urls.txt", "r") as f:
      data = f.read()
    return data