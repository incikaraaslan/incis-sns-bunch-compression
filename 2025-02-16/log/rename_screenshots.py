import os


def rename(filename: str) -> str:
    filename = filename.replace(", ", "_")
    filename = filename.replace(" ", "-")
    filename = filename.replace(",", "_")
    filename = filename.replace(";", "_")
    filename = filename.lower()
    return filename


input_dir = "./screenshots"

filenames = os.listdir(input_dir)
filenames = sorted(filenames)
filenames = [f for f in filenames if not f.endswith(".py")]

for filename in filenames:
    filename_old = filename
    filename_new = rename(filename)
    
    filename_old = os.path.join(input_dir, filename_old)
    filename_new = os.path.join(input_dir, filename_new)
    
    os.rename(filename_old, filename_new)

    print(filename_old)
    print(filename_new)
    print()
