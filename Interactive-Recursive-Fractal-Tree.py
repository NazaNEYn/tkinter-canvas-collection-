# Interactive Recursive Fractal Tree

# You will control the "DNA" of the tree (the spread angle and growth factor) with your mouse in real-time.



import tkinter as tk
import math
import colorsys

# --- Configuration ---
WIDTH = 800
HEIGHT = 600
BG_COLOR = "#1a1a1a" # Dark charcoal
MAX_DEPTH = 10       # How many times the tree splits (Careful going above 12!)
TRUNK_LEN = 120      # Starting length

class FractalTree:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Fractal Tree - Recursion")
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.canvas.pack()
        
        # Initial Tree DNA (Angle and Scale)
        self.angle_offset = math.pi / 4  # 45 degrees
        self.scale_factor = 0.7          # Branches get 30% smaller
        
        # Bind mouse movement to update the tree
        self.canvas.bind('<Motion>', self.update_tree)
        
        # Initial Draw
        self.draw()

    def update_tree(self, event):
        """Maps mouse position to tree logic."""
        # Map Mouse X to Angle (0 to 180 degrees)
        # We normalize x from 0-WIDTH to 0-PI
        self.angle_offset = (event.x / WIDTH) * math.pi
        
        # Map Mouse Y to Scale (Branches get shorter or longer)
        # We normalize y to 0.3 - 0.85 range
        self.scale_factor = 0.85 - (event.y / HEIGHT) * 0.5
        
        self.draw()

    def draw(self):
        """Clears screen and starts the recursive process."""
        self.canvas.delete("all")
        
        # Start the recursion from the bottom center
        # x, y, length, angle (pointing up), current_depth
        self.draw_branch(WIDTH / 2, HEIGHT, TRUNK_LEN, -math.pi / 2, MAX_DEPTH)

    def get_color(self, depth):
        """Calculates color based on branch depth."""
        # Depth 10 (trunk) -> Brown/Red
        # Depth 0 (leaves) -> Green/Cyan
        
        # Map depth to hue (0.0 to 0.4)
        hue = 0.4 - (depth / MAX_DEPTH) * 0.4
        
        rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        return f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'

    def draw_branch(self, x, y, length, angle, depth):
        """
        The Recursive Function.
        It draws a line, then calls ITSELF twice to draw two smaller lines.
        """
        if depth == 0:
            return

        # 1. Calculate the end point of the current branch
        x2 = x + math.cos(angle) * length
        y2 = y + math.sin(angle) * length
        
        # 2. Determine visual properties
        color = self.get_color(depth)
        width = depth # Thicker at bottom, thinner at top
        
        # 3. Draw the branch
        self.canvas.create_line(x, y, x2, y2, fill=color, width=width)
        
        # 4. RECURSION: Create two new branches
        new_length = length * self.scale_factor
        
        # Right Branch
        self.draw_branch(x2, y2, new_length, angle + self.angle_offset, depth - 1)
        
        # Left Branch
        self.draw_branch(x2, y2, new_length, angle - self.angle_offset, depth - 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = FractalTree(root)
    root.mainloop()
