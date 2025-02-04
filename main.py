import random
from typing import List, Optional, Tuple
import copy
import os
import tkinter as tk
from tkinter import filedialog
from threading import Thread
import sys

from settings import *

import pygame

pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tree evolution")

class Cell:
    def __init__(self, simulation: 'Simulation', tree: 'Tree', x: int, y: int, gen: Optional[int] = None, state: Optional[str] = None) -> None:
        self.simulation = simulation
        self.tree = tree
        self.x = x
        self.y = y
        self.level = 0
        self.energy = 0
        self.last_energy = 0
        self.gen = gen if gen else 0
        self.gen_number = tree.genome.genes.index(gen) if gen in tree.genome.genes else 0
        self.state = state if state else '0'

        self.update_level()

    def update_level(self) -> int:
        cell_y = rows - self.y - 1
        new_level = cell_y + self.simulation.sun_level
        self.level = min(new_level, 16)

    def how_mutch_upper(self) -> int:
        count = 0
        y_above = self.y - 1
        while y_above >= 0:
            if (self.x, y_above) in self.simulation.occupied_positions:
                count += 1
            y_above -= 1
        return count

    def update_energy(self) -> int:
        upper = self.how_mutch_upper()
        self.update_level()
        self.energy += self.level * max(3 - upper, 0)
        self.last_energy = self.energy
        return self.energy

    def draw_energy(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont(None, 12)
        string = f'{self.gen_number}'
        energy_text = font.render(string, True, (0, 0, 0))
        screen.blit(energy_text, (self.x * cell_size + 3, self.y * cell_size + 3))


class Genome:
    def __init__(self, tree: 'Tree', genes: List[List[int]] = None, color: Tuple[int, int, int] = None, ancestral_color: Tuple[int, int, int] = None) -> None:
        self.tree = tree
        self.genes = genes if genes else [self.generate_gen(i) for i in range(16)]
        self.color = color if color else self.generate_color()
        self.ancestral_color = ancestral_color if ancestral_color else self.color

    @staticmethod
    def generate_gen(index: int) -> List[List[int]]:
        result = []
        for _ in range(4):
            num = random.randint(0, 31)
            if num <= 15:
                result.append(num)
            else:
                result.append(30)

        if index == 0:
            count_30 = result.count(30)
            while count_30 > 2:
                result[result.index(30)] = random.randint(0, 15)
                count_30 -= 1

        return result

    @staticmethod
    def generate_color() -> Tuple[int, int, int]:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    

class Tree:
    def __init__(self, simulation: 'Simulation', x: int = None, y: int = None, genome: List[Tuple[int, int, int]] = None, color_gen: Tuple[int, int, int] = None, die_age: int = None, ancestral_color: Tuple[int, int, int] = None) -> None:
        self.simulation = simulation
        self.cells: List[Cell] = []
        self.energy: int = 300
        self.getting_energy = sum([cell.energy for cell in self.cells if cell.state == '1'])
        self.waste_energy: int = len(self.cells) * 13
        self.genome = Genome(self, genes=genome, color=color_gen, ancestral_color=ancestral_color)
        self.growth_energy = 18
        self.age = 0
        self.die_age = die_age if die_age else random.randint(88, 92)
        self.state = 1

        self.birth(x, y)
        self.update_energy()

    def birth(self, x, y) -> None:
        if x and y:
            self.cells.append(Cell(simulation=self.simulation, tree=self, x=x, y=y, gen=self.genome.genes[0]))
        else:
            self.cells.append(Cell(simulation=self.simulation, tree=self, x=random.randint(5, cols-1), y=rows - 1, gen=self.genome.genes[0]))

    def grow(self) -> None:
        for cell in self.cells:
            if cell.state == '0' and cell.energy >= self.growth_energy:
                is_growed = False
                can_grow = False
                
                directions = [
                    (cell.x, cell.y - 1),
                    (cell.x - 1, cell.y),
                    (cell.x + 1, cell.y),
                    (cell.x, cell.y + 1)  
                ]

                for i, (new_x, new_y) in enumerate(directions):
                    if cell.gen[i] == 30:
                        continue

                    new_x = cols - 1 if new_x < 0 else 0 if new_x >= cols else new_x

                    if 0 <= new_y < rows and new_y >= 19 and not (new_x, new_y) in self.simulation.occupied_positions:
                        can_grow = True 
                        self.cells.append(Cell(simulation=self.simulation, tree=self, x=new_x, y=new_y, gen=self.genome.genes[cell.gen[i]]))
                        is_growed = True

                if is_growed:
                    cell.energy -= self.growth_energy
                    cell.state = '1'

                if not can_grow:
                    cell.state = '1'
        
                self.simulation.update_cell_grid()

    def update_energy(self) -> None:
        growed_cells = [cell for cell in self.cells if cell.state == '1']

        self.getting_energy = 0

        for cell in growed_cells:
            self.getting_energy += cell.energy
            cell.energy = 0

        self.waste_energy = len(self.cells) * 13
        self.energy += self.getting_energy - self.waste_energy

    def update_cells(self) -> None:
        for cell in self.cells:
            cell.update_energy()

    def check_death(self) -> None:
        if self.state == 1:
            if self.energy <= 0 or self.age >= self.die_age:
                self.cells = [cell for cell in self.cells if cell.state == '0']
                self.state = 0
        elif self.state == 0:
            if len(self.cells) == 0:
                self.die()
            
            for cell in self.cells:
                if cell.y == rows - 1:
                    genome_copy = copy.deepcopy(self.genome.genes)
                    mutated_genome, mutated = self.mutate(genome=genome_copy, energy=self.energy)
                    die_age = self.mutate_die_age(self.die_age)
                    if mutated:
                        self.simulation.generation += 1
                        self.simulation.trees.append(Tree(simulation=self.simulation, x=cell.x, y=cell.y,
                                                          genome=mutated_genome, die_age=die_age,
                                                          ancestral_color=self.genome.ancestral_color))
                    else:
                        self.simulation.trees.append(Tree(simulation=self.simulation, x=cell.x, y=cell.y,
                                                          genome=mutated_genome, color_gen=self.genome.color,
                                                          die_age=die_age, ancestral_color=self.genome.ancestral_color))
                    
                    self.cells.remove(cell)

    @staticmethod
    def mutate(genome, energy, max_energy=500, min_chance=0.1, max_chance=0.3) -> List[Tuple[int, int, int]]:
        normalized_energy = max(0, min(energy / max_energy, 1))
        mutation_chance = min_chance + (1 - normalized_energy) * (max_chance - min_chance)

        if random.random() > mutation_chance:
            return genome, 0

        gene = random.randint(0, 15)
        position = random.randint(0, 3)
        value = random.randint(0, 15)

        genome[gene][position] = value

        return genome, 1

    @staticmethod
    def mutate_die_age(age, chance=0.25) -> None:
        if random.random() > chance:
            return age

        pom = random.randint(0, 1)
        if pom == 0:
            return age + 1
        else:
            return age - 1

    def die(self) -> None:
        self.cells = []
        self.energy = 0
        self.age = 0
        self.simulation.trees.remove(self)

    def fall_cells(self) -> None:
        for cell in self.cells:
            if cell.y < rows - 1 and not (cell.x, cell.y + 1) in self.simulation.occupied_positions:
                cell.y += 1
            elif cell.y == rows - 1:
                pass
            else:
                self.cells.remove(cell)

    def check_for_downtime(self) -> None:
        if len(self.cells) == 1 and self.age >= 5:
            self.die()

    def step(self) -> None:
        if self.state == 1:
            self.age += 1
            self.grow()
            self.update_cells()
            self.update_energy()
            self.check_death()
            self.check_for_downtime()
        elif self.state == 0:
            self.fall_cells()
            self.check_death()


class TreeDetailsWindow:
    def __init__(self, simulation: 'Simulation', tree: 'Tree') -> None:
        def open_window():
            self.simulation = simulation
            self.tree = tree
            self.simulation.paused = True
            self.window = tk.Tk()

            self.window.title("Tree Details")
            self.window.geometry("530x570")
            self.window.configure(bg='#242424')

            left_frame = tk.Frame(self.window, bg='#242424')
            left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

            tk.Label(left_frame, text=f"Energy: {tree.energy} ({tree.getting_energy-tree.waste_energy})", font=("Arial", 12), bg='#242424', fg='#5E9F61').pack(pady=5)
            tk.Label(left_frame, text=f"Getting: {tree.getting_energy} Waste: {tree.waste_energy}", font=("Arial", 12), bg='#242424', fg='#5E9F61').pack(pady=5)
            tk.Label(left_frame, text=f"Age: {tree.age}/{tree.die_age}", font=("Arial", 12), bg='#242424', fg='#5E9F61').pack(pady=5)

            right_frame = tk.Frame(self.window, bg='#242424')
            right_frame.pack(side=tk.LEFT, padx=0, pady=10, fill=tk.BOTH, expand=True)

            tk.Label(right_frame, text="Genome:", font=("Arial", 12, "bold"), bg='#242424', fg='#5E9F61').pack(pady=5)

            canvas = tk.Canvas(right_frame, width=300, height=520, bg='#333333', highlightbackground='#424242', highlightthickness=2) 
            canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            self.draw_genome(canvas, self.tree.genome.genes)

            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            self.window.mainloop()

        Thread(target=open_window).start()

    def close_window(self) -> None:
        self.simulation.tree_infos.remove(self.tree)
        if len(self.simulation.tree_infos) == 0:
            self.simulation.paused = False
        self.window.destroy()

    def draw_genome(self, canvas: tk.Canvas, genome: List[Tuple[int, int, int]]) -> None:
        x_offset = 40
        y_offset = 30
        column_width = 180
        max_genes_per_column = len(genome) // 2

        for i, gene in enumerate(genome[:16]):
            if i < max_genes_per_column:
                col_offset = x_offset
                gene_index = i
            else:
                col_offset = x_offset + column_width
                gene_index = i - max_genes_per_column

            canvas.create_text(col_offset - 30, y_offset + gene_index * 60 + 15,
                               text=f"{i}", font=("Arial", 14), fill='#5E9F61')

            gene_values = [str(g) for g in gene]
            positions = [(col_offset + 30, y_offset + gene_index * 80),
                         (col_offset, y_offset + gene_index * 80 + 30),
                         (col_offset + 50, y_offset + gene_index * 80 + 30),
                         (col_offset + 30, y_offset + gene_index * 80 + 50)]

            for idx, value in enumerate(gene_values):
                color = '#5E9F61' if value == '30' else '#FFFF00'
                canvas.create_text(positions[idx], text=value, font=("Arial", 14), fill=color)


class UI:
    def __init__(self, simulation: 'Simulation') -> None:
        self.simulation = simulation
        self.pause_button_rect = pygame.Rect(1200, 40, 40, 40)
        self.exit_button_rect = pygame.Rect(1250, 40, 40, 40)
        self.save_button_rect = pygame.Rect(480, 10, 90, 40)
        self.load_button_rect = pygame.Rect(480, 60, 90, 40)
        self.radio_x = 200
        self.font = pygame.font.SysFont('Arial', 20)
        self.icon_color = (94, 149, 95)
        self.bg_color = (66, 66, 66)

    def draw_button(self, screen, rect, text, offset_x=0, offset_y=0) -> None:
        pygame.draw.rect(screen, self.bg_color, rect, 2)
        rendered_text = self.font.render(text, True, self.icon_color)
        screen.blit(rendered_text, (rect.x + offset_x, rect.y + offset_y))

    def draw_pause_button(self) -> None:
        pygame.draw.rect(screen, self.bg_color, self.pause_button_rect, 2)

        if self.simulation.paused:
            pygame.draw.rect(screen, self.icon_color, pygame.Rect(self.pause_button_rect.x + 13.5,
                                                                  self.pause_button_rect.y + 10, 5, 20))
            pygame.draw.rect(screen, self.icon_color, pygame.Rect(self.pause_button_rect.x + 23.5,
                                                                  self.pause_button_rect.y + 10, 5, 20))
        else:
            points = [
                (self.pause_button_rect.x + 12.5, self.pause_button_rect.y + 10),
                (self.pause_button_rect.x + 30, self.pause_button_rect.y + 20),
                (self.pause_button_rect.x + 12.5, self.pause_button_rect.y + 30)
            ]
            pygame.draw.polygon(screen, self.icon_color, points)
    
    def draw_exit_button(self) -> None:
        pygame.draw.rect(screen, self.bg_color, self.exit_button_rect, 2)

        center_x = self.exit_button_rect.x + self.exit_button_rect.width // 2
        center_y = self.exit_button_rect.y + self.exit_button_rect.height // 2

        pygame.draw.line(screen, self.icon_color,
                        (center_x - 10, center_y - 10),
                        (center_x + 10, center_y + 10), 3)
        pygame.draw.line(screen, self.icon_color,
                        (center_x - 10, center_y + 10),
                        (center_x + 10, center_y - 10), 3)

        pygame.draw.rect(screen, self.bg_color, self.exit_button_rect, 2)
        
    def draw_radio_buttons(self) -> None:
        options = ['Normal', 'Energy', 'Family']
        for i, option in enumerate(options):
            y_pos = 30 + (i * 30)
            pygame.draw.circle(screen, self.bg_color, (self.radio_x, y_pos), 10, 1)

            if self.simulation.display_mode == option.lower():
                pygame.draw.circle(screen, self.icon_color, (self.radio_x, y_pos), 5)

            label_text = self.font.render(option, True, self.icon_color)
            screen.blit(label_text, (self.radio_x + 20, y_pos - 10))

    def draw_generation(self) -> None:
        font = pygame.font.SysFont('Arial', 21)
        generation_label = font.render("generation", True, self.icon_color)
        generation_number = font.render(f"{self.simulation.generation}", True, self.icon_color)

        screen.blit(generation_label, (40, 40))
        screen.blit(generation_number, (50, 70))

    def draw_buttons(self) -> None:
        self.draw_button(screen, self.save_button_rect, "Save", 23, 10)
        self.draw_button(screen, self.load_button_rect, "Load", 23, 10)

    def draw_speed_buttons(self) -> None:
        font = pygame.font.SysFont('Arial', 16)
        self.draw_button(screen, pygame.Rect(300, 60, 40, 40), "-", 18, 10)
        speed_text = font.render(f'Speed: {(500-self.simulation.simulation_speed)/100}', True, self.icon_color)
        screen.blit(speed_text, (345, 70))
        self.draw_button(screen, pygame.Rect(430, 60, 40, 40), "+", 15, 10)

    def draw_sun_level_buttons(self) -> None:
        font = pygame.font.SysFont('Arial', 16)
        self.draw_button(screen, pygame.Rect(300, 10, 40, 40), "-", 18, 10)
        sun_text = font.render(f'Sun: {self.simulation.sun_level}', True, self.icon_color)
        screen.blit(sun_text, (362 if self.simulation.sun_level < 10 else 359, 20))
        self.draw_button(screen, pygame.Rect(430, 10, 40, 40), "+", 15, 10)

    def draw_field(self) -> None:
        for row in range(rows):
            for col in range(cols):
                color = (36, 36, 36) if row < menu_height else (0, 0, 0)
                pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size), 1 if row >= 19 else 0)

    def draw(self) -> None:
        self.draw_field()
        self.draw_pause_button()
        self.draw_exit_button()
        self.draw_buttons()
        self.draw_speed_buttons()
        self.draw_sun_level_buttons()
        self.draw_radio_buttons()
        self.draw_generation()


