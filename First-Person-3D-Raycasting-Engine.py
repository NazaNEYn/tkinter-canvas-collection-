# First-Person 3D Raycasting Engine
# Use the Arrow Keys (Left/Right) to turn and (Up/Down) to move.



import tkinter as tk
import math

# --- Configuration ---
WIDTH = 640   # Screen Width
HEIGHT = 400  # Screen Height
MAP_SIZE = 16 # The map is 16x16 cells
CELL_SIZE = 64 # Size of one block in the "world"

# FOV settings
FOV = math.pi / 3       # Field of View (60 degrees)
HALF_FOV = FOV / 2
NUM_RAYS = 120          # Resolution (Lower = faster, Higher = smoother)
DELTA_ANGLE = FOV / NUM_RAYS # Angle between each ray
SCALE = WIDTH // NUM_RAYS    # Width of each drawn vertical strip

# Map Data (1 = Wall, 0 = Empty Space)
# A simple 16x16 grid
WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class RaycasterEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Raycaster (Wolfenstein Style)")
        
        # Create Canvas
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        
        # Player Start Position
        self.player_x = WIDTH / 2
        self.player_y = HEIGHT / 2
        self.player_angle = 0  # Facing right
        
        # Movement Flags
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
        # Bind Controls
        root.bind("<Left>", lambda e: setattr(self, 'left_pressed', True))
        root.bind("<Right>", lambda e: setattr(self, 'right_pressed', True))
        root.bind("<Up>", lambda e: setattr(self, 'up_pressed', True))
        root.bind("<Down>", lambda e: setattr(self, 'down_pressed', True))
        root.bind("<KeyRelease-Left>", lambda e: setattr(self, 'left_pressed', False))
        root.bind("<KeyRelease-Right>", lambda e: setattr(self, 'right_pressed', False))
        root.bind("<KeyRelease-Up>", lambda e: setattr(self, 'up_pressed', False))
        root.bind("<KeyRelease-Down>", lambda e: setattr(self, 'down_pressed', False))
        
        # Draw Floor and Ceiling (Static)
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT/2, fill="#333333", outline="") # Ceiling
        self.canvas.create_rectangle(0, HEIGHT/2, WIDTH, HEIGHT, fill="#1a1a1a", outline="") # Floor
        
        # Pre-create Vertical Strips (Lines)
        # We create them ONCE and update their coordinates later to be faster
        self.wall_strips = []
        for i in range(NUM_RAYS):
            line = self.canvas.create_line(
                i * SCALE, 0, i * SCALE, HEIGHT, 
                fill="white", width=SCALE + 1
            )
            self.wall_strips.append(line)

        self.game_loop()

    def move_player(self):
        speed = 3.0
        rot_speed = 0.05
        
        # Rotation
        if self.left_pressed: self.player_angle -= rot_speed
        if self.right_pressed: self.player_angle += rot_speed
        
        # Movement (Calculated using Sin/Cos of current angle)
        if self.up_pressed:
            new_x = self.player_x + math.cos(self.player_angle) * speed
            new_y = self.player_y + math.sin(self.player_angle) * speed
            if not self.check_collision(new_x, new_y):
                self.player_x = new_x
                self.player_y = new_y

        if self.down_pressed:
            new_x = self.player_x - math.cos(self.player_angle) * speed
            new_y = self.player_y - math.sin(self.player_angle) * speed
            if not self.check_collision(new_x, new_y):
                self.player_x = new_x
                self.player_y = new_y

    def check_collision(self, x, y):
        """Checks if (x, y) is inside a wall in the map grid."""
        grid_x = int(x // CELL_SIZE)
        grid_y = int(y // CELL_SIZE)
        if 0 <= grid_x < MAP_SIZE and 0 <= grid_y < MAP_SIZE:
            return WORLD_MAP[grid_y][grid_x] == 1
        return False

    def cast_rays(self):
        # Start ray angle at [Player Angle - Half FOV]
        ray_angle = self.player_angle - HALF_FOV
        
        for ray in range(NUM_RAYS):
            # 1. Simple "Stepping" Raycast (Not efficient DDA, but easier to read)
            # We step forward a few pixels at a time until we hit a wall.
            # Warning: Small steps = precision but slow. Big steps = fast but glitches.
            
            step_size = 2 # Precision 
            dist = 0
            
            eye_x = math.cos(ray_angle)
            eye_y = math.sin(ray_angle)
            
            curr_x = self.player_x
            curr_y = self.player_y
            
            hit_wall = False
            
            # Advance ray until it hits a wall or goes too far (Depth of Field)
            while not hit_wall and dist < 800:
                curr_x += eye_x * step_size
                curr_y += eye_y * step_size
                dist += step_size
                
                if self.check_collision(curr_x, curr_y):
                    hit_wall = True

            # 2. Fix "Fish-Eye" effect
            # Without this, walls look curved like a fish-eye lens
            corrected_dist = dist * math.cos(self.player_angle - ray_angle)
            
            # 3. Calculate Wall Height
            # Height is inversely proportional to distance (Further = smaller)
            # Avoid division by zero
            if corrected_dist < 1: corrected_dist = 1 
            
            proj_height = (CELL_SIZE * 350) / corrected_dist # 350 is a projection constant
            
            # 4. Calculate Wall Color (Fake Shading)
            # Darker color if further away to create "Fog" effect
            shade = int(255 - (corrected_dist * 255 / 800))
            if shade < 30: shade = 30 # Minimum brightness
            hex_color = f'#{shade:02x}{shade:02x}{shade:02x}' # Grayscale
            
            # A bit of color variety for walls? Let's stick to shaded gray/blue
            # To make it look like Wolfenstein, let's use a blue tint
            hex_color = f'#{0:02x}{0:02x}{shade:02x}' # Blue walls
            
            # 5. Render the Vertical Strip
            # Center the wall vertically
            wall_top = (HEIGHT / 2) - (proj_height / 2)
            wall_bottom = (HEIGHT / 2) + (proj_height / 2)
            
            self.canvas.coords(
                self.wall_strips[ray], 
                ray * SCALE, wall_top, 
                ray * SCALE, wall_bottom
            )
            self.canvas.itemconfig(self.wall_strips[ray], fill=hex_color)

            ray_angle += DELTA_ANGLE

    def game_loop(self):
        self.move_player()
        self.cast_rays()
        self.root.after(30, self.game_loop) # ~30 FPS

if __name__ == "__main__":
    root = tk.Tk()
    # Disable window resizing for performance
    root.resizable(False, False)
    app = RaycasterEngine(root)
    root.mainloop()
