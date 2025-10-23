from typing import Union
import re

class UIManager():
    def __init__(self): # add options for arbitrary output chanale, add option for logging
        pass
    
    def write(self, output: str, _end: str = "\n") -> None:
        print(output, end=_end)
    
    def get_raw_input(self) -> str:
        return input()

    def get_input(self, options: list[str], lock: bool = False)  -> Union[list[str]]:
        if lock:
            prompt = f"Please choose dices to lock [{" , ".join(options)}] :"
        else:
            prompt = f"Please choose the next option [{" , ".join(options)}] :"
        
        while True:
            u_input = input(prompt).strip()
            if not u_input:
                print("Please choose at least one option")
                continue
            selected_options = [option.strip() for option in re.split(r"[,\s]+", u_input) if option.strip()]

            if not selected_options:
                print("Please enter at least one valid option")
                continue
            
            if not lock and len(selected_options) > 1:
                print("Too much options selected")
                continue

            invalid_options = [opt for opt in selected_options if opt not in options]
            if invalid_options:
                print(f"Invalid option{"s" if len(invalid_options) > 1 else ""} {",".join(invalid_options)}")
                continue

            return selected_options


    def draw_table(self, data1: dict[str, list[Union[int, bool]]], data2: dict[str, int]):
        rows = []
        for key in data1:
            score_val, is_locked = data1[key]
            score_display = str(score_val) if is_locked else "_"
            calculated_display = str(data2[key]) if not is_locked else "_"
            rows.append((key, score_display, calculated_display))
        #create columns
        headers = ("Combination", "Score", "Calculated")
        all_rows = [headers] + rows
        col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(3)]
        #formating
        def format_row(r):
            cells = [f"{str(cell):<{w}}" for cell, w in zip(r, col_widths)]
            return "| " + " | ".join(cells) + " |"
        separator_line = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
        #build table
        table_lines = []
        table_lines.append(separator_line)
        table_lines.append(format_row(headers))
        table_lines.append(separator_line)
        for row in rows:
            table_lines.append(format_row(row))
        table_lines.append(separator_line)
        table = "\n".join(table_lines)
        return table