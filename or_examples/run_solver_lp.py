from __future__ import print_function
from ortools.linear_solver import pywraplp


def run_solver_lp():
    """
    We are a chemical company and we want to make as much money as possible.

    We have:
    1. 500 g of solution A.
    2. 400 g of solution B.
    3. 700 g of solution C.

    We can make:
    Compound x, which takes 10 g of A, 20 g of B, and 30 g of C to make 1 g of compound x.
    Compound y, which takes 20 g of A, 14 g of B, and 25 g of C to make 1 g of compound y.
    Compound z, which takes 22 g of A, 0 of B, and 40 of C to make 1 g of compound z.

    Compound x is worth $100 / g.
    Compound y is worth $80 / g.
    Compound z is worth 70 / g.

    Question: How can we maximize our profits?
    To do this, we want to maximize the OBJECTIVE FUNCTION:
    Maximize: 100x + 80y + 70z

    We can produce fractional amounts of compounds x, y, and z and use fractional amounts of solutions A, B, and C.
    This is called a LINEAR PROGRAM.
    """
    # We start off by creating a solver.
    solver = pywraplp.Solver("Chemistry Lab",
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    # Now we make the decision variables.
    # The decision variables determine how much of compounds x, y, and z we will make.
    x = solver.NumVar(0, solver.infinity(), 'x')
    y = solver.NumVar(0, solver.infinity(), 'y')
    z = solver.NumVar(0, solver.infinity(), 'z')

    # We have to implement constraints so that we don't use more material than we have. This
    # is where the recipes to make x, y, and z are implicitly coded.

    # For every x, we need 10 A.
    # For every y, we need 20 A.
    # For every z, we need 22 A.
    # We only have 500 g of A.
    a = solver.Add(10 * x + 20 * y + 22 * z <= 500)

    # For every x, we need 20 B.
    # For every y, we need 14 B.
    # For every z, we need 0 B.
    # We only have 400 g of B.
    b = solver.Add(20 * x + 14 * y <= 400)

    # For every x, we need 30 C.
    # For every y, we need 25 C.
    # For every z, we need 40 C.
    # We only have 700 g of C.
    c = solver.Add(30 * x + 25 * y + 40 * z <= 700)

    # Now, we want to maximize our profits.
    # Compound x is worth $100 / g.
    # Compound y is worth $80 / g.
    # Compound z is worth 70 / g.
    solver.Maximize(100 * x + 80 * y + 70 * z)

    # Run the solver.
    solver.Solve()

    # Print the value of each variable in the solution.
    print('Solution:')
    print('x = %f' % x.solution_value())
    print('y = %f' % y.solution_value())
    print('z = %f' % z.solution_value())
    print('Optimal earnings: %f\n' % solver.Objective().Value())

    # Let's just check to make sure that the constraints weren't violated.

    # Check no more than 500 A were used.
    print("A used (max 500): %f" % (10 * x.solution_value() + 20 * y.solution_value() + 22 * z.solution_value()))

    # Check no more than 400 B were used.
    print("B used (max 400): %f" % (20 * x.solution_value() + 14 * y.solution_value()))

    # Check that no more than 700 C were used.
    print('C used (max 700): %f' % (30 * x.solution_value() + 25 * y.solution_value() + 40 * z.solution_value()))


if __name__ == '__main__':
    run_solver_lp()
