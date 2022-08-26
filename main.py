from scout import Scout

def Main():
  quit_words = ["esc", "quit", "q", "x"]
  prompt = "Who would you like to scout on Lichess?: "
  while (player_name := input(prompt)).lower() not in quit_words:
    if player_name != "help":
      player_name = player_name.split()
      if len(player_name) == 1:
        player_name.append("all")
    
      scout = Scout(player_name[0], player_name[1])
      scout.scout()
    
      if __name__ == "__main__":
        scout.scouting_report.print_output()
    else:
      print_help()

  print("goodbye")

def print_help():
  print("\nEnter a lichess.org username and receive the result and opening of their last 20 games.\nUse it to prep for your opponent.\nType \"classical\" after the name to see the last 20 classical games or\n\"fast\" to see the blitz and bullet games.\nA username alone will find rated games of any time-control\nMade by @waynebeam I hope you find it useful!\n")

  
if __name__ == "__main__":
  Main()











