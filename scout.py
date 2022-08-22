from dataclasses import dataclass
import requests
import re

class Scout:
  player_color: str
  result: str
  pgn: str
  white_games = []
  black_games = []
  drawn_games = []
  all_games = []
  type_of_games_dict = {}
  type_of_games = ""
  urls_dict = {}
  
  def __init__(self, player_name:str, search_type: str):
    self.player = player_name.lower()
    self.prepare_url_and_type_dicts()
    if search_type in self.urls_dict:
      self.url = self.urls_dict[search_type]
      self.type_of_games = self.type_of_games_dict[search_type]
    else:
      self.url = self.urls_dict["all"]
      self.type_of_games_dict["all"]

  def prepare_url_and_type_dicts(self):
    classical_url = f'https://lichess.org/api/games/user/{self.player}?rated=&tags=true&clocks=false&evals=false&opening=false&max=20&perfType=classical'
    all_games_url = f'https://lichess.org/api/games/user/{self.player}?rated=true&tags=true&clocks=false&evals=false&opening=false&max=20&perfType=ultraBullet%2Cbullet%2Cblitz%2Crapid%2Cclassical'
    fast_games_url = f'https://lichess.org/api/games/user/{self.player}?rated=true&tags=true&clocks=false&evals=false&opening=false&max=20&perfType=bullet%2Cblitz%2Crapid'

    classical_words = ['classical',"c", "classic", "long", "slow"]
    all_games_words = ["rated","all"]
    fast_games_words = ['fast', 'rapid', 'blitz', 'quick', 'speed']
    
    self.add_to_url_and_type_dicts(classical_words,classical_url)
    self.add_to_url_and_type_dicts(all_games_words,all_games_url)
    self.add_to_url_and_type_dicts(fast_games_words,fast_games_url)



  def add_to_url_and_type_dicts(self,word_list,url):
    for word in word_list:
      self.urls_dict[word] = url
      self.type_of_games_dict[word] = word_list[0]
    
  def scout(self):
   
    white_pattern = re.compile(r'\[White "(\w+-*\w*)"')
    result_pattern = re.compile(r'\[Result "(\d(-|/)\d)')
    pgn_pattern = re.compile(r'1\. \w+ \w+ 2\. \w+ \w+')

    data = self.download_data_from_lichess()
    games = self.split_data_into_games(data)
    
    for game in games[1:]:     
      self.set_player_color(game,white_pattern)
      self.set_result(game,result_pattern)
      self.pgn = pgn_pattern.search(game).group()
      game_score = self.make_game_score()
      self.all_games.append(game_score)
      if game_score.color == "White":
        self.white_games.append(game_score)
      else:
        self.black_games.append(game_score)
    

  def download_data_from_lichess(self):
    response = requests.get(self.url)
    data = response.text
    return data

  def split_data_into_games(self,data):
    games = data.split("[Event")
    return games  

  def set_player_color(self, game, pattern):
    p = pattern.search(game).group(1).lower()
    if p == self.player:
      self.player_color = "White"
    else:
      self.player_color = "Black"

  def set_result(self, game, pattern):
    result = pattern.search(game).group(1)
    if result == "1/2":
      self.result = "Draw"
    elif result == "1-0":
      if self.player_color == "White":
        self.result = "Win"
      else:
        self.result = "Loss"
    elif result == "0-1":
      if self.player_color == "Black":
        self.result = "Win"
      else:
        self.result = "Loss"
      
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


@dataclass
class ChessGameScore:
  player: str
  color: str
  pgn: str
  result: str