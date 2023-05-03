## Why do we need this file?
# We want our users to have a simple API to run the project. 
# So, we need a "wrapper" that will hide all  details to do so,
# thus enabling our users to simply type 'Assembler <path>' in order to use it.
# Define variables

SRC_DIR := .
SRC_FILES := $(wildcard $(SRC_DIR)/*.py)
OBJ_FILES := $(patsubst $(SRC_DIR)/%.py,$(SRC_DIR)/%.pyc,$(SRC_FILES))
TARGET := Assembler

# Define rules
all: $(TARGET)

$(TARGET): $(OBJ_FILES)
	python -m py_compile $(SRC_DIR)/Main.py
	mv $(SRC_DIR)/__pycache__/Main.*.pyc $(SRC_DIR)/$(TARGET)

$(SRC_DIR)/%.pyc: $(SRC_DIR)/%.py
	python -m py_compile $<

clean:
	rm -f $(SRC_DIR)/$(TARGET) $(OBJ_FILES)

.PHONY: all clean
