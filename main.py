import random
from typing import List, Optional, Tuple
import pygame

pygame.init()

width, height = 1200, 600
cell_size = 20

cols = width // cell_size
rows = height // cell_size

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tree evolution")


class Cell:
    def __init__(self, tree: 'Tree', x: int, y: int, gen: Optional[int] = None, state: Optional[str] = None) -> None:
        self.tree = tree
        self.x = x
        self.y = y
        self.level = (self.y - rows) + 7
        self.energy = self.update_energy()
        self.gen = gen if gen else 0
        self.state = state if state else '0'

    def how_mutch_upper(self) -> int:
        count = 0
        for cell in self.tree.cells:
            if cell.x == self.x and cell.y < self.y:
                count += 1
        return count if count < 3 else 0

    def update_energy(self) -> int:
        self.energy = self.level * (3 - self.how_mutch_upper())
        return self.energy

    def draw_energy(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont(None, 12)
        energy_text = font.render(str(self.energy), True, (0, 0, 0))
        screen.blit(energy_text, (self.x * cell_size + 3, self.y * cell_size + 3))


class Tree:
    def __init__(self) -> None:
        self.cells: List[Cell] = []
        self.energy: int = 300
        self.getting_energy: int = sum([cell.energy for cell in self.cells])
        self.waste_energy: int = len(self.cells) * 13
        self.genome: List[Tuple[int, int, int]] = [self.generate_gen() for _ in range(16)]
        self.genome += [self.generate_color()]

        self.birth()

    @staticmethod
    def generate_gen() -> List[int]:
        return [random.randint(0, 31) if (num := random.randint(0, 31)) <= 15 else 30 for _ in range(4)]

    @staticmethod
    def generate_color() -> Tuple[int, int, int]:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def birth(self) -> None:
        self.cells.append(Cell(tree=self, x=random.randint(5, cols-5), y=rows - 1, gen=self.genome[0]))
    
    def grow(self) -> None:
        for cell in self.cells:
            if cell.state == '0':
                pass


    def update_cells(self) -> None:
        for cell in self.cells:
            cell.update_energy()


def draw_genome(screen: pygame.Surface, genome: List[Tuple[int, int, int]]) -> None:
    font = pygame.font.SysFont('Arial', 15)
    x_offset = 50
    y_offset = 10
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

        gene_number_text = font.render(f"{i + 1}", True, (128, 128, 128))
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

tree = Tree()

running = True
selected_tree = None
genome_window = pygame.Surface((300, 560))
genome_window.fill((0, 0, 0)) 
while running:
    screen.fill((255, 255, 255))

    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, (200, 200, 200), (col * cell_size, row * cell_size, cell_size, cell_size), 1)

    for cell in tree.cells:
        cell.update_energy()
        pygame.draw.rect(screen, tree.genome[16] if cell.state == '1' else (240, 248, 255), (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
        cell.draw_energy(screen)

    if selected_tree:
        draw_genome(genome_window, selected_tree.genome)
        screen.blit(genome_window, (width - 320, 20))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            clicked_cell_x = mouse_x // cell_size
            clicked_cell_y = mouse_y // cell_size
            for cell in tree.cells:
                if cell.x == clicked_cell_x and cell.y == clicked_cell_y:
                    if selected_tree == tree:
                        selected_tree = None
                    else:
                        selected_tree = tree
                    break

pygame.quit()
