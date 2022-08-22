from scout import Scout

def Main():
  
  player_name = input("Who would you like to scout on Lichess?: ")
  player_name = player_name.split()
  if len(player_name) == 1:
    player_name.append("all")

  scout = Scout(player_name[0], player_name[1])
    
  scout.scout()

  if __name__ == "__main__":
    scout.print_output()


if __name__ == "__main__":
  Main()











