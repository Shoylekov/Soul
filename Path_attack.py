import random
import pygame
import math

class BossAttack:
    def __init__(self, boss, arena_rect):
        self.boss = boss
        self.arena_rect = arena_rect
        self.damage_sound = pygame.mixer.Sound("assets/music/damage_sound.mp3")
        
        # Define the attack order here (example):
        self.phase1_attacks = ['other_attack', 'path_spears', 'attack3']
        self.phase2_attacks = ['shadowfall_barrage', 'rotating_laser', 'shockwave_pulse']
        self.phase3_attacks = ['shadowfall_barrage', 'path_spears', 'other_attack']
        self.phase4_attacks = ['attack3', 'rotating_laser', 'wall_attack']
        self.phase5_attacks = ['attack3', 'shockwave_pulse', 'wall_attack']
        self.phase6_attacks = ['other_attack', 'shadowfall_barrage', 'rotating_laser']
        self.phase7_attacks = ['wall_attack', 'shockwave_pulse', 'wall_attack']
        self.current_phase = 1
        self.attack_order = self.phase1_attacks
        self.current_attack_index = 0
        self.current_attack_in_progress = False

        # ========== For path_spears attack ==========
        self.spears = []
        self.spears_start_time = None
        self.spears_finished_time = None
        self.spear_damage_cooldown = 300
        self.safe_margin = 30

        self.spear_image = pygame.image.load("assets/sheets/spear.png").convert_alpha()
        # If needed, scale the image to match your spear dimensions.
        self.spear_width = 10
        self.spear_height = 30
        self.spear_image = pygame.transform.scale(self.spear_image, (self.spear_width, self.spear_height))

        # ========== For other_attack (giant blaster beams) ==========
        self.blaster_beams = []  # Will store the two diagonal beams
        self.blaster_damage_cooldown = 300  # 0.3s cooldown
        self.other_attack_active = False

        # ========== For attack3 (fast scythes) ==========
        self.scythes = []                  # will store each scythe
        self.scythe_damage_cooldown = 300  # 0.3s between hits per scythe
        self.scythe_attack_start_time = 0  # time when attack starts
        self.scythe_attack_duration = 2600 # how long the scythes stay on screen (ms)
        # Load scythe images
        self.scythe_image = pygame.image.load("assets/sheets/scythe.png").convert_alpha()
        self.scythe_image_flipped = pygame.transform.flip(self.scythe_image, True, False)

        # ========== For Shadowfall barrage ==========
        self.shadowfall_projectiles = []
        self.shadowfall_attack_active = False

         # ========== For Rotating Laser attack ==========
        self.rotating_laser_active = False

        # ========== For Shockwave pulse attack ==========
        self.shockwave_active = False

        # ========== Wall attack ==========
        self.current_wall_index = 0  # Track the current wall being moved
        self.wall_attack_active = False
        self.wall_move_duration = 1500  # Duration for each wall to move
        self.gap_size = 50
        self.walls = []

        self.all_attacks_completed = False  # Reset the flag
        
    def reset_attacks(self):
        """Resets the attack sequence to allow choosing an action again."""
        self.current_attack_index = 0
        self.current_attack_in_progress = False
        self.spears = []
        self.blaster_beams = []
        self.scythes = []
        self.other_attack_active = False
        self.spears_start_time = None
        self.spears_finished_time = None
        self.scythe_attack_start_time = 0
        self.all_attacks_completed = False 

    def perform_next_attack(self, target):
        """Starts the next attack in the attack_order list."""
        if self.current_attack_index < len(self.attack_order):
            attack = self.attack_order[self.current_attack_index]
            print(f"[DEBUG] Starting attack: {attack}, current_phase: {self.current_phase}, current_attack_index: {self.current_attack_index}")
            if attack == 'path_spears':
                self.path_spears(target)
            elif attack == 'other_attack':
                self.other_attack(target)
            elif attack == 'attack3':
                self.attack3(target)
            elif attack == 'shadowfall_barrage':
                self.shadowfall_barrage_attack(target)
            elif attack == 'rotating_laser':
                self.rotating_laser_attack(target)
            elif attack == 'shockwave_pulse':
                self.shockwave_pulse_attack(target)
            elif attack == 'wall_attack':
                self.wall_attack(target)
            self.current_attack_in_progress = True
        else:
            print(f"[DEBUG] All attacks completed. current_phase: {self.current_phase}, current_attack_index: {self.current_attack_index}")
            self.all_attacks_completed = True

    def proceed_to_next_phase(self):
        """Proceeds to the next phase of attacks."""
        if self.current_phase == 1:
            self.current_phase = 2
            self.attack_order = self.phase2_attacks
            self.reset_attacks()
        elif self.current_phase == 2:
            self.current_phase = 3
            self.attack_order = self.phase3_attacks
            self.reset_attacks()
        elif self.current_phase == 3:
            self.current_phase = 4
            self.attack_order = self.phase4_attacks
            self.reset_attacks()
        elif self.current_phase == 4:
            self.current_phase = 5
            self.attack_order = self.phase5_attacks
            self.reset_attacks()
        elif self.current_phase == 5:
            self.current_phase = 6
            self.attack_order = self.phase6_attacks
            self.reset_attacks()
        elif self.current_phase == 6:
            self.current_phase = 7
            self.attack_order = self.phase7_attacks
            self.reset_attacks()
        
    # ------------------------------------------------------------------
    #                         OTHER ATTACK (X BLASTERS)
    # ------------------------------------------------------------------
    def other_attack(self, target):
        """
        Spawns two giant diagonal beams that form an X:
         1) From top-left to bottom-right
         2) From top-right to bottom-left

        Each beam has:
         - A telegraph phase (thin line)
         - An active phase (thick beam dealing damage)
         - Then disappears
        """
        current_time = pygame.time.get_ticks()

        # Beam parameters
        telegraph_delay = 600  # ms before the beam becomes active
        active_duration = 2000  # ms the beam remains active
        beam_thickness = 100     # thickness during the active phase

        # 1) Top-left to bottom-right
        beam1 = {
            'start': (self.arena_rect.left, self.arena_rect.top),
            'end': (self.arena_rect.right, self.arena_rect.bottom),
            'delay': current_time + telegraph_delay,
            'end_time': current_time + telegraph_delay + active_duration,
            'thickness': beam_thickness,
            'last_hit_time': 0
        }

        # 2) Top-right to bottom-left
        beam2 = {
            'start': (self.arena_rect.right, self.arena_rect.top),
            'end': (self.arena_rect.left, self.arena_rect.bottom),
            'delay': current_time + telegraph_delay,
            'end_time': current_time + telegraph_delay + active_duration,
            'thickness': beam_thickness,
            'last_hit_time': 0
        }

        self.blaster_beams = [beam1, beam2]
        self.other_attack_active = True
        print("Created X blaster beams.")

    # Helper function to measure distance from point to line segment
    def point_to_segment_distance(self, px, py, x1, y1, x2, y2):
        seg_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if seg_len_sq == 0:
            # Start and end are the same point
            return math.hypot(px - x1, py - y1)
        # Projection factor
        t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / seg_len_sq
        t = max(0, min(1, t))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return math.hypot(px - proj_x, py - proj_y)

    # ------------------------------------------------------------------
    #                         PATH SPEARS ATTACK
    # ------------------------------------------------------------------
    def path_spears(self, target):
        # Same code you used for the cage attack
        spear_width = 10
        spear_height = 30

        for y in range(self.arena_rect.top, self.arena_rect.bottom, spear_height + 10):
            spear_rect_left = pygame.Rect(self.arena_rect.left - spear_width, y, spear_width, spear_height)
            self.spears.append({'rect': spear_rect_left, 'direction': 'right', 'last_hit_time': 0})
            spear_rect_right = pygame.Rect(self.arena_rect.right, y, spear_width, spear_height)
            self.spears.append({'rect': spear_rect_right, 'direction': 'left', 'last_hit_time': 0})

        for x in range(self.arena_rect.left, self.arena_rect.right, spear_width + 10):
            spear_rect_top = pygame.Rect(x, self.arena_rect.top - spear_height, spear_width, spear_height)
            self.spears.append({'rect': spear_rect_top, 'direction': 'down', 'last_hit_time': 0})
            spear_rect_bottom = pygame.Rect(x, self.arena_rect.bottom, spear_width, spear_height)
            self.spears.append({'rect': spear_rect_bottom, 'direction': 'up', 'last_hit_time': 0})

        self.spears_start_time = pygame.time.get_ticks()
        self.spears_finished_time = None
        print("Path spears attack created.")

    # ------------------------------------------------------------------
    #                         OTHER ATTACKS (PLACEHOLDERS)
    # ------------------------------------------------------------------
    def attack3(self, target):
        """
        Spawns scythes around the edges (or outside) of the arena at random angles.
        Each scythe flies quickly toward the player's position at the time of spawning.
        """
        print("Executing attack3: fast scythes!")

        # 1. Clear any old scythes and set up timers
        self.scythes.clear()
        self.scythe_attack_start_time = pygame.time.get_ticks()

        # 2. How many scythes to spawn, how fast they move
        scythe_count = 3
        scythe_speed = 6  # fast movement
        radius = max(self.arena_rect.width, self.arena_rect.height) // 2 + 100

        # 3. Spawn scythes at random angles around the center
        center_x = self.arena_rect.centerx
        center_y = self.arena_rect.centery
        player_x, player_y = target.soul_collision_rect.center

        for _ in range(scythe_count):
            # Random angle [0, 2π)
            angle = random.uniform(0, 2 * math.pi)

            # Spawn position on a circle outside the arena
            spawn_x = center_x + radius * math.cos(angle)
            spawn_y = center_y + radius * math.sin(angle)

            # Direction toward player's position (at spawn time)
            dx = player_x - spawn_x
            dy = player_y - spawn_y
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist

            # Scythe dictionary
            scythe = {
                'rect': pygame.Rect(spawn_x, spawn_y, 32, 32),  # size of the scythe (adjust as needed)
                'velocity': (dx * scythe_speed, dy * scythe_speed),
                'last_hit_time': 0  # track damage cooldown
            }
            self.scythes.append(scythe)

        # 4. Mark this attack as active
        self.current_attack_in_progress = True
        print(f"Spawned {scythe_count} scythes for attack3.")

    # ------------------------------------------------------------------
    #             Phase 2 of the boss fight (Shadowfall Barrage)
    # ------------------------------------------------------------------
    def shadowfall_barrage_attack(self, target):
        """
        Initiates the Shadowfall Barrage, a two-phase attack:
        1) Downward Barrage: A series of projectiles rain down from the top of the arena,
            leaving alternating safe gaps for the player.
        2) Lateral Barrage: Projectiles enter from the left and right sides,
            further constricting the arena with narrow safe zones.

        Each projectile undergoes:
        - A telegraph phase (the location is indicated before it becomes active)
        - An active phase (it moves and can damage the player)
        """
        current_time = pygame.time.get_ticks()

        # Timing parameters (in milliseconds)
        telegraph_delay = 600      # Delay before projectiles become active
        active_duration = 2000     # Duration the projectiles remain active

        # ---------------------------
        # Phase 1: Downward Barrage
        # ---------------------------
        num_columns = 8  # Divide arena width into 8 columns
        column_width = self.arena_rect.width / num_columns
        projectile_speed_down = 5  # Speed (pixels per frame) for downward-moving projectiles

        downward_projectiles = []
        # Spawn projectiles in alternate columns to create safe gaps
        for i in range(num_columns):
            if i % 2 == 0:  # Only in even columns (0-indexed)
                x_pos = self.arena_rect.left + i * column_width + column_width / 2
                y_pos = self.arena_rect.top  # Start at the top edge of the arena
                projectile = {
                    'position': [x_pos, y_pos],
                    'velocity': [0, projectile_speed_down],
                    'telegraph_end_time': current_time + telegraph_delay,
                    'active_end_time': current_time + telegraph_delay + active_duration,
                    'type': 'downward'
                }
                downward_projectiles.append(projectile)

        # ---------------------------
        # Phase 2: Lateral Barrage
        # ---------------------------
        num_rows = 6  # Divide arena height into 6 rows
        row_height = self.arena_rect.height / num_rows
        projectile_speed_side = 5  # Speed for side-moving projectiles

        lateral_projectiles = []
        # Spawn projectiles from the left on even rows and from the right on odd rows
        for j in range(num_rows):
            y_pos = self.arena_rect.top + j * row_height + row_height / 2
            if j % 2 == 0:
                # Projectile from the left moving rightwards
                x_pos_left = self.arena_rect.left
                projectile_left = {
                    'position': [x_pos_left, y_pos],
                    'velocity': [projectile_speed_side, 0],
                    'telegraph_end_time': current_time + telegraph_delay,
                    'active_end_time': current_time + telegraph_delay + active_duration,
                    'type': 'lateral_left'
                }
                lateral_projectiles.append(projectile_left)
            else:
                # Projectile from the right moving leftwards
                x_pos_right = self.arena_rect.right
                projectile_right = {
                    'position': [x_pos_right, y_pos],
                    'velocity': [-projectile_speed_side, 0],
                    'telegraph_end_time': current_time + telegraph_delay,
                    'active_end_time': current_time + telegraph_delay + active_duration,
                    'type': 'lateral_right'
                }
                lateral_projectiles.append(projectile_right)

        # Combine both phases into one list of active projectiles
        self.shadowfall_projectiles = downward_projectiles + lateral_projectiles
        self.shadowfall_attack_active = True
        print("Shadowfall Barrage initiated.")


    
    def rotating_laser_attack(self, target):
        """
        Initiates the Rotating Laser attack:
        A laser beam originates from the arena center and rotates continuously.
        It has two phases:
        - Telegraph Phase: The beam is drawn thin (e.g. red) as a warning.
        - Active Phase: The beam thickens (e.g. white) and damages the player on contact.
        """
        current_time = pygame.time.get_ticks()
        
        # Timing parameters (in milliseconds)
        telegraph_delay = 500      # Delay before beam becomes active
        active_duration = 2500     # How long the active phase lasts

        # Define the rotating laser beam.
        # The beam originates from the arena center and extends outward.
        # Its angle will update in the main update loop.
        self.rotating_laser = {
            'center': (self.arena_rect.centerx, self.arena_rect.centery),
            'angle': 0,                    # Starting angle (in degrees)
            'rotation_speed': 4,           # Degrees per update call
            'telegraph_end_time': current_time + telegraph_delay,
            'active_end_time': current_time + telegraph_delay + active_duration,
            'thickness': 20,                # Thickness during active phase
            'beam_length': max(self.arena_rect.width, self.arena_rect.height)
        }
        self.rotating_laser_active = True
        print("Rotating Laser attack initiated.")

    def shockwave_pulse_attack(self, target):
        """
        Initiates the Shockwave Pulse attack:
        The boss sends out an expanding shockwave from the arena center.
        The attack has two phases:
        1) Telegraph Phase: A small circle appears at the arena center.
        2) Active Phase: The circle expands rapidly; if the shockwave’s edge
            intersects the player, damage is applied.
        """
        current_time = pygame.time.get_ticks()

        # Timing parameters (in milliseconds)
        telegraph_delay = 800       # Duration of telegraph phase
        active_duration = 1500      # Duration of the active (expansion) phase

        initial_radius = 20         # Starting radius during telegraph phase
        max_radius = self.arena_rect.width - 145  # Maximum expansion (adjust as needed)
        expansion_rate = (max_radius - initial_radius) / active_duration  # pixels per ms

        self.shockwave = {
            'center': (self.arena_rect.centerx, self.arena_rect.centery),
            'telegraph_end_time': current_time + telegraph_delay,
            'active_end_time': current_time + telegraph_delay + active_duration,
            'initial_radius': initial_radius,
            'current_radius': initial_radius,
            'expansion_rate': expansion_rate,
            'phase': 'telegraph'  # Starts in telegraph phase
        }
        self.shockwave_active = True
        print("Shockwave Pulse attack initiated.")
    
    def wall_attack(self, target):
        """
        Initiates the Wall Attack:
        1) Right wall moves leftward, leaving a small gap.
        2) Left wall moves rightward, leaving a small gap.
        3) Bottom wall moves upward, leaving a small gap.
        4) Top wall moves downward, completing the cycle.
        """
        current_time = pygame.time.get_ticks()

        self.walls = [
            {'rect': pygame.Rect(self.arena_rect.right, self.arena_rect.top, 10, self.arena_rect.height), 
            'direction': 'left', 'start_time': current_time, 'last_hit_time': 0},
            {'rect': pygame.Rect(self.arena_rect.left - 10, self.arena_rect.top, 10, self.arena_rect.height), 
            'direction': 'right', 'start_time': current_time + self.wall_move_duration, 'last_hit_time': 0},
            {'rect': pygame.Rect(self.arena_rect.left, self.arena_rect.bottom, self.arena_rect.width, 10), 
            'direction': 'up', 'start_time': current_time + 2 * self.wall_move_duration, 'last_hit_time': 0},
            {'rect': pygame.Rect(self.arena_rect.left, self.arena_rect.top - 10, self.arena_rect.width, 10), 
            'direction': 'down', 'start_time': current_time + 3 * self.wall_move_duration, 'last_hit_time': 0}
        ]

        self.current_wall_index = 0  # Reset the current wall index
        self.wall_attack_active = True
        print("Wall attack initiated.")
        
    
    # ------------------------------------------------------------------
    #                          MAIN UPDATE
    # ------------------------------------------------------------------
    def update(self, target, player_health):
        """
        Updates whichever attack is currently active.
        If no attack is active, starts the next one in the list.
        """
        current_time = pygame.time.get_ticks()

        # If no attack is in progress and not all attacks are completed, start the next one
        if not self.current_attack_in_progress and not self.all_attacks_completed:
            self.perform_next_attack(target)

        # Identify the current attack
        if self.current_attack_index < len(self.attack_order):
            current_attack = self.attack_order[self.current_attack_index]
        else:
            current_attack = None

        # Handle "other_attack" (the X blaster beams)
        if current_attack == 'other_attack' and self.other_attack_active:
            # For each beam, check if we're in telegraph or active phase
            beams_done = True  # We’ll check if all beams are done

            for beam in self.blaster_beams:
                delay_time = beam['delay']
                end_time = beam['end_time']

                if current_time < end_time:
                    beams_done = False  # At least one beam is still active
                else:
                    continue  # This beam has finished

                # Collision is only checked if we're past the delay (active phase)
                if current_time >= delay_time:
                    # The beam is active, do collision
                    # Check multiple points on the player's collision rect
                    thickness = beam['thickness']
                    half_thickness = thickness / 2
                    tolerance = 5  # Add a tolerance value for collision
                    # For robust collision, check the rect corners + center
                    points_to_check = [
                        target.soul_collision_rect.center,
                        target.soul_collision_rect.topleft,
                        target.soul_collision_rect.topright,
                        target.soul_collision_rect.bottomleft,
                        target.soul_collision_rect.bottomright,
                    ]

                    (x1, y1) = beam['start']
                    (x2, y2) = beam['end']

                    for point in points_to_check:
                        dist = self.point_to_segment_distance(point[0], point[1], x1, y1, x2, y2)
                        if dist < half_thickness + tolerance:
                            # If within beam thickness + tolerance, deal damage
                            if current_time - beam['last_hit_time'] >= self.blaster_damage_cooldown:
                                print("Player hit by X blaster beam!")
                                self.damage_sound.play()
                                player_health -= 7
                                beam['last_hit_time'] = current_time
                            break  # No need to check other points this frame

            # If all beams are done, proceed to next attack
            if beams_done:
                print("X blaster beams attack finished.")
                self.blaster_beams = []
                self.other_attack_active = False
                self.current_attack_in_progress = False
                self.current_attack_index += 1

        # Handle "path_spears" attack
        elif current_attack == 'path_spears' and len(self.spears) > 0:
            # Start moving the spears after 1 second
            if self.spears_start_time and current_time - self.spears_start_time > 850:
                for spear in self.spears:
                    if spear['direction'] == 'right':
                        spear['rect'].x += 5
                        if spear['rect'].x >= self.arena_rect.centerx - spear['rect'].width - self.safe_margin:
                            spear['rect'].x = self.arena_rect.centerx - spear['rect'].width - self.safe_margin
                    elif spear['direction'] == 'left':
                        spear['rect'].x -= 5
                        if spear['rect'].x <= self.arena_rect.centerx + self.safe_margin:
                            spear['rect'].x = self.arena_rect.centerx + self.safe_margin
                    elif spear['direction'] == 'down':
                        spear['rect'].y += 5
                        if spear['rect'].y >= self.arena_rect.centery - spear['rect'].height - self.safe_margin:
                            spear['rect'].y = self.arena_rect.centery - spear['rect'].height - self.safe_margin
                    elif spear['direction'] == 'up':
                        spear['rect'].y -= 5
                        if spear['rect'].y <= self.arena_rect.centery + self.safe_margin:
                            spear['rect'].y = self.arena_rect.centery + self.safe_margin

            # Collision detection
            for spear in self.spears:
                if spear['rect'].colliderect(target.soul_collision_rect):
                    if current_time - spear['last_hit_time'] >= self.spear_damage_cooldown:
                        print("Player hit by spear!")
                        self.damage_sound.play()
                        player_health -= 7
                        spear['last_hit_time'] = current_time

            # Check if all spears have reached destination
            all_stopped = True
            for spear in self.spears:
                if spear['direction'] == 'right' and spear['rect'].x < self.arena_rect.centerx - spear['rect'].width - self.safe_margin:
                    all_stopped = False
                elif spear['direction'] == 'left' and spear['rect'].x > self.arena_rect.centerx + self.safe_margin:
                    all_stopped = False
                elif spear['direction'] == 'down' and spear['rect'].y < self.arena_rect.centery - spear['rect'].height - self.safe_margin:
                    all_stopped = False
                elif spear['direction'] == 'up' and spear['rect'].y > self.arena_rect.centery + self.safe_margin:
                    all_stopped = False

            if all_stopped:
                # Start a hold timer if not started
                if self.spears_finished_time is None:
                    self.spears_finished_time = current_time
                elif current_time - self.spears_finished_time >= 1500:
                    # Clear spears and move to next attack
                    self.spears = []
                    self.spears_start_time = None
                    self.spears_finished_time = None
                    self.current_attack_in_progress = False
                    self.current_attack_index += 1

        elif current_attack == 'attack3' and len(self.scythes) > 0:
            # 1) Move each scythe
            for scythe in self.scythes:
                vx, vy = scythe['velocity']
                scythe['rect'].x += vx
                scythe['rect'].y += vy

                # 2) Check collision with the player
                if scythe['rect'].colliderect(target.soul_collision_rect):
                    if current_time - scythe['last_hit_time'] >= self.scythe_damage_cooldown:
                        print("Player hit by scythe!")
                        self.damage_sound.play()
                        player_health -= 7
                        scythe['last_hit_time'] = current_time

            # 3) End the attack after a certain duration
            if current_time - self.scythe_attack_start_time >= self.scythe_attack_duration:
                # Clear scythes, mark attack as finished
                self.scythes.clear()
                self.current_attack_in_progress = False
                self.current_attack_index += 1
                print("Scythe attack finished.")

        elif current_attack == 'shadowfall_barrage' and self.shadowfall_attack_active:
            for proj in self.shadowfall_projectiles:
                if current_time < proj['telegraph_end_time']:
                    continue  # Still in telegraph phase
                elif proj['telegraph_end_time'] <= current_time < proj['active_end_time']:
                    # Move the projectile
                    proj['position'][0] += proj['velocity'][0]
                    proj['position'][1] += proj['velocity'][1]

                    # Check collision with the player
                    if target.soul_collision_rect.collidepoint(proj['position']):
                        print("Player hit by Shadowfall projectile!")
                        self.damage_sound.play()
                        player_health -= 7
                        proj['active_end_time'] = current_time  # End this projectile's active phase

            # Remove projectiles that have finished their active phase
            self.shadowfall_projectiles = [proj for proj in self.shadowfall_projectiles if current_time < proj['active_end_time']]

            # If all projectiles are done, proceed to next attack
            if not self.shadowfall_projectiles:
                print("Shadowfall Barrage attack finished.")
                self.shadowfall_attack_active = False
                self.current_attack_in_progress = False
                self.current_attack_index += 1

        elif current_attack == 'rotating_laser' and self.rotating_laser_active:
            current_time = pygame.time.get_ticks()
            laser = self.rotating_laser
            # Update the laser's rotation angle
            laser['angle'] = (laser['angle'] + laser['rotation_speed']) % 360
            
            # Calculate the laser beam's line segment
            center = laser['center']
            angle_rad = math.radians(laser['angle'])
            end_x = center[0] + laser['beam_length'] * math.cos(angle_rad)
            end_y = center[1] + laser['beam_length'] * math.sin(angle_rad)
            
            # Check for collision with the player only if past telegraph phase
            if current_time >= laser['telegraph_end_time']:
                points_to_check = [
                    target.soul_collision_rect.center,
                    target.soul_collision_rect.topleft,
                    target.soul_collision_rect.topright,
                    target.soul_collision_rect.bottomleft,
                    target.soul_collision_rect.bottomright,
                ]
                
                for point in points_to_check:
                    dist = self.point_to_segment_distance(point[0], point[1], center[0], center[1], end_x, end_y)
                    if dist < laser['thickness'] / 2:
                        if current_time - laser.get('last_hit_time', 0) >= self.scythe_damage_cooldown:
                            print("Player hit by rotating laser!")
                            self.damage_sound.play()
                            player_health -= 7
                            laser['last_hit_time'] = current_time
                        break

            # End the attack when the active phase expires.
            if current_time >= laser['active_end_time']:
                self.rotating_laser_active = False
                self.current_attack_in_progress = False
                self.current_attack_index += 1
                print("Rotating Laser attack finished.")

        elif current_attack == 'shockwave_pulse' and self.shockwave_active:
            current_time = pygame.time.get_ticks()
            shockwave = self.shockwave

            # Transition from telegraph to active phase
            if shockwave['phase'] == 'telegraph' and current_time >= shockwave['telegraph_end_time']:
                shockwave['phase'] = 'active'
                shockwave['start_active_time'] = current_time
                print("Shockwave Pulse active.")

            # During active phase, update the current radius and check for collisions
            if shockwave['phase'] == 'active':
                elapsed = current_time - shockwave['start_active_time']
                shockwave['current_radius'] = shockwave['initial_radius'] + shockwave['expansion_rate'] * elapsed

                # Check if the player's collision center is near the expanding edge
                player_distance = math.hypot(
                    target.soul_collision_rect.centerx - shockwave['center'][0],
                    target.soul_collision_rect.centery - shockwave['center'][1]
                )
                tolerance = 10  # pixels tolerance for collision with the shockwave ring
                if abs(player_distance - shockwave['current_radius']) < tolerance:
                    print("Player hit by shockwave!")
                    self.damage_sound.play()
                    player_health -= 5  # Adjust damage as needed

                # End the active phase once its duration is exceeded
                if current_time >= shockwave['active_end_time']:
                    self.shockwave_active = False
                    self.current_attack_in_progress = False
                    self.current_attack_index += 1
                    print("Shockwave Pulse attack finished.")
        
        elif current_attack == 'wall_attack' and self.wall_attack_active:
            current_time = pygame.time.get_ticks()
            wall_move_duration = self.wall_move_duration
            gap_size = self.gap_size
            move_speed = 4  # Adjust speed based on game frame rate

            if self.current_wall_index < len(self.walls):
                wall = self.walls[self.current_wall_index]
                elapsed_time = current_time - wall['start_time']

                if elapsed_time < self.wall_move_duration:
                    if wall['direction'] == 'left':
                        wall['rect'].x -= move_speed
                        if wall['rect'].x <= self.arena_rect.centerx - gap_size:
                            wall['rect'].x = self.arena_rect.centerx - gap_size
                    elif wall['direction'] == 'right':
                        wall['rect'].x += move_speed
                        if wall['rect'].x >= self.arena_rect.centerx + gap_size:
                            wall['rect'].x = self.arena_rect.centerx + gap_size
                    elif wall['direction'] == 'up':
                        wall['rect'].y -= move_speed
                        if wall['rect'].y <= self.arena_rect.centery - gap_size:
                            wall['rect'].y = self.arena_rect.centery - gap_size
                    elif wall['direction'] == 'down':
                        wall['rect'].y += move_speed
                        if wall['rect'].y >= self.arena_rect.centery + gap_size:
                            wall['rect'].y = self.arena_rect.centery + gap_size

                    # Check collision with the player
                    if wall['rect'].colliderect(target.soul_collision_rect):
                        if current_time - wall['last_hit_time'] >= self.spear_damage_cooldown:
                            print("Player hit by moving wall!")
                            self.damage_sound.play()
                            player_health -= 10  # Adjust damage as needed
                            wall['last_hit_time'] = current_time

                else:
                    # Move to the next wall
                    self.walls.pop(self.current_wall_index)
                    if self.current_wall_index < len(self.walls):
                        self.walls[self.current_wall_index]['start_time'] = current_time

            else:
                # All walls have moved, reset and proceed to the next attack
                print("Wall attack finished.")
                self.walls = []
                self.wall_attack_active = False
                self.current_attack_in_progress = False
                self.current_attack_index += 1

        
            # Check if all attacks are completed
        if self.current_attack_index >= len(self.attack_order):
            self.all_attacks_completed = True
            print(f"[DEBUG] All attacks completed. current_phase: {self.current_phase}, current_attack_index: {self.current_attack_index}")

        return player_health
    # ------------------------------------------------------------------
    #                           DRAW
    # ------------------------------------------------------------------
    def draw(self, screen):
        """Draws whichever attack is currently active."""
        # Which attack are we on?
        if self.current_attack_index < len(self.attack_order):
            current_attack = self.attack_order[self.current_attack_index]
        else:
            current_attack = None

        # Hide the arena rectangle and the soul when all attacks are completed
        if current_attack is None:
            return

        # Draw X Blaster Beams
        if current_attack == 'other_attack' and self.other_attack_active:
            current_time = pygame.time.get_ticks()
            for beam in self.blaster_beams:
                # Telegraph phase: draw a thin line
                if current_time < beam['delay']:
                    color = (255, 0, 0)  # Red for telegraph
                    thickness = 2
                # Active phase: draw a thick line
                elif beam['delay'] <= current_time < beam['end_time']:
                    color = (255, 255, 255)  # White for active
                    thickness = beam['thickness']
                else:
                    # Beam finished, don't draw
                    continue

                start_pos = (int(beam['start'][0]), int(beam['start'][1]))
                end_pos = (int(beam['end'][0]), int(beam['end'][1]))
                pygame.draw.line(screen, color, start_pos, end_pos, thickness)

        # Draw Path Spears
        elif current_attack == 'path_spears':
            for spear in self.spears:
                # Choose a rotation angle based on spear['direction']
                direction = spear['direction']
                if direction == 'right':
                    rotated_image = pygame.transform.rotate(self.spear_image, -90)
                elif direction == 'left':
                    rotated_image = pygame.transform.rotate(self.spear_image, 90)
                elif direction == 'up':
                    rotated_image = self.spear_image  # No rotation needed
                elif direction == 'down':
                    rotated_image = pygame.transform.rotate(self.spear_image, 180)
                else:
                    rotated_image = self.spear_image  # Default

                # Get the new rect centered at the spear's position
                rotated_rect = rotated_image.get_rect(center=spear['rect'].center)
                # Blit the rotated image at the corrected position
                screen.blit(rotated_image, rotated_rect)

        # Draw Scythes
        elif current_attack == 'attack3':
            for scythe in self.scythes:
                # Calculate the angle of rotation based on the velocity
                angle = math.degrees(math.atan2(-scythe['velocity'][1], scythe['velocity'][0]))
                # Rotate the image
                rotated_image = pygame.transform.rotate(self.scythe_image, angle)
                # Get the new rect centered at the scythe's position
                rect = rotated_image.get_rect(center=scythe['rect'].center)
                # Blit the rotated image at the corrected position
                screen.blit(rotated_image, rect)
        
        # Draw Shadowfall Barrage Attack
        elif current_attack == 'shadowfall_barrage' and self.shadowfall_attack_active:
            current_time = pygame.time.get_ticks()
            for proj in self.shadowfall_projectiles:
                pos = (int(proj['position'][0]), int(proj['position'][1]))
                # Telegraph phase: draw an outlined circle to indicate the future projectile path
                if current_time < proj['telegraph_end_time']:
                    color = (255, 0, 0)  # Red telegraph indicator
                    radius = 8
                    pygame.draw.circle(screen, color, pos, radius, 2)
                # Active phase: draw a filled circle representing the active projectile
                elif proj['telegraph_end_time'] <= current_time < proj['active_end_time']:
                    color = (255, 255, 255)  # White active projectile
                    radius = 8
                    pygame.draw.circle(screen, color, pos, radius)

        elif current_attack == 'rotating_laser' and self.rotating_laser_active:
            current_time = pygame.time.get_ticks()
            laser = self.rotating_laser
            center = laser['center']
            angle_rad = math.radians(laser['angle'])
            end_x = center[0] + laser['beam_length'] * math.cos(angle_rad)
            end_y = center[1] + laser['beam_length'] * math.sin(angle_rad)
            
            # During telegraph phase, draw a thin red beam.
            if current_time < laser['telegraph_end_time']:
                color = (255, 0, 0)
                thickness = 2
            else:
                # Active phase: thick white beam.
                color = (255, 255, 255)
                thickness = laser['thickness']
            
            pygame.draw.line(screen, color, center, (end_x, end_y), thickness)

        # Draw Shockwave Pulse Attack
        elif current_attack == 'shockwave_pulse' and self.shockwave_active:
            current_time = pygame.time.get_ticks()
            shockwave = self.shockwave

            # Telegraph phase: draw a small circle at the center
            if shockwave['phase'] == 'telegraph':
                color = (255, 0, 0)  # Red for telegraph
                radius = shockwave['initial_radius']
                pygame.draw.circle(screen, color, shockwave['center'], radius, 2)
            
            # Active phase: draw an expanding circle
            elif shockwave['phase'] == 'active':
                color = (255, 255, 255)  # White for active
                radius = int(shockwave['current_radius'])
                pygame.draw.circle(screen, color, shockwave['center'], radius, 2)

        elif current_attack == 'wall_attack' and self.wall_attack_active:
            for wall in self.walls:
                pygame.draw.rect(screen, (255, 255, 255), wall['rect'])  # Draw walls in red

        