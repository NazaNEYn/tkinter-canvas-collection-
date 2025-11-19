# Interactive Cyberpunk Neural Network

# This script creates 50 autonomous nodes. If two nodes drift close to each other, they form a connection. If you move your mouse, you disrupt the network.
# Interaction: The particles will react to your mouse movement


import tkinter as tk
import random
import math

# --- Configuration ---
WIDTH = 800
HEIGHT = 600
BG_COLOR = "#050510" # Deep Cyberpunk Blue/Black
NODE_COLOR = "#00FFFF" # Cyan
LINE_COLOR = "#0088AA" # Darker Cyan for connections
MAX_DISTANCE = 100   # Distance at which nodes connect
MOUSE_RANGE = 150    # Distance where mouse affects nodes
NUM_NODES = 50       # Number of floating particles

class Particle:
    def __init__(self, canvas):
        self.canvas = canvas
        # Random Position
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        # Random Velocity (Speed)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        # Visual representation (The Dot)
        self.r = 3
        self.id = canvas.create_oval(
            self.x - self.r, self.y - self.r,
            self.x + self.r, self.y + self.r,
            fill=NODE_COLOR, outline=""
        )

    def move(self, mouse_x, mouse_y):
        # 1. Standard Movement
        self.x += self.vx
        self.y += self.vy

        # 2. Bounce off walls
        if self.x <= 0 or self.x >= WIDTH: self.vx *= -1
        if self.y <= 0 or self.y >= HEIGHT: self.vy *= -1
        
        # 3. Mouse Interaction (Repulsion)
        # If mouse is close, push the particle away
        if mouse_x:
            dist_x = self.x - mouse_x
            dist_y = self.y - mouse_y
            dist = math.sqrt(dist_x**2 + dist_y**2)
            
            if dist < MOUSE_RANGE:
                # Calculate repulsion force
                force = (MOUSE_RANGE - dist) / MOUSE_RANGE
                self.vx += (dist_x / dist) * force * 0.5
                self.vy += (dist_y / dist) * force * 0.5

        # 4. Speed Limit (Friction)
        # Keeps particles from going supersonic after mouse interaction
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > 4:
            self.vx *= 0.9
            self.vy *= 0.9

        # 5. Update Canvas Position
        self.canvas.coords(
            self.id, 
            self.x - self.r, self.y - self.r, 
            self.x + self.r, self.y + self.r
        )

class NeuralNetwork:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Neural Network")
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.canvas.pack()
        
        self.particles = [Particle(self.canvas) for _ in range(NUM_NODES)]
        
        # Track mouse position
        self.mouse_x = None
        self.mouse_y = None
        self.canvas.bind('<Motion>', self.update_mouse)
        
        # List to keep track of line IDs so we can delete them next frame
        self.line_ids = []
        
        self.animate()

    def update_mouse(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def animate(self):
        # 1. Clear old connections (Lines)
        # We don't clear the whole screen (too slow), just the lines we drew.
        for line_id in self.line_ids:
            self.canvas.delete(line_id)
        self.line_ids.clear()
        
        # 2. Move Particles
        for p in self.particles:
            p.move(self.mouse_x, self.mouse_y)
            
        # 3. Draw Connections (The "Brain" Logic)
        # We compare every particle to every other particle
        for i in range(NUM_NODES):
            for j in range(i + 1, NUM_NODES):
                p1 = self.particles[i]
                p2 = self.particles[j]
                
                # Pythagorean theorem for distance
                dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                
                if dist < MAX_DISTANCE:
                    # Connect them!
                    
                    # COOL FACTOR: Calculate opacity based on distance
                    # Closer = Brighter, Farther = Fainter
                    # Note: Tkinter lines don't support alpha easily, 
                    # so we simulate it by thinning the width
                    width = (1 - (dist / MAX_DISTANCE)) * 2
                    
                    line = self.canvas.create_line(
                        p1.x, p1.y, p2.x, p2.y,
                        fill=LINE_COLOR,
                        width=width
                    )
                    self.line_ids.append(line)

        self.root.after(20, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = NeuralNetwork(root)
    root.mainloop()
