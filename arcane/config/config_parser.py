import yaml 
import typer 
from pathlib import Path 

class ConfigError(Exception):
    "Custom exception for config errors"
    pass 

def load_config(config_path: Path) -> dict:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path (Path): The path to the configuration file. 

    Returns:
        dict: A dictionary containing the configuration.

    Raises:
        ConfigError: If the configuration file does not exist or is malformed.
    """

    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigError(f"The config file at {config_path} does not exist.")
    
    try: 
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
        
        if "nodes" not in config or "training" not in config: 
            raise ConfigError("The config file must contain 'nodes' and 'training' sections.")
    
        return config 
    
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing YAML file: {e}")