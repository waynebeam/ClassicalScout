import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re

@dataclass
class ChessGameScore:
  player: str
  color: str
  pgn: str
  result: str


class Scout_Player:
  player_color: str
  result: str
  pgn: str
  white_games = []
  black_games = []
  drawn_games = []
  all_games = []
  type_of_games_dict = {}
  type_of_games = ""
  
  
  def __init__(self, player_name:str, search_type: str):
    self.player = player_name.lower()
    self.urls = self.build_url_dict()
    if search_type in self.urls:
      self.url = self.urls[search_type]
      self.type_of_games = self.type_of_games_dict[search_type]
    else:
      self.url = self.urls["all"]
      self.type_of_games_dict["all"]

  def build_url_dict(self):
    classical_url = f'https://lichess.org/api/games/user/{self.player}?tags=true&clocks=false&evals=false&opening=false&max=20&perfType=classical'
    all_games_url = f'https://lichess.org/api/games/user/{self.player}?tags=true&clocks=false&evals=false&opening=false&max=20&perfType=ultraBullet%2Cbullet%2Cblitz%2Crapid%2Cclassical'

    classical_words = ["c", "classic", "classical"]
    all_games_words = ["all", "rated", "r"]
    urls_dict = {}
    for word in classical_words:
      urls_dict[word] = classical_url
      self.type_of_games_dict[word] = "classical"
    for word in all_games_words:
      urls_dict[word] = all_games_url
      self.type_of_games_dict[word] = "rated"

    return urls_dict
  
  def find_name_of_white_player(self,game):
    raw_name = game("div", class_="player white")
    white_player_name = raw_name[0].a.text.lower()
    white_player_name = white_player_name.split()
    if len(white_player_name) > 1:
      white_player_name = white_player_name[1]
    else: 
      white_player_name = white_player_name[0]
    
    return white_player_name

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
        #print(game)
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

  def scout(self):
   
    white_pattern = re.compile(r'\[White "(\w+-*\w*)"')
    pgn_pattern = re.compile(r'1\. \w+ \w+ 2\. \w+ \w+')
    result_pattern = re.compile(r'\[Result "(\d(-|/)\d)')
    
    response = requests.get(self.url)
    data = response.text
    games = data.split("[Event")
    for game in games[1:]:
      p = white_pattern.search(game).group(1).lower()
      if p == self.player:
        self.player_color = "White"
      else:
        self.player_color = "Black"

      result = result_pattern.search(game).group(1)
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
      
      self.pgn = pgn_pattern.search(game).group()
      game_score = self.make_game_score()
      self.all_games.append(game_score)
      if game_score.color == "White":
        self.white_games.append(game_score)
      else:
        self.black_games.append(game_score)

    


def Main():
  
  player_name = input("Who would you like to scout on Lichess?: ")
  player_name = player_name.split()
  if len(player_name) == 1:
    player_name.append("all")

  scout = Scout_Player(player_name[0], player_name[1])
    
  scout.scout()

  if __name__ == "__main__":
    scout.print_output()
    
if __name__ == "__main__":
  Main()











