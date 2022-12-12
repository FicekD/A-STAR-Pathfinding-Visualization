import pygame
import numpy as np
import math
import sys
import os

from pathfinding import AStarSolver


__author__ = "Dominik Ficek"
__license__ = "MIT"
__version__ = "1.1"
__maintainer__ = "Dominik Ficek"
__email__ = "dominik.ficek@email.cz"


RESOLUTION = 800, 600


class App:
    def __init__(self):
        self._running = True
        self.size = self.width, self.height = RESOLUTION
        self._display_surf = None
        # button bar
        self.button_height = 50
        # cursor
        self.cursor_position = (0, 0)
        # grid
        self.cols, self.rows = int(self.width / 10), int((self.height - self.button_height) / 10)
        self.color_grid = None
        # buttons
        self.font = None
        # starting and ending points
        self.start = None
        self.end = None
        # obstacles
        self.drag = False
        # phase drawing/calculating
        self.drawing = True
        self.finished = False
        # colors
        self.colors = {
            'background': [255, 255, 255, 255],
            'start': [51, 51, 255, 255],
            'end': [255, 255, 0, 255],
            'obstacle': [0, 0, 0, 255],
            'inspected': [255, 0, 0, 255],
            'path': [0, 153, 0, 255]
        }

    def init(self):
        # pygame init
        pygame.init()
        # display init
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill((128, 128, 128))
        pygame.display.set_caption("A* Pathfinding visualization")
        # grid init
        self.color_grid = np.full((self.rows, self.cols, 4), pygame.Color(255, 255, 255))
        self.font = pygame.font.SysFont(None, 30)

    def end_of_drawing_phase(self):
        self.drawing = False
        field_map = np.zeros(self.color_grid.shape[:2], dtype=np.int32)
        field_map[np.all(self.color_grid == self.colors['obstacle'], axis=-1)] = -1
        self.solver = AStarSolver(field_map, self.start, self.end)

    def clear_visuals(self):
        colors_to_keep = ['background', 'obstacle', 'start', 'end']
        for row in range(self.rows):
            for col in range(self.cols):
                if all(not np.all(self.color_grid[row, col] == self.colors[key]) for key in colors_to_keep):
                    self.color_grid[row, col] = self.colors['background']

    def cursor_pos_on_grid(self):
        return (math.floor(self.cursor_position[1] / 10), math.floor(self.cursor_position[0] / 10))

    def on_event(self, event):
        event_type = event.type
        # exit program
        if event_type == pygame.QUIT:
            self._running = False
        # drawing phase events
        elif self.drawing:
            if event_type == pygame.MOUSEMOTION:
                self.cursor_position = event.pos
                # button section
                if self.cursor_position[1] > self.height - self.button_height - 1:
                    return
                # if dragging: draw obstacles
                if self.drag:
                    self.color_grid[math.floor(event.pos[1] / 10), math.floor(event.pos[0] / 10)] = self.colors['obstacle']
            elif event_type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                # button section
                if self.cursor_position[1] > self.height - self.button_height - 1:
                    # filter out non left clicks on buttons
                    if button != 1:
                        return
                    if self.cursor_position[0] < self.width/2:
                        if self.start is not None and self.end is not None:
                            self.end_of_drawing_phase()
                    else:
                        print('wtf up')
                        self.color_grid = np.full((self.rows, self.cols, 4), pygame.Color(255, 255, 255))
                        self.start = self.end = None
                    return
                # left click: set obstacle, start dragging
                if button == 1:
                    self.color_grid[math.floor(event.pos[1] / 10), math.floor(event.pos[0] / 10)] = self.colors['obstacle']
                    self.drag = True
                # middle click: set starting point
                elif button == 2:
                    if self.start is not None:
                        self.color_grid[self.start] = self.colors['background']
                    self.start = (math.floor(event.pos[1] / 10), math.floor(event.pos[0]/10))
                    self.color_grid[self.start] = self.colors['start']
                # right click: set finish point
                elif button == 3:
                    if self.end is not None:
                        self.color_grid[self.end] = self.colors['background']
                    self.end = (math.floor(event.pos[1] / 10), math.floor(event.pos[0]/10))
                    self.color_grid[self.end] = self.colors['end']
            elif event_type == pygame.MOUSEBUTTONUP:
                button = event.button
                # left btton: stop dragging
                if button == 1:
                    self.drag = False
            elif event_type == pygame.KEYDOWN:
                key = event.key
                # delete key pressed: clear rectangle
                if key == 127:
                    position = self.cursor_pos_on_grid()
                    self.color_grid[position] = self.colors['background']
                    if position == self.start:
                        self.start = None
                    elif position == self.end:
                        self.end = None
                # space or enter key pressed: start visualization
                elif key == 13 or key == 32 or key == 271:
                    # dont start visualization if either
                    # starting or ending point is not set
                    if self.start is not None and self.end is not None:
                        self.end_of_drawing_phase()
                # escape key pressed: clear table
                elif key == 27:
                    self.color_grid = np.full((self.rows, self.cols, 4), pygame.Color(255, 255, 255))
                    self.start = self.end = None
                # s key pressed: alternate control, set starting point
                elif key == 115:
                    position = self.cursor_pos_on_grid()
                    if self.start is not None:
                        self.color_grid[self.start] = self.colors['background']
                    self.start = (math.floor(position[1]), math.floor(position[0]))
                    self.color_grid[self.start] = self.colors['start']
                # e key pressed: alternate control, set finish point
                elif key == 101:
                    position = self.cursor_pos_on_grid()
                    if self.end is not None:
                        self.color_grid[self.end] = self.colors['background']
                    self.end = math.floor(position[1]), math.floor(position[0])
                    self.color_grid[self.end] = self.colors['end']
        elif event_type == pygame.MOUSEBUTTONDOWN:
            button = event.button
            # button section
            if self.cursor_position[1] > self.height - self.button_height - 1:
                # filter out non left clicks on buttons
                if button != 1:
                    return
                if self.cursor_position[0] > self.width / 2:
                    self.drawing = True
                    self.finished = False
                    # remove all path visuals
                    self.clear_visuals()
        # escape key pressed: enter drawing phase
        elif event_type == pygame.KEYDOWN and event.key == 27:
            self.drawing = True
            self.finished = False
            # remove all path visuals
            self.clear_visuals()

    def render(self):
        # grid
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.rect(self._display_surf, self.color_grid[row, col],
                                 (10 * col - 1, 10 * row - 1, 9, 9))
        # buttons
        pygame.draw.rect(self._display_surf, pygame.Color(0x2A, 0x9D, 0x87),
                         (0, self.height - self.button_height - 1, int(self.width / 2),
                         self.height - self.button_height - 1))
        text = self.font.render('Start', True, pygame.Color(0, 0, 0))
        text_rect = text.get_rect(center=((int(self.width / 4), self.height - 25)))
        self._display_surf.blit(text, text_rect)

        pygame.draw.rect(self._display_surf, pygame.Color(0xE7, 0x6F, 0x51),
                         (int(self.width / 2), self.height - self.button_height - 1, self.width,
                         self.height - self.button_height - 1))
        text = self.font.render('Restart', True, pygame.Color(0, 0, 0))
        text_rect = text.get_rect(center=((int(3 * self.width / 4), self.height - 25)))
        self._display_surf.blit(text, text_rect)

        pygame.display.update()

    def cleanup(self):
        pygame.quit()

    def update_solver(self):
        try:
            path = self.solver.update()
            for inspected_pos in self.solver.get_inspected_positions():
                if inspected_pos == self.start or inspected_pos == self.end:
                    continue
                self.color_grid[inspected_pos] = self.colors['inspected']
            if path is not None:
                for pos in path[1:-1]:
                    self.color_grid[pos] = self.colors['path']
                self.finished = True
        except RuntimeError:
            self.finished = True

    def execute(self):
        self.init()
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            if not self.drawing and not self.finished:
                self.update_solver()
            self.render()
        self.cleanup()


def main():
    app = App()
    app.execute()


if __name__ == '__main__':
    main()
