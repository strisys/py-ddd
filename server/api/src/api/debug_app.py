from tabulate import tabulate
import sys

def print_paths():
   rows = [[i, path] for i, path in enumerate(sys.path) if path.strip()]
   print(">>> sys.path:\n" + tabulate(rows, headers=["Index", "Path"], tablefmt="github"))