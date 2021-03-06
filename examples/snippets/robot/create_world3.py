import logging
import sys
import gamegridp


class MyGrid(gamegridp.GameGrid):
    """My Grid with custom setup method."""

    def setup(self):
        self.toolbar.add_button("Speichern", "images/rock.png")

    def listen(self, event=None, data=None):
        self._logging.info("Event : "+str(event))
        if event == "mouse_left":
            if self.is_empty_cell((data[0], data[1])):
                Wall(self, (data[0], data[1]))
                self._logging.info("Wall created at: " + str(data[0]) + "," + str(data[1]))
            else:
                self.remove_actor(cell=(data[0], data[1]))
        elif event == "mouse_right":
            if self.is_empty_cell((data[0], data[1])):
                Robot(self, (data[0], data[1]))
                self._logging.info("Robo created at: " + str(data[0]) + "," + str(data[1]))
            else:
                self.remove_actor(cell=(data[0], data[1]))
        elif event == "button":
            self._logging.info("Button " + str(data) + " pressed")


class Robot(gamegridp.Actor):
    def setup(self):
        self.is_rotatable = True
        self.add_image("images/robo_green.png", "scale", (40, 40))

    def act(self):
        self.move(1)


class Wall(gamegridp.Actor):
    def setup(self):
        self.is_blocking = True
        self.add_image("images/rock.png", img_action="scale")


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
mygrid = MyGrid("My Grid", cell_size=60, columns=10, rows=10,
                margin=0, speed=120, img_path="images/stone.jpg", toolbar=True)
mygrid.show()