class EventHandler:
    def __init__(self, simulation: 'Simulation') -> None:
        self.simulation = simulation
        self.ui = self.simulation.ui

    def handle_sun_level_buttons(self, mouse_x: int, mouse_y: int) -> None:
        if 300 <= mouse_x <= 340 and 10 <= mouse_y <= 50:
            self.simulation.sun_level = max(0, self.simulation.sun_level - 1)
        elif 430 <= mouse_x <= 470 and 10 <= mouse_y <= 50:
            self.simulation.sun_level = min(16, self.simulation.sun_level + 1)

    def handle_save_load_buttons(self, mouse_x: int, mouse_y: int) -> None:
        if self.ui.save_button_rect.collidepoint(mouse_x, mouse_y):
            self.simulation.paused = True
            self.simulation.save_genome()
            self.simulation.paused = False

        elif self.ui.load_button_rect.collidepoint(mouse_x, mouse_y):
            self.simulation.paused = True
            self.simulation.load_genome()
            self.simulation.paused = False

    def handle_speed_buttons(self, mouse_x: int, mouse_y: int) -> None:
        if 300 <= mouse_x <= 340 and 60 <= mouse_y <= 100:
            self.simulation.simulation_speed = min(400, self.simulation.simulation_speed + 10)
        elif 430 <= mouse_x <= 470 and 60 <= mouse_y <= 100:
            self.simulation.simulation_speed = max(0, self.simulation.simulation_speed - 10) 

    def handle_radio_buttons(self, mouse_x: int, mouse_y: int) -> None:
        if self.ui.radio_x - 10 <= mouse_x <= self.ui.radio_x + 10 and 20 <= mouse_y <= 40:
            self.simulation.display_mode = 'normal'
        elif self.ui.radio_x - 10 <= mouse_x <= self.ui.radio_x + 10  and 50 <= mouse_y <= 70:
            self.simulation.display_mode = 'energy' if self.simulation.display_mode != 'energy' else 'normal'
        elif self.ui.radio_x - 10 <= mouse_x <= self.ui.radio_x + 10  and 80 <= mouse_y <= 100:
            self.simulation.display_mode = 'family' if self.simulation.display_mode != 'family' else 'normal'

    def handle_pause_button(self, mouse_x: int, mouse_y: int) -> None:
        if self.ui.pause_button_rect.collidepoint(mouse_x, mouse_y):
            self.simulation.paused = not self.simulation.paused

    def handle_exit_button(self, mouse_x: int, mouse_y: int) -> None:
        if self.ui.exit_button_rect.collidepoint(mouse_x, mouse_y):
            self.simulation.running = False
            pygame.quit()
            sys.exit()

    def handle_events(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    self.handle_pause_button(mouse_x, mouse_y)
                    self.handle_exit_button(mouse_x, mouse_y)
                    self.handle_radio_buttons(mouse_x, mouse_y)
                    self.handle_speed_buttons(mouse_x, mouse_y)
                    self.handle_save_load_buttons(mouse_x, mouse_y)
                    self.handle_sun_level_buttons(mouse_x, mouse_y)

                    cell_x = mouse_x // cell_size
                    cell_y = mouse_y // cell_size

                    for tree in self.simulation.trees:
                        for cell in tree.cells:
                            if cell.x == cell_x and cell.y == cell_y:
                                TreeDetailsWindow(simulation=self.simulation, tree=tree)
                                self.simulation.tree_infos.append(tree)

                elif event.type == pygame.KEYDOWN:
                    # Pause
                    if event.key == pygame.K_SPACE:
                        self.simulation.paused = not self.simulation.paused

                    # View Mode
                    elif event.key == pygame.K_z:
                        self.handle_radio_buttons(self.ui.radio_x, 20)
                    elif event.key == pygame.K_x:
                        self.handle_radio_buttons(self.ui.radio_x, 50)
                    elif event.key == pygame.K_c:
                        self.handle_radio_buttons(self.ui.radio_x, 80)


class Simulation:
    def __init__(self, started_tree: int = None) -> None:
        self.running = True
        self.trees = []
        self.tree_infos = []
        self.display_mode = 'normal'
        self.paused = False
        self.generation = 0
        self.simulation_speed = 100
        self.sun_level = 6
        self.ui = UI(self)
        self.cell_grid = {}
        self.occupied_positions = set()

        if started_tree:
            for _ in range(started_tree):
                self.add_tree()
    
    def update_cell_grid(self):
        new_cell_grid = {}
        for tree in self.trees:
            for cell in tree.cells:
                new_cell_grid[(cell.x, cell.y)] = cell

        self.cell_grid = new_cell_grid
        self.occupied_positions = set(self.cell_grid.keys())

    def add_tree(self, genome: List[Tuple[int, int, int]] = None, x: int = None, y: int = None) -> None:
        self.trees.append(Tree(simulation=self, genome=genome[:-1] if genome else None,
                               color_gen=genome[-1] if genome and len(genome) == 17 else None, x=x, y=y))

    def save_genome(self) -> None:
        self.selected_tree = None
        tree_for_save = None
        while not tree_for_save:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        clicked_cell_x = mouse_x // cell_size
                        clicked_cell_y = mouse_y // cell_size

                        for tree in self.trees:
                            for cell in tree.cells:
                                if cell.x == clicked_cell_x and cell.y == clicked_cell_y:
                                    tree_for_save = tree
                    elif event.button == 3:
                        return

        root = tk.Tk()
        root.withdraw()
        if not os.path.exists('saves'):
            os.makedirs('saves')
        file_path = filedialog.asksaveasfilename(initialdir='saves', defaultextension=".txt", filetypes=[("Text files", "*.txt")])

        if file_path:
            with open(file_path, 'w') as f:
                for gene in tree_for_save.genome.genes:
                    f.write(','.join(map(str, gene)) + '\n')
                f.write(','.join(map(str, tree_for_save.genome.color)) + '\n')

    def load_genome(self) -> None:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir='saves', filetypes=[("Text files", "*.txt")])

        if file_path:
            with open(file_path, 'r') as f:
                genome = [list(map(int, line.strip().split(','))) if i != 16 else tuple(map(int, line.strip().split(','))) for i, line in enumerate(f)] 
            
            selected_cell = None
            free_space = True
            while not selected_cell:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        clicked_cell_x = mouse_x // cell_size
                        clicked_cell_y = mouse_y // cell_size

                        for tree in self.trees:
                            for cell in tree.cells:
                                if cell.x == clicked_cell_x and cell.y == clicked_cell_y:
                                    free_space = False
                        
                        while clicked_cell_y < rows - 1 and not any(c.x == clicked_cell_x and c.y == clicked_cell_y + 1 for tree in self.trees for c in tree.cells):
                            clicked_cell_y += 1

                        if free_space:
                            selected_cell = (clicked_cell_x, clicked_cell_y)
            
            self.add_tree(genome=genome, x=selected_cell[0], y=selected_cell[1])  

    def run(self):
        event_handler = EventHandler(self)

        event_thread = Thread(target=event_handler.handle_events, daemon=True)
        event_thread.start()

        while self.running:
            screen.fill((0, 0, 0))

            self.update_cell_grid()
            self.ui.draw()

            # for tree in self.trees:
            #    for cell in tree.cells:
            for cell in self.cell_grid.values():
                if self.display_mode == 'normal':
                    pygame.draw.rect(screen, cell.tree.genome.color if cell.state == '1' else (240, 248, 255), 
                                        (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
                elif self.display_mode == 'energy':
                    energy_color = (min(255, int(cell.last_energy * 10) + 50), 0, 0)
                    pygame.draw.rect(screen, energy_color, (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
                elif self.display_mode == 'family':
                    pygame.draw.rect(screen, tree.genome.ancestral_color if cell.state == '1' else (240, 248, 255),
                    (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))

            pygame.display.flip()

            if not self.paused:
                for tree in self.trees:
                    tree.step()

            pygame.time.delay(self.simulation_speed)

        pygame.quit()


class Menu:
    def __init__(self):
        self.input_box = pygame.Rect((width / 2) - 100, 290, 200, 50)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.text = '10'
        self.running = True
        self.font = pygame.font.SysFont('Arial', 40)
        self.small_font = pygame.font.SysFont('Arial', 30)
    
    def draw(self):
        screen.fill((30, 30, 30))
        
        title = self.font.render("Tree Evolution", True, (200, 200, 200))
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))
        
        prompt = self.small_font.render("Enter initial number of trees:", True, (255, 255, 255))
        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, 200))
        
        pygame.draw.rect(screen, self.color, self.input_box, 2)
        txt_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(txt_surface, (self.input_box.x + 10, self.input_box.y + 5))
        
        self.start_button = pygame.Rect((width / 2) - 100, 350, 200, 50)
        pygame.draw.rect(screen, (50, 205, 50), self.start_button)
        start_text = self.font.render("Start", True, (0, 0, 0))
        screen.blit(start_text, (self.start_button.x + 50, self.start_button.y + 5))

        self.end_button = pygame.Rect((width / 2) - 100, 410, 200, 50)
        pygame.draw.rect(screen, (50, 205, 50), self.end_button)
        end_text = self.font.render("Exit", True, (0, 0, 0))
        screen.blit(end_text, (self.end_button.x + 60, self.end_button.y + 5))
        
    def run(self):
        while self.running:
            self.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.active = not self.active
                    else:
                        self.active = False
                    
                    if self.start_button.collidepoint(event.pos):
                        try:
                            initial_trees = int(self.text)
                            self.running = False
                        except ValueError:
                            self.text = '0'
                    
                    if self.end_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            self.active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode
            
            self.color = self.color_active if self.active else self.color_inactive
            pygame.display.flip()
        return int(self.text)

menu = Menu()
initial_trees = menu.run()

simulation = Simulation(started_tree=initial_trees)
simulation.run()