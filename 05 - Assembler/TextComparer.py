
"""
This Program created in order to compare two files and return the differences between them.
"""

import sys
import os

def compare_files(file1, file2):
    """
    Compare two files and return the differences between them.
    """
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        file1 = f1.readlines()
        file2 = f2.readlines()
    differences = []
    for i, line in enumerate(file1):
        if line != file2[i]:
            differences.append((i, line, file2[i]))
    return differences

if __name__ == "__main__":
    with open('differences.txt', 'w') as f:
        for difference in compare_files(sys.argv[1], sys.argv[2]):
            f.write(f"Line {difference[0]}: {difference[1]} {difference[2]}")
    # if the two files are identical, the differences.txt file will be empty,
    # and the program will print "Files are identical"
    # if the files are different, the differences.txt file will contain the differences
    # and the program will print "Files are different"

    if os.stat('differences.txt').st_size == 0:
        print("Files are identical")
    else:
        print("Files are different")
