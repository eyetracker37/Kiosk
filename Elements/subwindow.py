from logging import log
import pygame


class Subwindow:
    child_list = []

    def __init__(self, screen):
        self.screen = screen
        pass

    def update(self):
        for child in self.child_list:
            child.update()

    def draw(self):
        for child in self.child_list:
            child.draw()
        pygame.display.flip()

    def register(self, child):
        priority = child.priority
        for idx, entry in enumerate(self.child_list):
            if entry.priority >= priority:
                self.child_list.insert(idx, child)
                return
        self.child_list.append(child)

    def unregister(self, child):
        if child in self.child_list:
            self.child_list.remove(child)


class ChildElement:
    priority = 127

    def __init__(self, parent_window):
        self.parent = parent_window
        self.screen = parent_window.screen
        parent_window.register(self)

    def close(self):
        self.parent.unregister(self)

    def update(self):
        pass

    def draw(self):
        pass
