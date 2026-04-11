import random

class MovementSimulator:
    def __init__(self):
        self.moving = False

    def is_user_moving(self):
        # Change state occasionally (not every loop)
        if random.random() > 0.8:
            self.moving = not self.moving
        return self.moving