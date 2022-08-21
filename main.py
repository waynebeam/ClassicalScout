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
  type_of_games = ""
  
  def __init__(self, player_name:str):
    self.player = player_name.lower()
    self.url = f'https://lichess.org/@/{player_name}/rated'
    # self.url = 'https://lichess.org/api/games/user/Fins?tags=true&clocks=false&evals=false&opening=false&max=20&perfType=classical'

  def scout(self):
    self.type_of_games = "rated"
    response = requests.get(self.url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser") 
    games = soup.findAll("article")
    
    for game in games:
      white_player = self.find_name_of_white_player(game)
      player_is_white = self.player == white_player
      if player_is_white:
        self.player_color = "White"
      else:
        self.player_color = "Black"

      result_tag = game("div", class_="result")[0].text
      
      if "Draw" in result_tag:
        self.result = "Draw"
      elif "White is" in result_tag:
        if player_is_white:
          self.result = "Win"
        else:
          self.result = "Loss"
      elif "Black is" in result_tag:
        if not player_is_white:
          self.result = "Win"
        else:
          self.result = "Loss"
      elif "Playing right now" in result_tag:
        continue
      elif "aborted" in result_tag:
        continue
        
      pgn = game("div", class_="pgn")[0].text
      self.pgn = re.compile(r'1\. \w+ \w+ 2\. \w+ \w+').search(pgn).group()
      

      self.all_games.append(self.make_game_score())

    self.print_output()

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
    white_pgns = []
    black_pgns = []
    if self.all_games:
      for game in self.all_games:
        #print(game)
        
        result = game.result
        pgn = game.pgn + f" for a {result}"

        if game.color == "White":
          white_pgns.append(pgn)
          if game.result == "Win":
            white_wins += 1
          elif game.result == "Loss":
            white_losses += 1
        elif game.color == "Black":
          black_pgns.append(pgn)
          if game.result == "Win":
            black_wins += 1
          elif game.result == "Loss":
            black_losses += 1
      print(f"\nIn the last {len(self.all_games)} of {self.player}'s {self.type_of_games} games:")
      print(f"{self.player} had {white_wins+black_wins} wins and {white_losses+black_losses} losses\n")
      print(f"as White \n they had {white_wins} wins and {white_losses} losses playing:")
      for moves in white_pgns:
        print(moves)
      print(f"\nas Black \n they had {black_wins} wins and {black_losses} losses playing:")
      for moves in black_pgns:
        print(moves)
    else:
      print(f"{self.player} hasn't played any games... or doesn't exist yet")

  def classical_scout(self):
    self.type_of_games = "classical"
    url = f'https://lichess.org/api/games/user/{self.player}?tags=true&clocks=false&evals=false&opening=false&max=12&perfType=classical'

    white_pattern = re.compile(r'\[White "(\w+-*\w*)"')
    pgn_pattern = re.compile(r'1\. \w+ \w+ 2\. \w+ \w+')
    result_pattern = re.compile(r'\[Result "(\d(-|/)\d)')
    
    response = requests.get(url)
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
      self.all_games.append(self.make_game_score())

    self.print_output()


def Main():
  classical_words = ['c', 'classic', 'classical', 'slow']
  player_name = input("Who would you like to scout on Lichess?: ")
  player_name = player_name.split()
  if len(player_name) > 1:
    scout = Scout_Player(player_name[0])
    if player_name[1] in classical_words:
      scout.classical_scout()
    else:
      scout.scout()
  else:
    scout = Scout_Player(player_name[0])
    scout.scout()

if __name__ == "__main__":
  Main()











