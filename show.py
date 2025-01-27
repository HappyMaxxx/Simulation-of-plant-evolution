import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import filedialog

pygame.init()

width, height = 1000, 600
cell_size = 10
cols, rows = (width - 200) // cell_size, height // cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tree Growth Visualizer")

GRID_COLOR = (50, 50, 50)
BG_COLOR = (30, 30, 30)
TREE_COLOR = (0, 255, 0)
GROWING_COLOR = (255, 255, 255)
GENOME_BG_COLOR = (50, 50, 50)
GENOME_TEXT_COLOR = (255, 255, 255)

CELL_SIZE = 30
GENOME_BG_COLOR = (36, 36, 36)
GENOME_TEXT_COLOR = (255, 255, 255)

font = pygame.font.SysFont('Arial', 16)

class Cell:
    def __init__(self, tree, x, y, state, gen_index):
        self.tree = tree
        self.x = x
        self.y = y
        self.state = state
        self.gen_index = gen_index
        self.level = 0
        self.energy = 0
        self.last_energy = 0

        self.update_level()

    def update_level(self) -> int:
        cell_y = rows - self.y - 1
        new_level = cell_y + 6
        self.level = 16 if new_level > 16 else new_level

    def how_mutch_upper(self) -> int:
        count = 0
        for cell in self.tree.cells:
            if cell.x == self.x and cell.y < self.y:
                count += 1
        return count

    def update_energy(self) -> int:
        upper = self.how_mutch_upper()
        self.update_level()
        self.energy += self.level * max(3 - upper, 0)
        self.last_energy = self.energy
        return self.energy
    

class Tree:
    def __init__(self):
        self.cells = []
        self.genome = []
        self.getting_energy = 0
        self.waste_energy = 0
        self.energy = 300

    def grow_tree(self):
        for cell in self.cells:
            is_growed = False
            can_grow = False

            if cell.state == 0:
                current_gene = self.genome[cell.gen_index]
                directions = [
                    (cell.x, cell.y - 1),
                    (cell.x - 1, cell.y),
                    (cell.x + 1, cell.y),
                    (cell.x, cell.y + 1)
                ]

                for i, (new_x, new_y) in enumerate(directions):
                    if current_gene[i] == 30:
                        continue

                    if 0 <= new_x < cols and 0 <= new_y < rows:
                        if not any(c.x == new_x and c.y == new_y for c in self.cells):
                            can_grow = True
                            if cell.energy >= 18:
                                self.add_cell(new_x, new_y, 0, current_gene[i])
                                is_growed = True
                
                if is_growed:
                    cell.energy -= 18
                    cell.state = 1

                if not can_grow:
                    cell.state = 1

    def add_cell(self, x, y, state, gen_index):
        self.cells.append(Cell(self, x, y, state, gen_index))

    def update_energy(self) -> None:
        self.getting_energy = sum([cell.energy for cell in self.cells if cell.state == 1])
        self.dell_cells_energy()
        self.waste_energy = len(self.cells) * 13
        self.energy += self.getting_energy - self.waste_energy

    def dell_cells_energy(self) -> None:
        growed_cells = [cell for cell in self.cells if cell.state == 1]
        for cell in growed_cells:
            cell.energy = 0
    
    def update_cells(self) -> None:
        for cell in self.cells:
            cell.update_energy()

    def step(self):
        new_cells = self.grow_tree()
        self.update_cells()
        self.update_energy()

        return new_cells


def draw_grid():
    for x in range(0, width - 200, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (width - 200, y))


def load_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir='saves', filetypes=[("Text files", "*.txt")])
    if not file_path:
        return None
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [list(map(int, line.strip().split(","))) for line in data]

