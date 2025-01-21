import random
from typing import List, Optional, Tuple
import copy
import pygame

pygame.init()

width, height = 1320, 360
cell_size = 6

cols = width // cell_size
rows = height // cell_size

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tree evolution")

class Cell:
    def __init__(self, tree: 'Tree', x: int, y: int, gen: Optional[int] = None, state: Optional[str] = None) -> None:
        self.tree = tree
        self.x = x
        self.y = y
        self.level = 16 if rows - self.y + 5 > 16 else rows - self.y + 5
        self.energy = 0
        self.gen = gen if gen else 0
        self.gen_number = tree.genome.index(gen) if gen in tree.genome else 0
        self.state = state if state else '0'

    def how_mutch_upper(self) -> int:
        count = 0
        for tree in self.tree.simulation.trees:
            for cell in tree.cells:
                if cell.x == self.x and cell.y < self.y:
                    count += 1
        return count

    def update_energy(self) -> int:
        upper = self.how_mutch_upper()
        self.energy += self.level * max(3 - upper, 0)
        return self.energy

    def draw_energy(self, screen: pygame.Surface) -> None:
        font = pygame.font.SysFont(None, 12)
        string = f"{self.energy}" if self.energy > 0 else ''
        energy_text = font.render(string, True, (0, 0, 0))
        screen.blit(energy_text, (self.x * cell_size + 3, self.y * cell_size + 3))

class Tree:
    def __init__(self, simulation: 'Simulation', x: int = None, y: int = None, genome: List[Tuple[int, int, int]] = None, color_gen: Tuple[int, int, int] = None) -> None:
        self.simulation = simulation
        self.cells: List[Cell] = []
        self.energy: int = 300
        self.getting_energy = sum([cell.energy for cell in self.cells if cell.state == '1'])
        self.waste_energy: int = len(self.cells) * 13
        self.genome: List[Tuple[int, int, int]] = genome if genome else [self.generate_gen(i) for i in range(16)]
        self.genome += [color_gen] if color_gen else [self.generate_color()]
        self.growth_energy = 18
        self.age = 0
        self.die_age = random.randint(88, 92)

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
            self.cells.append(Cell(tree=self, x=x, y=y, gen=self.genome[0]))
        else:
            self.cells.append(Cell(tree=self, x=random.randint(5, cols-1), y=rows - 1, gen=self.genome[0]))

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
                        if cell.y > 0 and not any(c.x == cell.x and c.y == cell.y - 1 for tree in self.simulation.trees for c in tree.cells):
                            can_grow = True
                            if cell.energy >= self.growth_energy:
                                self.cells.append(Cell(tree=self, x=cell.x, y=cell.y - 1, gen=self.genome[gen[i]]))
                                is_growed = True

                    elif i == 1:  # Ліво
                        if cell.x > 0:
                            if not any(c.x == cell.x - 1 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(tree=self, x=cell.x - 1, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True
                        else:
                            if not any(c.x == cols - 1 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(tree=self, x=cols - 1, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True

                    elif i == 2:  # Право
                        if cell.x < cols - 1:
                            if not any(c.x == cell.x + 1 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(tree=self, x=cell.x + 1, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True
                        else:
                            if not any(c.x == 0 and c.y == cell.y for tree in self.simulation.trees for c in tree.cells):
                                can_grow = True
                                if cell.energy >= self.growth_energy:
                                    self.cells.append(Cell(tree=self, x=0, y=cell.y, gen=self.genome[gen[i]]))
                                    is_growed = True

                    elif i == 3:  # Низ
                        if cell.y < rows - 1 and not any(c.x == cell.x and c.y == cell.y + 1 for tree in self.simulation.trees for c in tree.cells):
                            can_grow = True
                            if cell.energy >= self.growth_energy:
                                self.cells.append(Cell(tree=self, x=cell.x, y=cell.y + 1, gen=self.genome[gen[i]]))
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

    def check_death(self) -> None:
        if self.energy <= 0 or self.age >= self.die_age:
            self.die()

    @staticmethod
    def mutate(genome, chance=0.15) -> List[Tuple[int, int, int]]:
        if random.random() > chance:
            return genome, 0

        gene = random.randint(0, 15)
        position = random.randint(0, 3)
        value = random.randint(0, 31)
        if value >= 16:
            value = 30
        genome[gene][position] = value

        return genome[:16], 1

    def clear(self) -> None:
        self.cells = []
        self.energy = 0
        self.age = 0
        self.simulation.trees.remove(self)

    def die(self) -> None:
        self.cells = [cell for cell in self.cells if cell.state == '0']

        for cell in self.cells:
            while cell.y < rows - 1 and not any(c.x == cell.x and c.y == cell.y + 1 for tree in self.simulation.trees for c in tree.cells):
                cell.y += 1

        grounded_cells = [cell for cell in self.cells if cell.y == rows - 1]

        for cell in grounded_cells:
            genome_copy = copy.deepcopy(self.genome[:16])
            mutated_genome, mutated = self.mutate(genome=genome_copy)
            if mutated:
                self.simulation.trees.append(Tree(simulation=self.simulation, x=cell.x, y=cell.y, genome=mutated_genome))
            else:
                self.simulation.trees.append(Tree(simulation=self.simulation, x=cell.x, y=cell.y, genome=mutated_genome, color_gen=self.genome[16]))

        self.clear()

    def check_for_downtime(self) -> None:
        if len(self.cells) == 1 and self.age >= 5:
            self.clear()

    def step(self) -> None:
        self.age += 1
        self.grow()
        self.update_energy()
        self.check_death()
        self.check_for_downtime()

class Simulation:
    def __init__(self) -> None:
        self.trees = []
        self.selected_tree = None
        self.genome_window = pygame.Surface((300, 560))
        self.genome_window.fill((0, 0, 0))

    def add_tree(self, genome: List[Tuple[int, int, int]] = None) -> None:
        self.trees.append(Tree(simulation=self, genome=genome))

    def draw_genome(self, screen: pygame.Surface, genome: List[Tuple[int, int, int]]) -> None:
        font = pygame.font.SysFont('Arial', 5)
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

    def run(self) -> None:
        running = True

        while running:
            screen.fill((0, 0, 0))

            for row in range(rows):
                for col in range(cols):
                    pygame.draw.rect(screen, (0, 0, 0), (col * cell_size, row * cell_size, cell_size, cell_size), 1)

            for tree in self.trees:
                for cell in tree.cells:
                    cell.update_energy()
                    pygame.draw.rect(screen, tree.genome[16] if cell.state == '1' else (240, 248, 255), (cell.x * cell_size, cell.y * cell_size, cell_size, cell_size))
                    # cell.draw_energy(screen)

            if self.selected_tree:
                self.draw_genome(self.genome_window, self.selected_tree.genome)
                screen.blit(self.genome_window, (width - 320, 20))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
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

            for tree in self.trees:
                tree.step()

            pygame.time.delay(100)

        pygame.quit()

genome = [[13, 30, 12, 30], [30, 14, 12, 30], [30, 30, 2, 9], [30, 30, 30, 30],
          [0, 30, 30, 30], [10, 5, 30, 30], [6, 30, 30, 30], [30, 13, 30, 13],
          [15, 30, 30, 30], [30, 30, 0, 30], [30, 30, 30, 30], [30, 30, 2, 30],
          [30, 2, 30, 7], [8, 9, 1, 30], [9, 30, 30, 30], [30, 15, 9, 30],
            (255, 255, 255)]

simulation = Simulation()
for _ in range(4):
    simulation.add_tree(genome=genome)

simulation.run()