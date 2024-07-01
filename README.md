# PID Controller Tuning with Multi-Objective Optimization

## Overview

### Project Description
This project presents a Python-based approach to PID controller tuning employing multi-objective optimization algorithms, specifically NSGA-II and MOEA/D. The aim is to optimize the PID parameters (Proportional, Integral, Derivative gains) to achieve a desired performance in controlling a DC motor, balancing between competing objectives such as minimizing the Integral Time Absolute Error (ITAE) and Integral Square Error (ISE).

### Objectives
- Optimize the PID parameters to improve DC motor control performance.
- Balance between competing objectives like ITAE and ISE.

### Key Features
- Implementation of PID optimization problem tailored for DC motor control.
- Utilization of NSGA-II and MOEA/D algorithms from the PyMOO library.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/pid-controller-optimization.git
    cd pid-controller-optimization
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the optimization script:
    ```sh
    python optimize_pid.py
    ```

2. The optimized PID parameters and performance metrics will be outputted to the console and saved in a results file.

## Contributing
Contributions are welcome! If you have any improvements or additions, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.
