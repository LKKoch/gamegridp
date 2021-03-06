# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 21:49:29 2018

@author: asieb
"""
import logging
import os

import easygui
import pygame
from gamegridp import gamegrid_actionbar
from gamegridp import gamegrid_console
from gamegridp import gamegrid_toolbar
from gamegridp import keys


class GameGrid(object):
    """
    Das GameGrid
        Das **GameGrid** ist ein **Spielfeld**, welches in einzelne Zellen unterteilt ist.
        Es kann unterschieden werden zwischen zwei Arten von GameGrids:

        * Die Zellengröße ist 1: Es handelt sich um ein pixelgenaues Spiel
            bei dem die exakte Position der Akteure von Bedeutung ist.
        * Die Zellengröße ist größer als 1: Es handelt sich um ein Spiel, das auf einzelnen
            Feldern basiert.

        Für beide Arten von Spielen gibt es einige Subklassen, die Spezialfunktionen zur Verfügung stellen.

    **Attribute:**

        * cell_size: int
            Die Größe einer einzelnen Zelle in Pixeln.
        * toolbar : gamegridp.Toolbar
            Die Toolbar auf der rechten Seite
        * actionbar : gamegridp.Actionbar
            Die Actionbar unterhalb des Spielfeldes.
        * console : gamegridp.Console
            Die Konsole unterhalb des Spielfeldes.
        * is_running : bool
            Bestimmt, ob Act() in jedem Durchlauf der Mainloop ausgeführt wird.
        * speed: int
            Die Geschwindigkeit mit der das Spiel läuft (bisher nur als Max. Geschwindigkeit definiert)
        * rows: int
            Die Anzahl der Zeilen.
        * columns: int
            Die Anzahl der Spalten.

        **Methoden:**

        """

    # Properties

    @property
    def is_running(self):
        return self._running

    @is_running.setter
    def is_running(self, value):
        self._running = value


    @property
    def cell_size(self):
        """"""
        return self._cell_size

    @property
    def cell_margin(self):
        """
        returns the margin between cells
        """
        return self._cell_margin

    @cell_size.setter
    def cell_size(self, value: int):
        """ Sets the cell-size"""
        self._cell_size = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def rows(self):
        """
        returns the margin between cells
        """
        return self._grid_rows

    @property
    def columns(self):
        """
        returns the margin between cells
        """
        return self._grid_columns


    # Methoden

    def __init__(self, title, cell_size=32,
                 columns=8, rows=8, margin=0,
                 background_color=(255, 255, 255), cell_color=(0, 0, 0),
                 img_path=None, img_action="upscale", speed=60, toolbar=False, console=False, actionbar=True):

        self.grid = self
        self.__is_setting_up__ = False
        # Define instance variables
        self.title = title  #
        self._logging = logging.getLogger('GameGrid')
        self.__done__ = False
        self._image = None
        self._grid = []
        self._info = False
        self._actors = []
        self._frame = 0
        self.colliding_actors = []
        self._resolution = ()
        self._running = False
        self.effects = set()
        self._cell_margin = 0
        self._collision_type = "cell"
        self._image = None
        self._cell_transparency = 0
        self._clock = None
        self._grid_rows = 0
        self._grid_columns = 0
        self._background_color = (255, 255, 255)
        self._cell_color = (0, 0, 0)
        self._draw_queue = []  # a queue of rectangles
        self._key_pressed = False
        self._key = 0
        self._speed = speed
        self._animated = False
        self._show_bounding_boxes = False
        self._show_direction_marker = False
        if toolbar is True:
            self.toolbar = gamegrid_toolbar.Toolbar(self)
        else:
            self.toolbar = None
        if actionbar is True:
            self.actionbar = gamegrid_actionbar.Actionbar(self)
        else:
            self.actionbar = None
        if console is True:
            self.console = gamegrid_console.Console(self, 5)
        else:
            self.console = None
        """
        Initialises the grid
        """
        # attributes
        self._cell_margin = margin
        self._grid_columns = columns
        self._grid_rows = rows
        self._cell_size = cell_size
        if self.cell_size == 1:
            self._collision_type = "bounding_box"
        else:
            self._collision_type = "bounding_box"
        self._background_color = background_color
        self._cell_color = cell_color
        # grid and grid-dimensions
        for row in range(rows):
            self._grid.append([])
            for column in range(columns):
                self._grid[row].append(0)
        # Init gui
        if self.toolbar is not None:
            _toolbar_width = self.toolbar.width
        else:
            _toolbar_width = 0
        if self.actionbar is not None:
            _actionbar_height = self.actionbar.height
        else:
            _actionbar_height = 0
        if self.console is not None:
            _console_height = self.console.height
        else:
            _console_height = 0
        x_res = self.__grid_width_in_pixels__ + _toolbar_width
        y_res = self.__grid_height_in_pixels__ + _actionbar_height + _console_height  # 100 pixels for actionbar
        if self.toolbar is not None:
            self.toolbar.set_height(y_res)
            self.toolbar.set_posx(self.__grid_width_in_pixels__)
        if self.actionbar is not None:
            self.actionbar.set_width(x_res)
            self.actionbar.set_posy(self.__grid_height_in_pixels__)
        if self.console is not None:
            self.console.set_width(x_res)
            self.console.set_posy(self.__grid_height_in_pixels__ + _actionbar_height)
        self._resolution = x_res, y_res
        WINDOW_SIZE = (self._resolution[0], self._resolution[1])
        self._logging.info(
            "gamegrid.__init__(): Created windows of dimension: (" + str(self._resolution[0]) + "," + str(
                self._resolution[1]) + ")")
        # Init pygame
        pygame.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.grid_surface = pygame.Surface((self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
        self.grid_surface.fill((255, 255, 255))
        pygame.display.set_caption(title)
        pygame.screen.fill((255, 255, 255))
        # Init clock
        self.clock = pygame.time.Clock()
        # time of last frame change
        self.last_update = pygame.time.get_ticks()
        # current frame
        self._frame = 0
        pygame.init()
        # image
        self.set_image(img_path, img_action)
        self._setup()
        # Draw_Qeue
        pygame.screen.blit(self.grid_surface, (0, 0, self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
        self._draw_queue.append(pygame.Rect(0, 0, self._resolution[0], self._resolution[1]))

    def set_image(self, img_path: str, img_action: str = "upscale", size=None):
        """
        Setzt das Hintergrundbild des Grids

        :param img_path: Der Pfad zum Bild als relativer Dateipfad
        :param img_action: Die Aktion, die mit dem Bild durchgeführt werden soll (scale, upscale, fill, crop
        :param size: Die Größe auf die das Bild skaliert / zugeschnitten etc. werden soll
        """
        self._logging.info(
            "gamegrid.set_image : Set new image with action:" + str(img_action) + " and path:" + str(img_path))
        if img_path is not None:
            self._image = pygame.image.load(img_path).convert()
            self._image = self._image
            self._cell_transparency = 0
            if img_path is not None and img_action == "scale":
                if size is None:
                    self._image = pygame.transform.scale(self._image,
                                                         (
                                                             self.__grid_width_in_pixels__,
                                                             self.__grid_height_in_pixels__))
                else:
                    self._image = pygame.transform.scale(self._image, (size[0], size[1]))
                self._image = pygame.transform.scale(
                    self._image, (self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
            elif img_path is not None and img_action == "upscale":
                if self._image.get_width() < self.__grid_width_in_pixels__ or self._image.get_height() < self.__grid_height_in_pixels__:
                    self._image = pygame.transform.scale(
                        self._image, (self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
            elif img_path is not None and img_action == "fill":
                if size is None:
                    self._image = pygame.transform.scale(self._image,
                                                         (self.cell_size, self.cell_size))
                else:
                    self._image = pygame.transform.scale(self._image, (size[0], size[1]))
                i = 0
                j = 0
                surface = pygame.Surface((self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
                while (i < self.__grid_width_in_pixels__):
                    j = 0
                    while (j < self.__grid_height_in_pixels__):
                        surface.blit(self._image, (i, j), (0, 0, self._image.get_width(),
                                                           self._image.get_height()))
                        j = j + self._image.get_height() + self.cell_margin
                    i = i + self._image.get_width() + self.cell_margin
                self._image = surface
        else:
            self._cell_transparency = None
            self._image = pygame.Surface((self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))

        # Crop surface
        cropped_surface = pygame.Surface((self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
        cropped_surface.fill((255, 255, 255))
        cropped_surface.blit(self._image, (0, 0),
                             (0, 0, self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
        self._image = cropped_surface
        # draw grid around the cells
        if self._cell_margin > 0:
            i = 0
            while i <= self.__grid_width_in_pixels__:
                pygame.draw.rect(self._image, self._background_color,
                                 [i, 0, self._cell_margin, self.__grid_height_in_pixels__])
                i += self.cell_size + self._cell_margin
            i = 0
            while i <= self.__grid_height_in_pixels__:
                pygame.draw.rect(self._image, self._background_color,
                                 [0, i, self.__grid_width_in_pixels__, self._cell_margin])
                i += self.cell_size + self._cell_margin
        self._draw_queue.append(pygame.Rect(0, 0, self._resolution[0], self._resolution[1]))

    def act(self):
        """
        Überschreibe diese Methode in deinen Kind-Klassen
        """
        pass

    def add_actor(self, actor, location=None):
        self._actors.append(actor)
        self.repaint_area(actor.image_rect)
        if location is not None:
            actor.location = location

    def __act_all__(self):
        for actor in self._actors:
            actor.act()
        self.act()



    def draw(self):
        """
        draws the entire window with grid, actionbar and toolbar
        :return:
        """
        self.__draw_grid__()
        self.__draw_actionbar__()
        self.__draw_toolbaar__()
        self.__draw_console__()

    def __draw_grid__(self):
        """
        Draws grid with all actors in it.
        """
        # Draw the gamegrid-cells
        if self._image is not None:
            self.grid_surface.blit(self._image, (0, 0, self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))
        for actor in self._actors:
            actor._next_sprite()
            actor.draw()
        pygame.screen.blit(self.grid_surface, (0, 0, self.__grid_width_in_pixels__, self.__grid_height_in_pixels__))

    def __draw_toolbaar__(self):
        if self.toolbar is not None:
            self.toolbar.draw()
            self.grid._draw_queue.append(pygame.Rect(0, 0, self._resolution[0], self._resolution[1]))

    def __draw_console__(self):
        if self.console is not None:
            self.console.draw()
            self.grid._draw_queue.append(pygame.Rect(0, 0, self._resolution[0], self._resolution[1]))

    def __draw_actionbar__(self):
        if self.actionbar is not None:
            self.actionbar.draw()
            self.grid._draw_queue.append(pygame.Rect(0, 0, self._resolution[0], self._resolution[1]))


    @property
    def actors(self) -> list:
        """
        returns all actors in grid
        :return: a list of all actors
        """
        return self._actors

    @property
    def frame(self) -> int:
        """
        Returns the actual frame
        :return: the value of actual frame
        """
        return self._frame


    @property
    def __grid_width_in_pixels__(self) -> int:
        """ returns the grid with in pixes
        :return: The grid_width in pixels
        """
        return self._grid_columns * self.cell_size + (self._grid_columns + 1) * self._cell_margin

    @property
    def __grid_height_in_pixels__(self) -> int:
        """ returns the grid-height in pixels"""
        height = self._grid_rows * self.cell_size + (self._grid_rows + 1) * self._cell_margin
        return height

    def __grid_dimensions_in_pixels__(self) -> tuple:
        """
        Returns the grid-dimension in pixesls
        :return:
        """
        return self.__grid_width_in_pixels__, self.__grid_height_in_pixels__

    def __check_collision_cell__(self, actor1, actor2) -> bool:
        """
        Checks if two actors are in the same cell
        :param actor1: first actor
        :param actor2: partner
        :return: true if both actors are on the same cell
        """
        if actor1.is_in_grid(self) and actor2.is_in_grid(self):
            self._logging.debug(
                "gamegrid.collision_cell() : Collision? A1:" + str(actor1.location) + ",A2:" + str(actor2.location))
            if actor1.location == actor2.location:
                return True
            else:
                return False

    def __check_collision_bounding_box__(self, actor1, actor2) -> bool:
        """
        Checks if the bounding boxes of two actors collide
        :param actor1: first actor
        :param actor2: partner
        :return: true if the bounding boxes collide
        """
        if actor1.bounding_box().colliderect(actor2.bounding_box()):
            self._logging.debug("gamegrid.collision_bounding_box: colliding")
            return True
        else:
            self._logging.debug("gamegrid.collision_bounding_box: not colliding")
            return False

    def __get_bounding_box_collisions__(self, actor):
        """
        Gets all bounding box collisions for one actor
        :param actor:
        :return:
        """
        for partner in actor._collision_partners:
            if self.__check_collision_bounding_box__(actor, partner):
                return partner
        return None

    def __get_cell_collisions__(self, actor):
        """
        Gets all cell collisions for one actor
        :param actor:
        :return:
        """
        for partner in actor._collision_partners:
            if self.__check_collision_cell__(actor, partner):
                return partner
        return None

    def _collision(self):
        self._logging.debug("gamegrid.__collision__() - Type:" + str(self._collision_type))
        pairs = []
        for actor in self.actors:
            if self._collision_type == "bounding_box":
                partner2 = self.__get_bounding_box_collisions__(actor)
                if partner2 is not None:
                    partner1 = actor
                    if (partner2, partner1) not in pairs:
                        pairs.append((partner1, partner2))
            else:
                partner2 = self.__get_cell_collisions__(actor)
                if partner2 is not None:
                    partner1 = actor
                    if (partner2, partner1) not in pairs:
                        pairs.append((partner1, partner2))
        for pair in pairs:
            partner1 = pair[0]
            partner2 = pair[1]
            if pair not in self.colliding_actors:
                self.collision(partner1, partner2)
        self.colliding_actors = pairs

    def collision(self, partner1, partner2):
        """
        Überschreibe diese Methoden, wenn du Kollisionen handhaben möchtest.
        """

    def get_actors_at_location(self, location: tuple, class_name: str = "") -> list:
        """
        Gebe alle Akteure an den angegebenen Zellenkoordinaten zurück

        :param location: Die Zellenkordinaten als Tupel (x,y)
        :param class_name: Den Klassennamen, nachdem gefiltert werden soll
        :return: Eine Liste aller Akteure (mit der angegebenen Klasse) an der Position.
        """
        actors_at_location = []
        for actor in self._actors:
            if actor.location == location:
                if class_name is "" or actor.__class__.__name__ == class_name:
                    actors_at_location.append(actor)
        return actors_at_location

    def is_location_in_grid(self, location):
        """
        Gibt an, ob eine Zellenkoordinate im Grid liegt

        :param location: Die Zellenkoordinate als Tupel (x,y)
        :return: True falls Koordinate im Grid, ansonsten False
        """
        if location[0] > self._grid_columns - 1:
            return False
        elif location[1] > self._grid_rows - 1:
            return False
        elif location[0] < 0 or location[1] < 0:
            return False
        else:
            return True

    def is_at_left_border(self, rect) -> bool:
        """
        Überprüfe, ob das Rechteck über den linken Rand hinausragt

        :param rect:
        :return: True, falls Ja, ansonsten False
        """
        if rect.topleft[0] <= 0:
            return True
        else:
            return False

    def is_at_bottom_border(self, rect):
        """
        Überprüfe, ob das Rechteck über den unteren Rand hinausragt

        :param rect:
        :return: True, falls Ja, ansonsten False
        """
        if rect.topleft[1] + rect.height >= self.__grid_height_in_pixels__:
            return True
        else:
            return False

    def is_at_right_border(self, rect):
        """
        Überprüfe, ob das Rechteck über den rechten Rand hinausragt

        :param rect:
        :return: True, falls Ja, ansonsten False
        """
        if rect.topleft[0] + rect.width >= self.__grid_width_in_pixels__:
            return True
        else:
            return False

    def is_at_top_border(self, rect):
        """
        Überprüfe, ob das Rechteck über den oberen Rand hinausragt

        :param rect:
        :return: True, falls Ja, ansonsten False
        """
        if rect.topleft[1] <= 0:
            return True
        else:
            return False

    def is_rectangle_in_grid(self, rect) -> bool:
        """
        Überprüfe, ob das Rechteck komplett im Grid ist.

        :param rect: Ein Rechteck
        :return: True, falls Ja, ansonsten False
        """
        if rect.topleft[0] < 0 \
                or rect.topleft[1] < 0 \
                or rect.topleft[0] + rect.width > self.__grid_width_in_pixels__ \
                or rect.topleft[1] + rect.height > self.__grid_height_in_pixels__:
            self._logging.info("is_rectangle_in_grid() : false)")
            return False  # rectangle is not in grid
        else:
            self._logging.info("is_rectangle_in_grid() : true)")
            return True  # rectangle is in grid

    def is_empty_cell(self, cell: tuple) -> bool:
        """
        Überprüfe, ob eine Zelle leer ist.

        :param cell: Die Zellenkoordinaten als Tupel (x,y)
        :return: True, falls Ja, ansonsten False
        """
        if not self.get_actors_at_location(cell):
            return True
        else:
            return False

    def __listen__(self):
        """
        Listen to key events
        """
        if self.__is_setting_up__:
            return
        key_pressed = False
        self._logging.debug("gamegrid.__listen__() : Listen...")
        do_act = False
        for event in pygame.event.get():
            key = False
            cell = False
            # Event: Quit
            if event.type == pygame.QUIT:
                self.__done__ = True
                pygame.quit()
                os._exit(0)
            # Event: Mouse-Button Down
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                self._logging.info("gamegrid.__listen__(): Mouseclick with button:" + str(event.button))
                # Click is in gamegrid
                if pos[0] < self.__grid_width_in_pixels__ and pos[
                    1] < self.__grid_height_in_pixels__ and event.button == 1:
                    cell_location = self.__pixel_to_cell__(pos)
                    self._logging.info("gamegrid.__listen__() : " + str(cell_location))
                    column = cell_location[0]
                    row = cell_location[1]
                    cell_clicked = (column, row)
                    self.__listen_all__("mouse_left", cell_location)
                    self._logging.info("gamegrid.__listen__(): Mouseclick left at grid-position:" +
                                       str(cell_clicked))
                elif pos[0] < self.__grid_width_in_pixels__ and pos[
                    1] < self.__grid_height_in_pixels__ and event.button == 3:
                    cell_location = self.__pixel_to_cell__(pos)
                    self._logging.info("gamegrid.__listen__() : " + str(cell_location))
                    column = cell_location[0]
                    row = cell_location[1]
                    cell_clicked = (column, row)
                    self._logging.info("gamegrid.__listen__(): - Mouseclick right at grid-position:" +
                                       str(cell_clicked))
                    self.__listen_all__("mouse_right", cell_location)
                # Click is in status_bar
                elif pos[1] >= self.__grid_height_in_pixels__:
                    if pos[0] > 5 and pos[0] < 60:
                        if not self._running:
                            self._logging.debug("gamegrid.__listen__(): : Act")
                            return True
                    elif pos[1] >= self.__grid_height_in_pixels__ and pos[0] > 60 and pos[
                        0] < 120 and not self._running:
                        self._running = True
                        self._logging.debug("gamegrid.__listen__(): : Play")
                    elif pos[1] >= self.__grid_height_in_pixels__ and pos[0] > 60 and pos[0] < 120 and self._running:
                        self._running = False
                        self._logging.debug("gamegrid.__listen__() : Pause")
                    elif pos[1] >= self.__grid_height_in_pixels__ and pos[0] > 120 and pos[0] < 220:
                        self._logging.info("gamegrid.__listen__() : Reset")
                        self._running = False
                        self.reset()
                    elif pos[1] >= self.__grid_height_in_pixels__ and pos[0] > 220 and pos[0] < 280:
                        self._logging.info("gamegrid.__listen__() : Info")
                        if self._info == True:
                            self._show_bounding_boxes = False
                            self._show_direction_marker = False
                            self._info = False
                        elif self._info == False:
                            self._show_bounding_boxes = True
                            self._show_direction_marker = True
                            self._info = True
                    elif pos[1] >= self.__grid_height_in_pixels__ and pos[0] > 285 and pos[0] < 345:
                        self.speed = self.speed - 1
                    elif pos[1] >= self.__grid_height_in_pixels__ and pos[0] > 345 and pos[0] < 395:
                        self.speed = self.speed + 1
                elif pos[0] > self.__grid_width_in_pixels__:
                    toolbar_event = self.toolbar.listen("mouse_left", position=(pos[0], pos[1]))
                    self.__listen_all__(toolbar_event)
            elif event.type == pygame.KEYDOWN:
                keys_pressed = pygame.key.get_pressed()
                self.__listen_all__("key_down", keys.key_pressed_to_key(keys_pressed))
        if pygame.key.get_pressed().count(1) != 0:
            keys_pressed = pygame.key.get_pressed()
            self.__listen_all__("key", keys.key_pressed_to_key(keys_pressed))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x > self.__grid_width_in_pixels__:
            toolbar_event = self.toolbar.listen("mouse_hover", position=(mouse_x, mouse_y))

        return False

    def __listen_all__(self, event: str = None, data=None):
        """ Calls listen of grid and all actors """
        self.listen(event, data)
        for actor in self._actors:
            actor.listen(event, data)

    def listen(self, event: str = None, data=None):
        """
        Überschreibe diese Methode in deiner Kind-Klasse

        :param event: Das Event, welches getriggert wurde. Mögliche Events:
            * mousedown
            * key_pressed / key - Eine taste wird gedrückt (gehalten)
            * key_down - Eine Taste wird gerade heruntergedrückt
            * button_name Falls ein Button geklickt wurde.
        :param data: Zusätzliche Infos, wie z.B. die gedrückten Tasten oder
            die Koordinaten der Maus.
        """
        pass

    def __update__(self, no_logic: bool = False, no_drawing: bool = False):
        ''' Part 1:
        For grid an all actors
        listen to events
        react with listen() method
        '''
        if self.__is_setting_up__:
            no_logic = True
            no_drawing = True
            max_speed = 120
        else:
            max_speed = self._speed
        if not no_logic:
            do_act = self.__listen__()
            ''' Part 2:
                For grid an all actors
                act()
            '''
            if (self._running or do_act) and (not no_logic):
                self.__act_all__()
        ''' Part 3: Draw actors
            Draw actors in every frame, regardless of speed
        '''
        if not no_logic:
            self._collision()
        if not no_drawing:
            self.draw()
            pygame.display.update(self._draw_queue)
            self._draw_queue = []
        self._logging.debug("gamegrid.update() : str(self.clock.tick()")
        if not no_logic:
            self.clock.tick(max_speed)
            self._logging.debug("gamegrid.update() frame:" + str(self._frame) + "speed:" + str(max_speed) + "tick:")
        if self._frame % max_speed == 0:
            self._frame = 1
        else:
            self._frame = self._frame + 1

    def repaint_area(self, rect: pygame.Rect):
        self._draw_queue.append(pygame.Rect(rect))

    def remove_actor(self, actor=None, cell: tuple = None):
        """
        Entfernt einen Akteur aus dem Grid

        :param actor: Der zu entfernende Akteur
        :param cell: Entfernt alle Akteure an einer Zelle (actor wird dann ignoriert)
        :return:
        """
        if cell == None:
            actor.remove()
        else:
            actors_at_cell = self.get_actors_at_location(cell)
            self._logging.info("gamegrid.remove_actor(): Remove actor at: " + str(cell))
            for actor in actors_at_cell:
                try:
                    self._logging.info("gamegrid.remove_actor() : remove_actor" + str(actor) + " wird gelöscht...")
                    self._actors.remove(actor)
                    actor._remove_from_grid()
                except ValueError:
                    self._logging.warning("gamegrid.remove_actor() : Nicht in Liste vorhanden")

    def remove_all_actors(self):
        """
        Entfernt alle Akteure aus dem Grid.
        """
        for actor in self._actors:
            self.remove_actor(actor)
        self._actors = []

    def reset(self):
        """
        Entfernt alle Akteure aus dem Grid und setzt sie an ihre Ursprungspositionen.
        """
        self.remove_all_actors()
        self._setup()
        self._draw_queue.append(pygame.Rect(0, 0, self._resolution[0], self._resolution[1]))
        self.__update__(no_logic=True, no_drawing=True)

    def stop(self):
        """
        Stoppt die Ausführung (siehe auch run)
        """
        self._running = False

    def run(self):
        """
        Startet die Ausführung (equivalent zum Drücken des Run-Buttons).
        Wenn das Spiel läuft handeln die Akteure mit jedem Durchlauf der mainloop genau einmal.
        """
        self._running = True


    def show(self):
        """
        Startet das Programm.
        """
        self.__update__()
        while not self.__done__:
            self.__update__()
        pygame.quit()

    def _setup(self):
        self.__is_setting_up__ = True
        self.setup()
        self.__is_setting_up__ = False

    def setup(self):
        """
        Sollte in deiner Kind-Klasse überschrieben werden.
        """
        pass

    def __pixel_to_cell__(self, pos: tuple):
        """
        transforms a pixel-coordinate into a cell coordinate in grid
        :param pos: the position in pixels
        """
        column = \
            (pos[0] - self._cell_margin) // (self.cell_size + self._cell_margin)
        row = \
            (pos[1] - self._cell_margin) // (self.cell_size + self._cell_margin)
        return column, row

    def cell_rect(self, cell: tuple):
        """
        Gibt das Rechteck zurück, dass eine Zelle umschließt.
        """
        x = cell[0] * self.cell_size + cell[0] * self._cell_margin + self._cell_margin
        y = cell[1] * self.cell_size + cell[1] * self._cell_margin + self._cell_margin
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def cell_to_pixel(self, cell: tuple):
        """
        Gibt die obere-linke Koordinate einer Zelle zurück.
        """
        x = cell[0] * self.cell_size + cell[0] * self._cell_margin + self._cell_margin
        y = cell[1] * self.cell_size + cell[1] * self._cell_margin + self._cell_margin
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def play_sound(self, sound_path):
        """
        Spielt einen Sound

        :param sound_path: Der Pfad zum Sound relativ zum aktuellen Verzeichnis.
        """
        effect = pygame.mixer.Sound(sound_path)
        effect.play()

    def play_music(self, music_path):
        """
        Spielt eine Musik in Endlosschleife

        :param music_path: Der Pfad zur Musikdatei relativ zum aktuellen Verzeichnis.
        """
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    def msgbox(self, message :str, choices : list) -> str:
        reply = easygui.buttonbox(message, choices=choices)
        return reply



class PixelGrid(GameGrid):
    """
    Das Pixel-Grid ist gedacht für Grids, deren Zellen genau 1 Pixel groß sind, d.h.
    für Spiele in denen Pixelgenaue Informationen wichtig sind.
    """
    def bounce(self, partner1, partner2):
        mirror_axis = (partner1.direction + partner2.direction) / 2
        self._logging.info(
            "Bouncing: actor1:" + str(partner1.direction) + ", actor2:" + str(partner2.direction) + "mirror:" + str(
                mirror_axis))
        self._logging.info(
            "Bouncing: actor2:" + str(partner2.direction) + ", actor2:" + str(partner1.direction) + "mirror:" + str(
                mirror_axis))
        self.bounce_against_line(partner1, mirror_axis)
        self.bounce_against_line(partner2, mirror_axis)

    def bounce_against_line(self, actor, line_axis):
        """
        Pralle gegen eine (gedachte) Linie mit dem angegebenen
        Winkel nach der Formel Enfallswinkel=Ausfallswinkel

        :param actor: Der Actor, der abprallt.
        :param line_axis: Der Winkel in dem die Linie steht.
            0° bezeichnet eine horizontale Linie (von links nach rechts verlaufend,
            der Winkel wird gegen den Uhrzeigersinn angegeben.

        """
        actor.direction = (line_axis * 2 - actor.direction) % 360

    def bounce_from_border(self, actor, border: str):
        """
        Pralle gegen einen Rand und ändere dabei den Winkel nach der Formel
        Einfallswinkel = Ausfallswinkel.

        :param actor: Der Actor der abprallen soll.
        :param border: Der Rand als String ("left", "right", "top", "border")

        """
        deg_mirror = 0
        if border == "top":
            deg_mirror = 0
        elif border == "bottom":
            deg_mirror = 180
        elif border == "left":
            deg_mirror = 90
        elif border == "right":
            deg_mirror = 270
        actor.direction = deg_mirror * 2 - actor.direction


class CellGrid(GameGrid):
    """
    Das Cell-Grid ist gedacht für Grids, deren Zellen größer als 1 Pixel sind.
    """
    def add_cell_image(self, img_path: str, location: tuple):
        """
        Fügt ein Bild zu einer einzelnen Zelle hinzu

        :param img_path: Der Pfad zum Bild relativ zum aktuellen Verzeichnis
        :param location: Die Zelle, die "angemalt" werden soll.
        """
        top_left = self.cell_to_pixel(location)
        cell_image = pygame.image.load(img_path).convert()
        cell_image = pygame.transform.scale(cell_image, (self.cell_size, self.cell_size))
        self._image.blit(cell_image, (top_left[0], top_left[1], self.cell_size, self.cell_size))