def draw_genome(genome):
    pygame.draw.rect(screen, GENOME_BG_COLOR, (width - 200, 0, 200, height))
    y_offset = 10

    header = ["№", "U", "L", "R", "D"]
    for j, header_item in enumerate(header):
        rect = pygame.Rect(width - 190 + j * (CELL_SIZE), y_offset, CELL_SIZE, CELL_SIZE)
        header_text = font.render(header_item, True, GENOME_TEXT_COLOR)
        screen.blit(header_text, rect.move((CELL_SIZE - header_text.get_width()) // 2, (CELL_SIZE - header_text.get_height()) // 2))
    
    y_offset += CELL_SIZE

    for i, gene in enumerate(genome[:16]):
        index_rect = pygame.Rect(width - 190, y_offset, CELL_SIZE, CELL_SIZE)
        index_text = font.render(f"{i:2}", True, GENOME_TEXT_COLOR)
        screen.blit(index_text, index_rect.move((CELL_SIZE - index_text.get_width()) // 2, (CELL_SIZE - index_text.get_height()) // 2))

        for j, g in enumerate(gene):
            rect = pygame.Rect(width - 190 + (j + 1) * (CELL_SIZE), y_offset, CELL_SIZE, CELL_SIZE)
            gene_number_text = font.render(str(g), True, GENOME_TEXT_COLOR)
            screen.blit(gene_number_text, rect.move((CELL_SIZE - gene_number_text.get_width()) // 2, (CELL_SIZE - gene_number_text.get_height()) // 2))

        y_offset += CELL_SIZE

def draw_tree(tree, display_mode):
    gen_font = pygame.font.SysFont('Arial', 8)

    for cell in tree.cells:
        if display_mode == 'normal':
            x, y, color, gen_index = cell.x, cell.y, TREE_COLOR if cell.state == 1 else GROWING_COLOR, cell.gen_index
            pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))
            # if color == GROWING_COLOR:
            gene_text = gen_font.render(str(cell.last_energy), True, (0, 0, 0))
            screen.blit(gene_text, (x * cell_size + cell_size // 4, y * cell_size + cell_size // 4))
        elif display_mode == 'energy':
            energy_color = (min(255, int(cell.last_energy * 10) + 50), 0, 0)
            pygame.draw.rect(screen, energy_color, (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))

def draw_step_button():
    pygame.draw.rect(screen, (100, 100, 100), (width - 180, height - 50, 160, 40))
    step_text = font.render("Next Step", True, (255, 255, 255))
    screen.blit(step_text, (width - 150, height - 40))

def draw_radio_buttons(screen, display_mode):
        font = pygame.font.SysFont(None, 24)
        normal_text = font.render('Normal', True, (255, 255, 255))
        energy_text = font.render('Energy', True, (255, 255, 255))

        pygame.draw.circle(screen, (255, 255, 255), (width - 185, 535), 10, 1)
        pygame.draw.circle(screen, (255, 255, 255), (width - 95, 535), 10, 1)

        if display_mode == 'normal':
            pygame.draw.circle(screen, (255, 255, 255), (width - 185, 535), 5)
        elif display_mode == 'energy':
            pygame.draw.circle(screen, (255, 255, 255), (width - 95, 535), 5)

        screen.blit(normal_text, (width - 185 + 15, 527))
        screen.blit(energy_text, (width - 105 + 25, 527))

def handle_radio_buttons(mouse_x: int, mouse_y: int, display_mode):
        if width - 185 - 10 <= mouse_x <= width - 185 + 10 and 525 <= mouse_y <= 545:
            return 'normal'
        elif width - 95 - 10 <= mouse_x <= width - 95 + 10  and 525 <= mouse_y <= 545:
            return 'energy' if display_mode != 'energy' else 'normal'
        
        return display_mode

def draw_info(tree):
    font = pygame.font.SysFont('Arial', 18)
    energy_info_text = font.render(f"Energy: {tree.energy} ({tree.getting_energy-tree.waste_energy})", True, (255, 255, 255))
    screen.blit(energy_info_text, (10, 10))
    energy_info_text = font.render(f"Getting: {tree.getting_energy} | Wasting: {tree.waste_energy}", True, (255, 255, 255))
    screen.blit(energy_info_text, (10, 30))
    energy_info_text = font.render(f"Cells: {len(tree.cells)}", True, (255, 255, 255))
    screen.blit(energy_info_text, (10, 50))

def main():
    running = True
    clock = pygame.time.Clock()
    tree = Tree()
    step_mode = False
    display_mode = 'normal'

    tree.genome = load_file()
    if not tree.genome:
        tree.genome = [[0, 1, 2, 3]] * 16

    initial_x, initial_y = (cols // 2, rows - 1)
    tree.add_cell(initial_x, initial_y, 0, 0)
    tree.update_cells()

    while running:
        screen.fill(BG_COLOR)
        draw_grid()
        draw_tree(tree, display_mode)
        draw_genome(tree.genome)
        draw_step_button()
        draw_radio_buttons(screen, display_mode)

        draw_info(tree)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if width - 180 <= mouse_x <= width - 20 and height - 50 <= mouse_y <= height - 10:
                    step_mode = True
                
                display_mode = handle_radio_buttons(mouse_x, mouse_y, display_mode)

        if step_mode:
            tree.step()
            step_mode = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
