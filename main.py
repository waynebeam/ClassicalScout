import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

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
  
  def __init__(self, player_name:str):
    self.player = player_name
    self.url = 'https://lichess.org/@/'+self.player+'/rated'


  def scout(self):
    response = requests.get(self.url)
    
    html = response.text
    
    soup = BeautifulSoup(html, "html.parser")
    
    
    games = soup.findAll("article")
    
    for game in games:
    
      white_player = game("div", class_="player white")
   
      player_is_white = white_player[0].a.text == self.player
      if player_is_white:
        self.player_color = "White"
       
      else:
        self.player_color = "Black"
        
      
      self.pgn = game("div", class_="pgn")[0].text
      
      result_tag = game("div", class_="result")[0].text
      #print(result_tag)
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


      self.all_games.append(self.make_game_score())
    


    self.print_output()

  def make_game_score(self):
    score = ChessGameScore(player=self.player, color=self.player_color, pgn=self.pgn,result=self.result)

    return score

  def print_output(self):
    print(f"{self.player} has played:")
    # print(f'White Games = {len(self.white_games)}')
    # print(f'Black games = {len(self.black_games)}')
    # print(f"Drawn games = {len(self.drawn_games)}")
    # print('As white they have played: ')
    # for white_game in self.white_games:
    #  print(f'{white_game.pgn} and {white_game.result}')
    # print('As black they have played: ')
    # for black_game in self.black_games:
    #  print(f'{black_game.pgn} and {black_game.result}')
    print(len(self.all_games))
    for game in self.all_games:
      print(f"{game.color} and played {game.pgn} and {game.result}")
          


test = Scout_Player('waynebeam')
test.scout()












