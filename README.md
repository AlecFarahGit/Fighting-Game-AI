# NES Fighting Game AI Agent

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FCEUX](https://img.shields.io/badge/FCEUX-Emulator-red.svg)


## Overview

This project utilizes a Reinforcement Learning agent trained to play a NES fighting game against thfroe built-in CPU. The environment bridges a Python-based machine learning backend with the FCEUX NES emulator using a custom Lua scripting interface and pipe communication.

## Architecture

The system is divided into three main components:
1. **FCEUX Emulator:** Runs the NES ROM.
2. **Lua Bridge (`Luafiles.lua`, `EmulationInterface.py`):** Handles startup of FCEUX enviroment, reads memory addresses (RAM) to extract game state (player health and position) and writes controller inputs. It communicates with the Python script via a pipe.
3. **Python Agent (`AI.py`):** Receives the game state, processes it through a Deep Q-Network algorithm, and sends the optimal next action back to the emulator.

## Prerequisites

* Python 3.8 or higher
* [FCEUX Emulator](http://fceux.com/) 
* Super Tilt Bro. for NES version 2.RC4

## Installation

1. Clone the repository

2. Install the required Python dependencies:
   * `pip install torch gymnasium matplotlib` 
   *(Dependencies: `torch`, `gymnasium`, `matplotlib`)*

## Setup & Usage


### 1. Start Training
Launch the Python training script:
```bash
python AI.py
```

### 2. Watch agent in real time
Watch the agent train while playing against the CPU in real time

---

## How It Works: The Deep Q-Network Agent

The brain of this AI agent is built using a Deep Q-Network implemented in PyTorch. The agent learns to play the game through trial and error, utilizing a reinforcement learning loop that balances exploring new moves and exploiting known winning strategies.

### 1. The Neural Network Architecture
The agent evaluates the game state and decides on an action using a Feed-Forward Neural Network. 
* **Input:** The current state of the emulator (`n_observations`).
* **Hidden Layers:** The network consists of four hidden layers, each containing 254 neurons. It uses ReLU (Rectified Linear Unit) activation functions to process complex, non-linear relationships in the game state.
* **Output:** The final layer outputs a predicted "Q-value" (expected future reward) for each of the **18 possible controller actions**. The action with the highest Q-value is generally chosen.

### 2. Decision Making: The Epsilon-Greedy Strategy
To ensure the agent discovers good strategies rather than just repeating the first safe move it finds, it uses an Epsilon-Greedy policy:
* **Exploration:** In the beginning, the agent relies heavily on random actions to explore the environment (`EPS_START = 0.9` means 90% of early actions are random).
* **Exploitation:** As training progresses, the probability of taking a random action exponentially decays (`EPS_DECAY = 1000`) down to a minimum threshold (`EPS_END = 0.05`). The agent shifts to relying on the Neural Network to pick the best possible move.

### 3. Experience Replay (The Agent's Memory)
Instead of learning from single, immediate actions—which can cause the network to forget past lessons or get stuck in repetitive loops—the agent uses a **Replay Memory**.
* Every step taken produces a transition: `(State, Action, Next State, Reward)`.
* These transitions are saved into a memory buffer with a maximum capacity of **20,000** events.
* During the learning phase, the agent randomly samples a batch of **254 transitions** from this memory to train on. This breaks the correlation between sequential game frames and stabilizes the learning process.

### 4. The Learning Loop and Optimization
The core training loop involves calculating how "wrong" the network's predictions were and adjusting its internal weights to be more accurate:
1. **Target Network:** The system actually uses *two* neural networks. The active `policy_net` makes the decisions, while a slower-updating `target_net` is used to estimate the optimal future rewards. This dual-network setup prevents the AI from chasing a moving target.
2. **Bellman Equation:** For the sampled batch, the agent calculates the target Q-value by taking the immediate reward and adding the discounted maximum future reward (discounted by `GAMMA = 0.99`).
3. **Loss Calculation:** It measures the difference between what the active network predicted and the target Q-value using **Huber Loss (Smooth L1 Loss)**, which is less sensitive to extreme outliers than standard squared error.
4. **Backpropagation:** The `AdamW` optimizer (with a learning rate of `1e-4`) updates the network weights. Gradient clipping is applied (max value 100) to prevent the "exploding gradient" problem.
5. **Soft Updates:** At the end of every step, a tiny fraction (`TAU = 0.005`) of the active network's learned weights are blended into the target network, ensuring smooth and stable progression.

---

## Directory Structure
```text
├── runs/                  # Saved tfevents for analysis
├── AI.py
├── EmulationInterface.py
├── Luafiles.lua
├── Game.nes		   # The NES game file (Super Tilt Bro. for NES version 2.RC4)
└── README.md
