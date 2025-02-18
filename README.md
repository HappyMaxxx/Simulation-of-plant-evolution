# Simulation of Plant Evolution

This program simulates plant evolution, where trees grow, interact with the
environment, and adapt to changing conditions. The simulation models essential
biological processes such as energy distribution, photosynthesis, and soil fertility
effects.

---

## How It Works

The main simulation logic is handled in `main.py`. It initializes the environment,
places trees, and runs the simulation step by step, processing factors such as:

- **Growth Mechanics** — Trees grow cell by cell, using energy gained through
  photosynthesis. Each tree consists of multiple Cell objects, which store
  energy and contribute to the plant's overall growth.
- **Sun Energy** — The simulation includes a dynamic sun level that affects
  photosynthesis. Cells at higher positions receive more sunlight and generate
  more energy.
- **Genetic Evolution** — Each tree has a `Genome` composed of multiple genes
  that determine its growth pattern. When a tree dies, it has a chance to pass
  on a mutated genome to new trees.
- **Tree Aging and Death** — Trees have a finite lifespan, consuming energy each
- step. If a tree runs out of energy or exceeds its lifespan, it dies, making room
  for new growth.

---

## Project Structure

### Main File

- `main.py` — the core simulation program that executes plant growth and environmental interactions. It contains key classes:
  - `Cell` — represents an individual part of a tree, storing energy and interacting with sunlight.
  - `Genome` — defines a tree's genetic information, dictating its growth behavior.
  - `Tree` — manages tree growth, energy usage, aging, and reproduction.
  - `Simulation` — controls the overall simulation, handling updates, rendering, and tree lifecycle management.
  - `UI` — provides a graphical interface for interaction, including a menu and display options.

### Test Implementations

- `test_bigger_map.py` — tests the simulation on a larger map with a minimap for navigation.
- `test_day_night.py` — simulates the transition between day and night, affecting plant energy levels.
- `test_soil.py` — evaluates how soil fertility influences plant development.

### Visualization

- `show.py` — includes two modes:
  - **Sandbox Mode** — allows users to manually design organisms and analyze energy distribution.
  - **Step-by-Step Mode** — enables detailed tracking of genome growth over time. The genome should be selected from those saved from the simulation.

---

## Installation and Running

1. Clone the repository:
   ```bash
   git clone https://github.com/HappyMaxxx/Simulation-of-plant-evolution.git
   cd Simulation-of-plant-evolution
   ```
2. Create and activate a Python virtual environment:  
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # For Linux and macOS
  # or
  venv\Scripts\activate     # For Windows
  ```
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the main simulation:
   ```bash
   python main.py
   ```

---

## Author

Developed as a course project in the discipline “Object-oriented Programming” in the second year of study of the specialty 122 “Computer Science” at VNTU.
2025 1cs-23b Max Patyk.