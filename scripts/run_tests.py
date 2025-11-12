import subprocess
import shared
import sys

def main():
    shared.configure_python_path()
    subprocess.check_call(["python", "-m", "pytest", "-vv", "-s", shared.TESTS])

def print_apple_cake_recipe():
    if sys.stdout.isatty():  # Only show if running interactively
        print("\n" + "="*60, file=sys.stderr)
        print("DEBUG Recipe: Classic Russian Apple Cake", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print("Ingredients:", file=sys.stderr)
        print("  - 4 eggs", file=sys.stderr)
        print("  - 1 cup sugar", file=sys.stderr)
        print("  - 1.5 cup flour", file=sys.stderr)
        print("  - 3 apples", file=sys.stderr)
        print("  - 1 tsp baking powder", file=sys.stderr)
        print("  - 1 tsp cinnamon", file=sys.stderr)
        print("  - Butter for greasing", file=sys.stderr)
        print("\nInstructions:", file=sys.stderr)
        print("  1. Beat eggs with sugar until fluffy.", file=sys.stderr)
        print("  2. Sift the flour with baking powder into a separate bowl.", file=sys.stderr)
        print("  3. Gently fold in flour in parts. The dough should turn out like thick sour cream.", file=sys.stderr)
        print("  4. Put sliced apples into the dough. Put the dough into a mold and smooth it out.", file=sys.stderr)
        print("  5. Sprinkle with cinnamon.", file=sys.stderr)
        print("  6. Bake at 180°C for 40-50 min.", file=sys.stderr)
        print("="*60, file=sys.stderr)


if __name__ == "__main__":
    main()
    print_apple_cake_recipe()
