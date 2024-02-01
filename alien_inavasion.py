import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard



class AlienInvasion:
    """overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game and create game resourrces."""

        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
    
        
        pygame.display.set_caption("Alien Invasion Game By rishi")

        self.ship = Ship(self)
        self.ship.resize((80, 80))  # Set the desired size (width, height)
        
        # Create an instance to store game statistics.
        # Create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        

        self._create_fleet()

        #set the background colour 
        self.bg_color = self.settings.bg_color

        # Start Alien Invasion in an active state.
        self.game_active = True

        # Make the Play button.
        self.play_button = Button(self, "Play")

        # Start Alien Invasion in an inactive state.
        self.game_active = False

        self.game_paused = False
        
        self.bullet_timer = pygame.time.get_ticks()  # Initialize the bullet timer



    def run_game(self):
        """start the main loop for the game."""

        while True:
            
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         sys.exit()

            # # Redraw the screen during each pass through the loop.
            # self.screen.fill(self.bg_color)

            # self.ship.blitme()

            # # Make the most recently drawn screen visible.
            # pygame.display.flip()

            self._check_events()

            if self.game_active:
                self.ship.update()

                self._update_aliens()
                # print(len(self.bullets))
                self._update_bullets()
            self._update_screen()
            self.clock.tick(60)


    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self,event):
        
        if event.key == pygame.K_RIGHT:
            # move the ship to the right.
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            # self._fire_bullet()
            # self._fire_ship_bullet()
            if not self.game_active:
                self._start_game()
            else:
                self._fire_bullet()

    def _start_game(self):
        """Start the game."""
        self.game_active = True
        self.game_paused = False

        # Reset game statistics
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # Get rid of any remaining bullets and aliens.
        self.bullets.empty()
        self.aliens.empty()

        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()

        # Reset the game settings.
        self.settings.initialize_dynamic_settings()

        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)


    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
        # if not self.game_paused and len(self.bullets) < self.settings.bullets_allowed:
        #     new_bullet = Bullet(self)
        #     self.bullets.add(new_bullet)
            
            # Create and add alien bullets
            for alien in self.aliens.sprites():
                new_alien_bullet = Bullet(self, is_alien_bullet=True)
                new_alien_bullet.rect.x = alien.rect.x
                new_alien_bullet.rect.y = alien.rect.y
                self.bullets.add(new_alien_bullet)

    
    # Add this method to the AlienInvasion class
    def _fire_ship_bullet(self):
        """Create a new bullet for the ship and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            new_bullet.rect.centerx = self.ship.rect.centerx
            new_bullet.rect.top = self.ship.rect.top
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """update position of bullets and get rid of old bullets"""
        current_time = pygame.time.get_ticks()

        self.bullets.update()
        self._check_bullet_alien_collisions()
        self._check_ship_bullet_collisions()  # Add this line
        
        # Check ship bullet firing every 250 milliseconds (adjust the interval as needed)
        if current_time - self.bullet_timer > 250:
            self._fire_bullet()
            self.bullet_timer = current_time

        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0 or bullet.rect.top >= self.settings.screen_height:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
        self._check_ship_bullet_collisions()
    

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

    def _check_ship_bullet_collisions(self):
        """Check for collisions between the ship and alien bullets."""
        collisions = pygame.sprite.spritecollide(self.ship, self.bullets, True)

        if collisions:
            print("Ship hit by alien bullet!!!")
            self._ship_hit()


    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet() 
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Draw the score information
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.game_active or self.game_paused:
            self.play_button.draw_button()

        pygame.display.flip()

    def _create_fleet(self):
        """Create the fleet of aliens."""

        # make an alien.
        alien = Alien(self)
        # self.aliens.add(alien)
        alien_width = alien.rect.width
        alien_height = alien.rect.height

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):

            while current_x < (self.settings.screen_width - 2 * alien_width):
                new_alien = Alien(self)
                new_alien.x = current_x
                new_alien.rect.x = current_x
                new_alien.rect.y = current_y
                self.aliens.add(new_alien)
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            
            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row"""

        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""  
        self._check_fleet_edges()      
        self.aliens.update()
        self._check_aliens_bottom()

        # look for alien ship collision 
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            print("Ship hit!!!")
            self._ship_hit()

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge.""" 
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """respond to the ship being by alien"""

        if self.stats.ships_left > 0:

            # decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # pause
            sleep(0.5)

        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # treat this the same as if the ship got hit
                self._ship_hit()
                break

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""

        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:            
            # reset the game statistics
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # create a new fleet and center the ship
            self._create_fleet
            self.ship.center_ship()

            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)


if __name__ == '__main__':

    ai = AlienInvasion()
    ai.run_game()

