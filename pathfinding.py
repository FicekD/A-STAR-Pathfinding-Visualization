import pygame
import numpy as np
import math


class App:
    def __init__(self):
        self._running = True
        self.size = self.width, self.height = 800, 600
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

    def init(self):
        # pygame init
        pygame.init()
        # display init
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill((128, 128, 128))
        pygame.display.set_caption("Playground")
        # grid init
        self.color_grid = np.full((self.rows, self.cols, 4), pygame.Color(255, 255, 255))

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
                    self.color_grid[math.floor(event.pos[1]/10), math.floor(event.pos[0]/10)] = [0, 0, 0, 255]
            elif event_type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                # left click: set obstacle, start dragging
                if button == 1:
                    self.color_grid[math.floor(event.pos[1]/10), math.floor(event.pos[0]/10)] = [0, 0, 0, 255]
                    self.drag = True
                # middle click: set starting point
                elif button == 2:
                    if self.start is not None:
                        self.color_grid[self.start] = [255, 255, 255, 255]
                    self.start = math.floor(event.pos[1]/10), math.floor(event.pos[0]/10)
                    self.color_grid[self.start] = [255, 51, 51, 255]
                # right click: set finish point
                elif button == 3:
                    if self.end is not None:
                        self.color_grid[self.end] = [255, 255, 255, 255]
                    self.end = math.floor(event.pos[1]/10), math.floor(event.pos[0]/10)
                    self.color_grid[self.end] = [0, 153, 0, 255]
            elif event_type == pygame.MOUSEBUTTONUP:
                button = event.button
                # left btton: stop dragging
                if button == 1:
                    self.drag = False
            elif event_type == pygame.KEYDOWN:
                key = event.key
                # delete key pressed: clear rectangle
                if key == 127:
                    position = math.floor(self.cursor_position[1]/10), math.floor(self.cursor_position[0]/10)
                    self.color_grid[position] = [255, 255, 255, 255]
                    if position == self.start:
                        self.start = None
                    elif position == self.end:
                        self.end = None
                # space or enter key pressed: stop drawing phase, start calculating
                elif key == 13 or event.key == 32:
                    # dont start caluclating if either starting or ending point is not set
                    if self.start is None or self.end is None:
                        return
                    self.drawing = False
                # escape key pressed: clear table
                elif event_type == pygame.KEYDOWN and key == 27:
                    self.color_grid = np.full((self.rows, self.cols, 4), pygame.Color(255, 255, 255))
                    self.start = self.end = None
        # escape key pressed: enter drawing phase
        elif event_type == pygame.KEYDOWN and event.key == 27:
            self.drawing = True

    def step(self):
        if self.drawing:
            return
        # calculating phase

    def render(self):
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.rect(self._display_surf, self.color_grid[row, col], (10*col - 1, 10*row - 1, 9, 9))
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


def main():
    app = App()
    app.execute()


if __name__ == '__main__':
    main()
