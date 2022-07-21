import os
from pathlib import Path

if __name__ == "__main__":
    ROOT = Path('/home', 'gmarvin', 'Network_1_Znanstveni_Rad')
    INPUT_OUTPUT_DATA = Path(ROOT, 'input_output_data_0.05_P')
    files = os.listdir(INPUT_OUTPUT_DATA)
    sum = 0
    for file in files:
        sum += os.path.getsize(Path(INPUT_OUTPUT_DATA, file))
    
    print(f"Sum of sizes: {sum*1e-9}GB")