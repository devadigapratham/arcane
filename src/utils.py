import yaml 

def load_config(config_path): 
    """Load and parse the YAML configuration file."""
    with open(config_path, "r") as file: 
        return yaml.safe_load(file)

def log_message(message): 
    """Log a message to the console."""
    print(f"[Arcane] {message}")