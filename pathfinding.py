import numpy as np


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


class AStarSolver:
    def __init__(self, field_map, start, end):
        self.open_list = [Node(start)]
        self.closed_list = list()

        self.field_map = field_map
        self.start = start
        self.end = end

        self.dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.abs_distance_fn = lambda x, y: sum(abs(x_i - y_i) for x_i, y_i in zip(x, y))

    def get_inspected_positions(self):
        return [node.pos for node in self.closed_list]

    @staticmethod
    def get_node_path(node):
        positions = [node]
        while node.parent is not None:
            positions.append(node.parent.pos)
            node = node.parent
        return positions

    def update(self):
        # path not found
        if len(self.open_list) == 0:
            raise RuntimeError('Path not found')
        # find cheapest node
        current_node_idx = np.argmin([node.F for node in self.open_list])
        # remove cheapest node from open list and add it to closed list
        current_node = self.open_list.pop(current_node_idx)
        self.closed_list.append(current_node)
        # reached end
        if current_node.pos == self.end:
            # visualize final path
            return AStarSolver.get_node_path(current_node)
        # scan 8 surrounding tiles
        for (dx, dy) in self.dirs:
            new_pos = current_node.x + dx, current_node.y + dy
            # check grid boundaries
            if(new_pos[0] < 0 or new_pos[1] < 0 or
                new_pos[0] > self.field_map.shape[0] - 1 or new_pos[1] > self.field_map.shape[1] - 1):
                continue
            # check if node is on an obstacle
            if self.field_map[new_pos] == -1:
                continue
            # create new node, calculate its cost
            node = Node(new_pos, current_node)
            node.G = current_node.G + 1
            node.H = self.abs_distance_fn(node.pos, self.end)
            node.F = node.G + node.H
            # check if node is already in closed or opened list
            if node in self.closed_list or node in self.open_list:
                continue
            # add node to opened list, node can be part of a valid path
            self.open_list.append(node)
