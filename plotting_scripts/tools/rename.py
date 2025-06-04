import os


def rename(filename: str) -> str:
    filename = filename.replace(", ", "_")
    filename = filename.replace(" ", "-")
    filename = filename.lower()
    return filename


filenames = os.listdir(".")
filenames = [f for f in filenames if not f.endswith(".py")]

for filename in filenames:
    filename_old = filename
    filename_new = rename(filename)
    os.rename(filename_old, filename_new)

    print(filename_old)
    print(filename_new)
    print()
