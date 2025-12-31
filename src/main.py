import matplotlib.pyplot as plt
import numpy as np
import time as tm

class PlotResults:
    """
    Class to plot the results for comparison. 
    """
    def plot_results(self, data1, data2, label1, label2, filename):
        _, ax = plt.subplots()
        ax.scatter(data1, data2, s=100, c="g", alpha=0.5, cmap=plt.cm.coolwarm, zorder=10)
    
        lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
        ]
    
        ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        plt.xlabel(label1)
        plt.ylabel(label2)
        plt.grid()
        plt.savefig(filename)

class Grid:
    """
    Class to represent an assignment of values to the variables of a Sudoku puzzle. 
    """
    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
        """
        Returns a copy of the grid. 
        """
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
        """
        Returns the matrix with the domains of all variables in the puzzle.
        """
        return self._cells

    def get_width(self):
        """
        Returns the width of the grid.
        """
        return self._width

    def read_file(self, string_puzzle):
        """
        Reads a Sudoku puzzle from string
        """
        i = 0
        row = []
        for p in string_puzzle:
            if p == '.':
                row.append(self._complete_domain)
            else:
                row.append(p)

            i += 1

            if i % self._width == 0:
                self._cells.append(row)
                row = []
            
    def print(self):
        """
        Prints the grid on the screen
        """
        for _ in range(self._width + 4):
            print('-', end=" ")
        print()

        for i in range(self._width):

            print('|', end=" ")

            for j in range(self._width):
                if len(self._cells[i][j]) == 1:
                    print(self._cells[i][j], end=" ")
                elif len(self._cells[i][j]) > 1:
                    print('.', end=" ")
                else:
                    print(';', end=" ")

                if (j + 1) % 3 == 0:
                    print('|', end=" ")
            print()

            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4):
                    print('-', end=" ")
                print()
        print()

    def print_domains(self):
        """
        Print the domain of each variable for a given grid of the puzzle.
        """
        for row in self._cells:
            print(row)

    def is_solved(self):
        """
        Returns True if the puzzle is solved and False otherwise. 
        """
        for i in range(self._width):
            for j in range(self._width):
                if len(self._cells[i][j]) > 1 or not self.is_value_consistent(self._cells[i][j], i, j):
                    return False
        return True
    
    def is_value_consistent(self, value, row, column):
        for i in range(self.get_width()):
            if i == column: continue
            if self.get_cells()[row][i] == value:
                return False
        
        for i in range(self.get_width()):
            if i == row: continue
            if self.get_cells()[i][column] == value:
                return False

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue
                if self.get_cells()[i][j] == value:
                    return False
        return True

class FirstAvailable():
    """
    Returns the first variable encountered whose domain is larger than one.
    """
    def select_variable(self, grid):
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) > 1:
                    return (i,j)
                else:
                    continue
        return None

class MRV():
    """
    Implements the MRV heuristic, that returns one of the variables with smallest domain. 
    """
    def select_variable(self, grid):
        variable = None
        size = 10
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                length = len(grid.get_cells()[i][j])
                if (length > 1) and (length < size) :
                    size = length
                    variable = (i,j)
        return variable



class AC3:
    """
    This class implements the methods needed to run AC3 on Sudoku. 
    """
    def remove_domain_row(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same row. 
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != column:
                new_domain = grid.get_cells()[row][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[row][j]) > 1:
                    variables_assigned.append((row, j))

                grid.get_cells()[row][j] = new_domain
        
        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same column. 
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != row:
                new_domain = grid.get_cells()[j][column].replace(grid.get_cells()[row][column], '')
                
                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[j][column]) > 1:
                    variables_assigned.append((j, column))

                grid.get_cells()[j][column] = new_domain

        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same unit. 
        """
        variables_assigned = []

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue

                new_domain = grid.get_cells()[i][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[i][j]) > 1:
                    variables_assigned.append((i, j))

                grid.get_cells()[i][j] = new_domain
        return variables_assigned, False

    def pre_process_consistency(self, grid):
        """
        The method runs AC3 for the arcs involving the variables whose values are 
        already assigned in the initial grid. 
        """
        Q = set()

        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if (len(grid.get_cells()[i][j])) == 1:
                    Q.add((i,j))
        
        return self.consistency(grid, Q)

    

    def consistency(self, grid, Q):
        """
        Implement the arc consistency of the puzzle
        """

        while Q:
            var = Q.pop()

            if (len(grid.get_cells()[var[0]][var[1]])) != 1:
                continue

            var_asgr, statusr = self.remove_domain_row(grid, var[0], var[1])
            var_asgc, statusc = self.remove_domain_column(grid, var[0], var[1])
            var_asgu, statusu = self.remove_domain_unit(grid, var[0], var[1])

            if (statusr == True) or (statusc == True) or (statusu == True):
                return True
            for item in var_asgr:
                Q.add(item)
            
            for item in var_asgc:
                Q.add(item)
            
            for item in var_asgu:
                Q.add(item)
        
        return False

class Backtracking:
    """
    Class that implements backtracking search for solving the puzzle. 
    """

    def search(self, grid, var_selector):
        """
        Implements backtracking search with inference. 
        """
        ac3 = AC3()
        
        if grid.is_solved():
            return grid
       
        
        var = var_selector.select_variable(grid)

        if var == None:
            return None

        for d in grid.get_cells()[var[0]][var[1]]:
            if (grid.is_value_consistent(d, var[0], var[1])) == False:
                continue
            else:
                copy_g = grid.copy()
                copy_g.get_cells()[var[0]][var[1]] = d
                Q = {(var[0], var[1])}
                failure = ac3.consistency(copy_g, Q)
                if failure:
                    continue

                rb = self.search(copy_g, var_selector)
                if rb is not None:
                    return rb

        return None


file = open('Puzzles.txt', 'r')
problems = file.readlines()

running_time_mrv = []
running_time_first_available = []

for p in problems:
    # Read problem from string
    g = Grid()
    g.read_file(p)


    mrv = MRV()

    ac3 = AC3()
    ac3.pre_process_consistency(g)

    
    search = Backtracking()
    start = tm.time()
    solution = search.search(g, mrv)
    end = tm.time()
    running_time_mrv.append(end - start)
    print("Solved Sudoku Puzzle using MRV selection algorithm:")
    solution.print()
    
  

    
    fa = FirstAvailable()
    fasearch = Backtracking()
    fstart = tm.time()
    fasolution = fasearch.search(g,fa)
    fend = tm.time()
    running_time_first_available.append(fend - fstart)
    print("Solved Sudoku Puzzle using First Available selection algorithm:")
    fasolution.print()

'''
plotter = PlotResults()
plotter.plot_results(running_time_mrv, running_time_first_available, "Running Time Backtracking (MRV)",
"Running Time Backtracking (FA)", "running_time")
'''

