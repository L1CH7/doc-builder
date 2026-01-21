# Makefile for Gostdown Automation

# Directories
INPUT_DIR := input
OUTPUT_DIR := output
RUNNER := -m src.main

# Find all subdirectories in input/ - each is a project
# Find all subdirectories in input/ - each is a project
PROJECTS := $(shell find $(INPUT_DIR) -mindepth 1 -maxdepth 1 -type d)
PROJECT_NAMES := $(notdir $(PROJECTS))

# Define targets: output/ProjectName.docx
# Note: Pandoc/Word single file output, we put it directly in output/
TARGETS := $(foreach proj,$(PROJECT_NAMES),$(OUTPUT_DIR)/$(proj).docx)

.PHONY: all clean help debug

# Default target
all: $(TARGETS)

debug:
	@echo "PROJECTS: $(PROJECTS)"
	@echo "PROJECT_NAMES: $(PROJECT_NAMES)"
	@echo "TARGETS: $(TARGETS)"

# Rule to build a project
# The dependency is the runner script and directory
$(OUTPUT_DIR)/%.docx: $(INPUT_DIR)/% src/main.py src/config.py src/runner.py
	@echo "Building project: $*"
	@mkdir -p $(OUTPUT_DIR)
	python3 $(RUNNER) --input-dir $< --output-dir $(OUTPUT_DIR) --root-dir $(CURDIR)

# Clean output
clean:
	rm -rf $(OUTPUT_DIR)
