import random
from typing import List, Optional, Tuple
import copy
import os
import tkinter as tk
from tkinter import filedialog

import pygame

pygame.init()

width, height = 1320, 540
cell_size = 6

cols = width // cell_size
rows = height // cell_size

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
        self.gen_number = tree.genome.index(gen) if gen in tree.genome else 0
        self.state = state if state else '0'

        self.update_level()

    def update_level(self) -> int:
        cell_y = rows - self.y - 1
        new_level = cell_y + self.simulation.sun_level
        self.level = 16 if new_level > 16 else new_level

    def how_mutch_upper(self) -> int:
        count = 0
        for tree in self.tree.simulation.trees:
            for cell in tree.cells:
                if cell.x == self.x and cell.y < self.y:
                    count += 1
        return count

    def update_energy(self) -> int:
        upper = self.how_mutch_upper()
        self.update_level()
        self.energy += self.level * max(3 - upper, 0)
        self.last_energy = self.energy
        return self.energy

    def draw_energy(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont(None, 12)
        # string = f"{self.last_energy}" if self.last_energy > 0 else ''
        string = f'{self.level}'
        energy_text = font.render(string, True, (0, 0, 0))
        screen.blit(energy_text, (self.x * cell_size + 3, self.y * cell_size + 3))


class Tree:
    def __init__(self, simulation: 'Simulation', x: int = None, y: int = None, genome: List[Tuple[int, int, int]] = None, color_gen: Tuple[int, int, int] = None, die_age: int = None) -> None:
        self.simulation = simulation
        self.cells: List[Cell] = []
        self.energy: int = 300
        self.getting_energy = sum([cell.energy for cell in self.cells if cell.state == '1'])
        self.waste_energy: int = len(self.cells) * 13
        self.genome: List[Tuple[int, int, int]] = genome if genome else [self.generate_gen(i) for i in range(16)]
        self.genome += [color_gen] if color_gen else [self.generate_color()]
        self.growth_energy = 18
        self.age = 0
        self.die_age = die_age if die_age else random.randint(88, 92)
        self.state = 1

        self.birth(x, y)
        self.update_energy()

    @staticmethod
    def generate_gen(index: int) -> Tuple[int, int, int]:
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

    def birth(self, x, y) -> None:
        if x and y:
            self.cells.append(Cell(simulation=self.simulation, tree=self, x=x, y=y, gen=self.genome[0]))
        else:
            self.cells.append(Cell(simulation=self.simulation, tree=self, x=random.randint(5, cols-1), y=rows - 1, gen=self.genome[0]))

    def grow(self) -> None:
        cells = self.cells
        for cell in cells:
            is_growed = False
            can_grow = False
            if cell.state == '0':
                gen = cell.gen

                for i in range(4):
                    if gen[i] == 30:
                        continue

                    if i == 0:  # Верх
                        if cell.y > 0 and cell.y + 1 > 20 and not any(c.x == cell.x and c.y == cell.y - 1 for tree in self.simulation.trees for c in tree.cells):
                            can_grow = True
                            if cell.energy >= self.growth_energy:
                                self.cells.append(Cell(simulation=self.simulation, tree=self, x=cell.x, y=cell.y - 1, gen=self.genome[gen[i]]))
                                is_growed = True

                    elif i == 1:  # Ліво
                        if cell.x > 0:
                            if not any(c.x == cell.x - 1 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(simulation=self.simulation, tree=self, x=cell.x - 1, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True
                        else:
                            if not any(c.x == cols - 1 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(simulation=self.simulation, tree=self, x=cols - 1, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True

                    elif i == 2:  # Право
                        if cell.x < cols - 1:
                            if not any(c.x == cell.x + 1 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(simulation=self.simulation, tree=self, x=cell.x + 1, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True
                        else:
                            if not any(c.x == 0 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(simulation=self.simulation, tree=self, x=0, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True

                    elif i == 3:  # Низ
                        if cell.y < rows - 1 and not any(c.x == cell.x and c.y == cell.y + 1 for tree in self.simulation.trees for c in tree.cells):
                            can_grow = True
                            if cell.energy >= self.growth_energy:
                                self.cells.append(Cell(simulation=self.simulation, tree=self, x=cell.x, y=cell.y + 1, gen=self.genome[gen[i]]))
                                is_growed = True

                if is_growed:
                    cell.energy -= self.growth_energy
                    cell.state = '1'

                if not can_grow:
                    cell.state = '1'

    def update_energy(self) -> None:
        self.getting_energy = sum([cell.energy for cell in self.cells if cell.state == '1'])
        self.dell_cells_energy()
        self.waste_energy = len(self.cells) * 13
        self.energy += self.getting_energy - self.waste_energy

    def dell_cells_energy(self) -> None:
        growed_cells = [cell for cell in self.cells if cell.state == '1']
        for cell in growed_cells:
            cell.energy = 0

    def update_cells(self) -> None:
        for cell in self.cells:
            cell.update_energy()

    def check_first_death(self) -> None:
        if self.energy <= 0 or self.age >= self.die_age:
            self.first_die()

    def check_death(self) -> None:
        if len(self.cells) == 0:
            self.die()
        
        for cell in self.cells:
            if cell.y == rows - 1:
                genome_copy = copy.deepcopy(self.genome[:16])
                mutated_genome, mutated = self.mutate(genome=genome_copy)
                die_age = self.mutate_die_age(self.die_age)
                if mutated:
                    self.simulation.generation += 1
                    self.simulation.trees.append(Tree(simulation=self.simulation, x=cell.x, y=cell.y, genome=mutated_genome, die_age=die_age))
                else:
                    self.simulation.trees.append(Tree(simulation=self.simulation, x=cell.x, y=cell.y, genome=mutated_genome, color_gen=self.genome[16], die_age=die_age))
                
                self.cells.remove(cell)

    @staticmethod
    def mutate(genome, chance=0.25) -> List[Tuple[int, int, int]]:
        if random.random() > chance:
            return genome, 0

        gene = random.randint(0, 15)
        position = random.randint(0, 3)
        value = random.randint(0, 15)

        genome[gene][position] = value

        return genome[:16], 1

    @staticmethod
    def mutate_die_age(age, chance=0.25) -> None:
        if random.random() > chance:
            return age

        pom = random.randint(0, 1)
        if pom == 0:
            return age + 1
        else:
            return age - 1

    def clear(self) -> None:
        self.cells = []
        self.energy = 0
        self.age = 0
        self.simulation.trees.remove(self)

    def first_die(self) -> None:
        self.cells = [cell for cell in self.cells if cell.state == '0']
        self.state = 0

    def fall_cells(self) -> None:
        for cell in self.cells:
            if cell.y < rows - 1 and not any(c.x == cell.x and c.y == cell.y + 1 for tree in self.simulation.trees for c in tree.cells):
                cell.y += 1
            elif cell.y == rows - 1:
                pass
            else:
                self.cells.remove(cell)

    def die(self) -> None:
        self.clear()

    def check_for_downtime(self) -> None:
        if len(self.cells) == 1 and self.age >= 5:
            self.clear()

    def step(self) -> None:
        if self.state == 1:
            self.age += 1
            self.grow()
            self.update_cells()
            self.update_energy()
            self.check_first_death()
            self.check_for_downtime()
        elif self.state == 0:
            self.fall_cells()
            self.check_death()


class Simulation:
    def __init__(self, started_tree: int = None) -> None:
        self.trees = []
        self.selected_tree = None
        self.genome_window = pygame.Surface((300, 560))
        self.genome_window.fill((0, 0, 0))
        self.display_mode = 'normal'
        self.paused = False
        self.pause_button_rect = pygame.Rect(1200, 40, 40, 40)
        self.save_button_rect = pygame.Rect(950, 40, 90, 40)
        self.load_button_rect = pygame.Rect(1050, 40, 90, 40)
        self.speed_up_button_rect = pygame.Rect(1250, 40, 40, 40)
        self.slow_down_button_rect = pygame.Rect(1150, 40, 40, 40)
        self.radio_x = 200
        self.generation = 0
        self.simulation_speed = 100
        self.sun_level = 6

        if started_tree:
            for _ in range(started_tree):
                self.add_tree()

    def draw_pause_button(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (255, 255, 255), self.pause_button_rect, 2)

        if self.paused:
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.pause_button_rect.x + 13.5, self.pause_button_rect.y + 10, 5, 20))
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.pause_button_rect.x + 23.5, self.pause_button_rect.y + 10, 5, 20))
        else:
            points = [
                (self.pause_button_rect.x + 12.5, self.pause_button_rect.y + 10),
                (self.pause_button_rect.x + 30, self.pause_button_rect.y + 20),
                (self.pause_button_rect.x + 12.5, self.pause_button_rect.y + 30)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), points)

    def draw_speed_buttons(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont('Arial', 16)
        pygame.draw.rect(screen, (255, 255, 255), self.speed_up_button_rect, 2)
        speed_up_text = font.render("+", True, (255, 255, 255))
        screen.blit(speed_up_text, (self.speed_up_button_rect.x + 14, self.speed_up_button_rect.y + 10))

        pygame.draw.rect(screen, (255, 255, 255), self.slow_down_button_rect, 2)
        slow_down_text = font.render("-", True, (255, 255, 255))
        screen.blit(slow_down_text, (self.slow_down_button_rect.x + 18, self.slow_down_button_rect.y + 10))

        speed_text = font.render(f'Speed: {(500-self.simulation_speed)/100}', True, (255, 255, 255))
        screen.blit(speed_text, (1175, 90))

    def add_tree(self, genome: List[Tuple[int, int, int]] = None, x: int = None, y: int = None) -> None:
        self.trees.append(Tree(simulation=self, genome=genome, x=x, y=y))

    def draw_genome(self, screen: pygame.Surface, genome: List[Tuple[int, int, int]]) -> None:
        font = pygame.font.SysFont('Arial', 20)
        x_offset = 50
        y_offset = 2
        column_width = 160
        max_genes_per_column = len(genome) // 2

        for i, gene in enumerate(genome):
            if i == 16:
                continue

            if i < max_genes_per_column:
                col_offset = x_offset
                gene_index = i
            else:
                col_offset = x_offset + column_width
                gene_index = i - max_genes_per_column

            gene_number_text = font.render(f"{i}", True, (128, 128, 128))
            screen.blit(gene_number_text, (col_offset - 30, y_offset + gene_index * 90 + 25))

            gene_values = [str(g) for g in gene]
            positions = [(col_offset + 20, y_offset + gene_index * 90 + 20),
                         (col_offset, y_offset + gene_index * 90 + 40),
                         (col_offset + 40, y_offset + gene_index * 90 + 40),
                         (col_offset + 20, y_offset + gene_index * 90 + 60)]

            for idx, value in enumerate(gene_values):
                color = (128, 128, 128) if value == '30' else (255, 255, 0)
                gene_number_text = font.render(value, True, color)
                screen.blit(gene_number_text, positions[idx])

    def draw_radio_buttons(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont(None, 24)
        normal_text = font.render('Normal', True, (255, 255, 255))
        energy_text = font.render('Energy', True, (255, 255, 255))
        age_text = font.render('Age', True, (255, 255, 255))

        pygame.draw.circle(screen, (255, 255, 255), (self.radio_x, 30), 10, 1)
        pygame.draw.circle(screen, (255, 255, 255), (self.radio_x, 60), 10, 1)
        pygame.draw.circle(screen, (255, 255, 255), (self.radio_x, 90), 10, 1)

        if self.display_mode == 'normal':
            pygame.draw.circle(screen, (255, 255, 255), (self.radio_x, 30), 5)
        elif self.display_mode == 'energy':
            pygame.draw.circle(screen, (255, 255, 255), (self.radio_x, 60), 5)
        elif self.display_mode == 'age':
            pygame.draw.circle(screen, (255, 255, 255), (self.radio_x, 90), 5)

        screen.blit(normal_text, (self.radio_x + 20, 20))
        screen.blit(energy_text, (self.radio_x + 20, 50))
        screen.blit(age_text, (self.radio_x + 20, 80))
    
    def draw_generation(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont('Arial', 21)
        generation_label = font.render("generation", True, (255, 255, 255))
        generation_number = font.render(f"{self.generation}", True, (255, 255, 255))

        screen.blit(generation_label, (40, 40))
        screen.blit(generation_number, (50, 70))

    def save_genome(self):
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
                for gene in tree_for_save.genome:
                    f.write(','.join(map(str, gene)) + '\n')

    def load_genome(self):
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

    def draw_buttons(self, screen):
        font = pygame.font.SysFont('Arial', 20)

        pygame.draw.rect(screen, (255, 255, 255), self.save_button_rect, 2)
        save_text = font.render("Save", True, (255, 255, 255))
        screen.blit(save_text, (self.save_button_rect.x + 15, self.save_button_rect.y + 10))

        pygame.draw.rect(screen, (255, 255, 255), self.load_button_rect, 2)
        load_text = font.render("Load", True, (255, 255, 255))
        screen.blit(load_text, (self.load_button_rect.x + 15, self.load_button_rect.y + 10))

    def run(self) -> None:
        running = True

        while running:
            screen.fill((0, 0, 0))

            for row in range(rows):
                for col in range(cols):
                    if row in range(0, 19):
                        pygame.draw.rect(screen, (169, 169, 169), (col * cell_size, row * cell_size, cell_size, cell_size))
                    else:
                        pygame.draw.rect(screen, (0, 0, 0), (col * cell_size, row * cell_size, cell_size, cell_size), 1)

            for tree in self.trees:
                for cell in tree.cells:
                    if self.display_mode == 'normal':
                        pygame.draw.rect(screen, tree.genome[16] if cell.state == '1' else (240, 248, 255), (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
                    elif self.display_mode == 'energy':
                        energy_color = (min(255, int(cell.last_energy * 10) + 50), 0, 0)
                        pygame.draw.rect(screen, energy_color, (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
                    elif self.display_mode == 'age':
                        age_color = (225 - min(205, int(tree.age * 2.5)), 225 - min(205, int(tree.age * 2.5)), 225 - min(205, int(tree.age * 2.5)))
                        pygame.draw.rect(screen, age_color, (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
                    
                    # cell.draw_energy(screen)

            self.draw_pause_button(screen)
            self.draw_speed_buttons(screen)
            self.draw_buttons(screen)

            if self.selected_tree:
                self.genome_window.fill((0, 0, 0))
                self.draw_genome(self.genome_window, self.selected_tree.genome)
                screen.blit(self.genome_window, (width - 320, 20))

            self.draw_radio_buttons(screen)
            self.draw_generation(screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    clicked_cell_x = mouse_x // cell_size
                    clicked_cell_y = mouse_y // cell_size

                    for tree in self.trees:
                        for cell in tree.cells:
                            if cell.x == clicked_cell_x and cell.y == clicked_cell_y:
                                if self.selected_tree == tree:
                                    self.selected_tree = None
                                else:
                                    self.selected_tree = tree

                    genome_window_rect = pygame.Rect(width - 320, 20, 300, 560)
                    if genome_window_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_tree = None

                    if self.pause_button_rect.collidepoint(mouse_x, mouse_y):
                        self.paused = not self.paused
                    elif self.speed_up_button_rect.collidepoint(mouse_x, mouse_y):
                        self.simulation_speed = max(0, self.simulation_speed - 10) 
                    elif self.slow_down_button_rect.collidepoint(mouse_x, mouse_y):
                        self.simulation_speed = min(400, self.simulation_speed + 10)

                    if self.radio_x - 10 <= mouse_x <= self.radio_x + 10 and 20 <= mouse_y <= 40:
                        self.display_mode = 'normal'
                    elif self.radio_x - 10 <= mouse_x <= self.radio_x + 10  and 50 <= mouse_y <= 70:
                        self.display_mode = 'energy' if self.display_mode != 'energy' else 'normal'
                    elif self.radio_x - 10 <= mouse_x <= self.radio_x + 10  and 80 <= mouse_y <= 100:
                        self.display_mode = 'age' if self.display_mode != 'age' else 'normal'

                    if self.save_button_rect.collidepoint(mouse_x, mouse_y):
                        self.paused = True
                        self.save_genome()
                        self.paused = False

                    elif self.load_button_rect.collidepoint(mouse_x, mouse_y):
                        self.paused = True
                        self.load_genome()
                        self.paused = False

            if not self.paused:
                for tree in self.trees:
                    tree.step()

            pygame.time.delay(self.simulation_speed)

        pygame.quit()


simulation = Simulation(3)
simulation.run()