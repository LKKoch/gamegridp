import sys
sys.path.insert(0, "D:\\Code\\gamegridp\\gamegridp")
sys.path.insert(0, "D:\\Code\\gamegridp\\actor")
from gamegridp import actor
from gamegridp import gamegrid
#print(dir (gamegridp))
#print (gamegridp.__file__)
#print(sys.path)
import gamegrid
import logging

class MyGrid(gamegrid.GameGrid):
    def setup(self):
        player1=Player("Player",mygrid, (3,3), img_path="images/char_blue.png",
                       img_action="do_nothing")
        #player2=Player("Player",mygrid, (8,2), img_path="images/char_blue.png",
        #               img_action="do_nothing")


class Player(actor.Actor):
    def act(self):
        for i in range(3):
            if self.is_move_valid():
                self.move()
            else:
                self.turn_left()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
module_logger = logging.getLogger('gglogger')
mygrid=MyGrid("My Grid", log=True, cell_size=12, columns=16, rows=16,margin=5,
              img_path="images/soccer_green.jpg")
mygrid.show()
