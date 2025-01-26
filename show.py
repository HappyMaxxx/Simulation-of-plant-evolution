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
        return self.energy


class Tree:
    def __init__(self):
        self.cells = []
        self.genome = []
        self.getting_energy = 0
        self.waste_energy = 0
        self.energy = 300

    def grow_tree(self):
        new_cells = []

        for cell in self.cells:
            is_growed = False
            can_grow = False

            if cell.state == 0:
                current_gene = self.genome[cell.gen_index % len(self.genome)]
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
                        if not any(c.x == new_x and c.y == new_y for c in self.cells + new_cells):
                            can_grow = True
                            if cell.energy >= 18:
                                new_cells.append(Cell(self, new_x, new_y, 0, current_gene[i]))
                                is_growed = True
                
                if is_growed:
                    cell.energy -= 18
                    cell.state = 1

                if not can_grow:
                    cell.state = 1

        return new_cells

    def add_cell(self, x, y, state, gen_index):
        self.cells.append(Cell(self, x, y, state, gen_index))

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

    gene_text = font.render("№  |  U  |  L  |  R  |  D", True, GENOME_TEXT_COLOR)
    screen.blit(gene_text, (width - 190, y_offset))
    y_offset += 15
    
    rozdil_text = font.render("-" * 33, True, GENOME_TEXT_COLOR)
    screen.blit(rozdil_text, (width - 190, y_offset))
    y_offset += 15

    for i, gene in enumerate(genome[:16]):
        gen_str = " | ".join(f"{g:2}" for g in gene)
        gene_text = font.render(f"{i:2}: | {gen_str}", True, GENOME_TEXT_COLOR)
        screen.blit(gene_text, (width - 190, y_offset))
        y_offset += 15

        screen.blit(rozdil_text, (width - 190, y_offset))
        y_offset += 15

def draw_tree(tree):
    gen_font = pygame.font.SysFont('Arial', 8)

    for cell in tree.cells:
        x, y, color, gen_index = cell.x, cell.y, TREE_COLOR if cell.state == 1 else GROWING_COLOR, cell.gen_index
        pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))
        if color == GROWING_COLOR:
            gene_text = gen_font.render(str(cell.energy), True, (0, 0, 0))
            screen.blit(gene_text, (x * cell_size + cell_size // 4, y * cell_size + cell_size // 4))


def draw_step_button():
    pygame.draw.rect(screen, (100, 100, 100), (width - 180, height - 50, 160, 40))
    step_text = font.render("Next Step", True, (255, 255, 255))
    screen.blit(step_text, (width - 150, height - 40))


def main():
    running = True
    clock = pygame.time.Clock()
    tree = Tree()
    step_mode = False

    tree.genome = load_file()
    if not tree.genome:
        tree.genome = [[0, 1, 2, 3]] * 16

    initial_x, initial_y = (cols // 2, rows - 1)
    tree.add_cell(initial_x, initial_y, 0, 0)
    tree.update_cells()

    while running:
        screen.fill(BG_COLOR)
        draw_grid()
        draw_tree(tree)
        draw_genome(tree.genome)
        draw_step_button()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if width - 180 <= mouse_x <= width - 20 and height - 50 <= mouse_y <= height - 10:
                    step_mode = True

        if step_mode:
            new_cells = tree.step()
            tree.cells.extend(new_cells)
            step_mode = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
