# Get the script name dynamically based on the sole script in the repo
SCRIPT_NAME := $(wildcard *.py)
INSTALL_NAME := $(basename $(SCRIPT_NAME))
INSTALL_PATH := /usr/local/bin/$(INSTALL_NAME)

build:
	@echo "Copying $(SCRIPT_NAME) to $(INSTALL_PATH)..."
	sudo cp $(SCRIPT_NAME) $(INSTALL_PATH)
	sudo chmod +x $(INSTALL_PATH)
	@echo "Installed $(INSTALL_NAME) to $(INSTALL_PATH)."

rebuild:
	@echo "Rebuilding $(INSTALL_NAME)..."
	sudo rm -f $(INSTALL_PATH)
	sudo cp $(SCRIPT_NAME) $(INSTALL_PATH)
	sudo chmod +x $(INSTALL_PATH)
	@echo "Rebuilt $(INSTALL_NAME) at $(INSTALL_PATH)."

delete:
	@echo "Removing $(INSTALL_NAME) from $(INSTALL_PATH)..."
	sudo rm -f $(INSTALL_PATH)
	@echo "Uninstalled $(INSTALL_NAME)."