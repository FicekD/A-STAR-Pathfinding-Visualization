import pygame
import numpy as np
import math


RESOLUTION = 800, 600


class Node:
    def __init__(self, pos, parent=None):
        self.pos = self.x, self.y = pos
        self.parent = parent
        # squared distance from start
        self.G = 0
        # squared distance from end
        self.H = 0
        # total cost of the node
        self.F = 0

    def __eq__(self, other):
        return self.pos == other.pos


class App:
    def __init__(self):
        self._running = True
        self.size = self.width, self.height = RESOLUTION
        self._display_surf = None
        # cursor
        self.cursor_position = (0, 0)
        # grid
        self.cols, self.rows = int(self.width/10), int(self.height/10)
        self.color_grid = None
        # starting and ending points
        self.start = None
        self.end = None
        # obstacles
        self.drag = False
        # phase drawing/calculating
        self.drawing = True
        # pathfinding
        self.open_list = list()
        self.closed_list = list()
        self.finished = False

    def init(self):
        # pygame init
        pygame.init()
        # display init
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill((128, 128, 128))
        pygame.display.set_caption(
            "A* Pathfinding visualization by Dominik Ficek")
        # grid init
        self.color_grid = np.full(
            (self.rows, self.cols, 4), pygame.Color(255, 255, 255))

    def on_event(self, event):
        event_type = event.type
        # exit program
        if event_type == pygame.QUIT:
            self._running = False
        # drawing phase events
        elif self.drawing:
            if event_type == pygame.MOUSEMOTION:
                self.cursor_position = event.pos
                # if dragging: draw obstacles
                if self.drag:
                    self.color_grid[
                        math.floor(event.pos[1]/10),
                        math.floor(event.pos[0]/10)] = [0, 0, 0, 255]
            elif event_type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                # left click: set obstacle, start dragging
                if button == 1:
                    self.color_grid[
                        math.floor(event.pos[1]/10),
                        math.floor(event.pos[0]/10)] = [0, 0, 0, 255]
                    self.drag = True
                # middle click: set starting point
                elif button == 2:
                    if self.start is not None:
                        self.color_grid[self.start] = [255, 255, 255, 255]
                    self.start = (math.floor(event.pos[1]/10),
                                  math.floor(event.pos[0]/10))
                    self.color_grid[self.start] = [51, 51, 255, 255]
                # right click: set finish point
                elif button == 3:
                    if self.end is not None:
                        self.color_grid[self.end] = [255, 255, 255, 255]
                    self.end = (math.floor(event.pos[1]/10),
                                math.floor(event.pos[0]/10))
                    self.color_grid[self.end] = [255, 255, 0, 255]
            elif event_type == pygame.MOUSEBUTTONUP:
                button = event.button
                # left btton: stop dragging
                if button == 1:
                    self.drag = False
            elif event_type == pygame.KEYDOWN:
                key = event.key
                # delete key pressed: clear rectangle
                if key == 127:
                    position = (math.floor(self.cursor_position[1]/10),
                                math.floor(self.cursor_position[0]/10))
                    self.color_grid[position] = [255, 255, 255, 255]
                    if position == self.start:
                        self.start = None
                    elif position == self.end:
                        self.end = None
                # space or enter key pressed: start visualization
                elif key == 13 or key == 32 or key == 271:
                    # dont start visualization if either
                    # starting or ending point is not set
                    if self.start is None or self.end is None:
                        return
                    self.open_list.append(Node(self.start))
                    self.drawing = False
                # escape key pressed: clear table
                elif key == 27:
                    self.color_grid = np.full((self.rows, self.cols, 4),
                                              pygame.Color(255, 255, 255))
                    self.start = self.end = None
                # s key pressed: alternate control, set starting point
                elif key == 115:
                    position = (math.floor(
                        self.cursor_position[0]/10),
                        math.floor(self.cursor_position[1]/10))
                    if self.start is not None:
                        self.color_grid[self.start] = [255, 255, 255, 255]
                    self.start = (math.floor(position[1]),
                                  math.floor(position[0]))
                    self.color_grid[self.start] = [51, 51, 255, 255]
                # e key pressed: alternate control, set finish point
                elif key == 101:
                    position = (math.floor(self.cursor_position[0]/10),
                                math.floor(self.cursor_position[1]/10))
                    if self.end is not None:
                        self.color_grid[self.end] = [255, 255, 255, 255]
                    self.end = math.floor(position[1]), math.floor(position[0])
                    self.color_grid[self.end] = [255, 255, 0, 255]
        # escape key pressed: enter drawing phase
        elif event_type == pygame.KEYDOWN and event.key == 27:
            self.drawing = True
            self.finished = False
            self.closed_list = list()
            self.open_list = list()
            # remove all path visuals
            for row in range(self.rows):
                for col in range(self.cols):
                    if (not np.array_equal(self.color_grid[row, col],
                                           [255, 255, 255, 255]) and
                        not np.array_equal(self.color_grid[row, col],
                                           [0, 0, 0, 255]) and
                        not np.array_equal(self.color_grid[row, col],
                                           [51, 51, 255, 255]) and
                        not np.array_equal(self.color_grid[row, col],
                                           [255, 255, 0, 255])):
                        self.color_grid[row, col] = [255, 255, 255, 255]

    def step(self):
        # drawing phase
        if self.drawing or self.finished:
            return
        # calculating phase
        start = self.start
        end = self.end
        # path not found
        if len(self.open_list) == 0:
            self.finished = True
            return
        # find cheapest node
        current_node = self.open_list[0]
        index = 0
        for i, node in enumerate(self.open_list):
            if node.F < current_node.F:
                current_node = node
                index = i
        # remove cheapest node from open list and add it to closed list
        self.open_list.pop(index)
        self.closed_list.append(current_node)
        # visualize path
        if current_node.pos != start and current_node.pos != end:
            self.color_grid[current_node.pos] = [255, 0, 0, 255]
        # reached end
        if current_node.pos == end:
            self.finished = True
            # visualize final path
            current = current_node.parent
            while current is not None and current.pos != start:
                self.color_grid[current.pos] = [0, 153, 0, 255]
                current = current.parent
        # scan 8 surrounding tiles
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                new_pos = current_node.x + i, current_node.y + j
                # check grid boundaries
                if(new_pos[0] < 0 or new_pos[1] < 0 or
                   new_pos[0] > self.rows - 1 or new_pos[1] > self.cols - 1):
                    continue
                # create new node, calculate its cost
                node = Node(new_pos, current_node)
                node.G = current_node.G + 1
                node.H = distance(node.pos, end)
                node.F = node.G + node.H
                # check if node is already in closed list
                cont = False  # nested loop continue flag
                for node_i in self.closed_list:
                    if node_i == node:
                        cont = True
                        break
                if cont:
                    continue
                # check if node is already in opened list
                for node_i in self.open_list:
                    if node_i == node:
                        cont = True
                        break
                if cont:
                    continue
                # check if node is on an obstacle
                if np.array_equal(self.color_grid[node.pos],
                                  np.array([0, 0, 0, 255])):
                    continue
                # add node to opened list, node can be part of a valid path
                self.open_list.append(node)

    def render(self):
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.rect(self._display_surf, self.color_grid[row, col],
                                 (10*col - 1, 10*row - 1, 9, 9))
        pygame.display.update()

    def cleanup(self):
        pygame.quit()

    def execute(self):
        self.init()
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.step()
            self.render()
        self.cleanup()


def distance(pos1, pos2):
    return (((pos1[0] - pos2[0]) ** 2) + ((pos1[1] - pos2[1]) ** 2))


def main():
    app = App()
    app.execute()


if __name__ == '__main__':
    main()
