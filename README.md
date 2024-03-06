## MILP Optimization - Minimizing Travel Route Optimization
- Goal: To construct a path that has the shortest distance. <br>
Here I implemented **`Pyomo`** framework to solve the **Mixed-Integer Linear Programming(MILP)** optimization problem, and make comparison with Greedy Algorithm. <br>
### Directed Diagram:
<img src='Sample diagram.png'>

### Steps:
1. Define Parameters, Variables, and Sets. (see notebook)
2. Mathematical formulation: Define object function and constraints.(see notebook)
3. Optimization programming.

#### The solution by `Pyomo` framework with total distance **20**.
<img src='solution with pyomo.png'>

#### The solution by `Greedy Heuristic Algorithm` with total distance **25**.
<img src='solution with greedy.png'>

### Conclusion:
1. With `Pyomo` framework, we got the optimal solution 20.
2. Through `Greedy Heuristic Algorithm`, we got the optimal solution 25, which demonstrates there is no algorithms that always provides the best solution. It depends on the problem statement and objective.
