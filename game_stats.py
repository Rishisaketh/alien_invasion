class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """intialize statistics"""

        self.settings = ai_game.settings

        # High score should never be reset
        self.high_score = 0
        self.level = 0
        self.reset_stats()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""

        self.ships_left = self.settings.ship_limit
        self.score = 0

        self.alien_left = self.settings.aliens_limit


        