import os
import json
import re
import logging
from typing import List, Callable, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def create_classifier(conf: Dict) -> Callable[[str], Optional[str]]:
    """
    Creates a classifier function from a configuration dictionary.
    
    The configuration supports two types:
    
    1. Dynamic: If a "format" field is provided, the function will search for the regex pattern and,
       if a match is found, use a capture group (named "value" or group 1) to build a classifier name
       using the provided format string.
       
       Example configuration:
       {
         "pattern": "/x/y/(?P<value>\\w+)",
         "format": "x-y-{value}",
         "flags": "IGNORECASE"
       }
    
    2. Static: If a "name" field is provided, the function will return that fixed name when the pattern matches.
       
       Example configuration:
       {
         "pattern": "error occurred",
         "name": "error_found",
         "flags": "IGNORECASE"
       }
    
    The "flags" field is optional.
    """
    pattern = conf.get("pattern")
    if not pattern:
        raise ValueError("Configuration must include a 'pattern'.")
    flags = conf.get("flags")
    re_flags = re.IGNORECASE if flags == "IGNORECASE" else 0
    regex = re.compile(pattern, re_flags)
    
    if "format" in conf:
        # Dynamic classifier: build name using the format and captured value.
        format_str = conf.get("format")
        def classifier(content: str) -> Optional[str]:
            match = regex.search(content)
            if match:
                if "value" in match.groupdict():
                    captured = match.group("value")
                elif match.groups():
                    captured = match.group(1)
                else:
                    captured = ""
                return format_str.format(value=captured)
            return None
        return classifier
    elif "name" in conf:
        # Static classifier: always return the fixed name if the pattern matches.
        fixed_name = conf.get("name")
        def classifier(content: str) -> Optional[str]:
            if regex.search(content):
                return fixed_name
            return None
        return classifier
    else:
        raise ValueError("Configuration must include either a 'format' (for dynamic) or a 'name' (for static).")

class LogClassifier:
    def __init__(self, config_file: str = None):
        """
        Initializes the LogClassifier by loading classifier definitions from an external JSON configuration file.
        
        The configuration file must have the following structure:
        
        {
          "classifiers": {
            "classifier_key": { ... classifier configuration ... },
            ...
          }
        }
        
        You can specify the config file path directly or via the environment variable CLASSIFIER_CONFIG_PATH.
        """
        config_path = config_file or os.getenv("CLASSIFIER_CONFIG_PATH")
        self.classifiers = {}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                for key, conf in config.get("classifiers", {}).items():
                    try:
                        self.classifiers[key] = create_classifier(conf)
                    except Exception as e:
                        logging.warning(f"Skipping classifier '{key}': {e}")
                logging.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logging.error(f"Failed to load configuration: {e}")
        else:
            logging.warning("No configuration file provided or file does not exist.")
    
    def classify(self, content: str) -> List[str]:
        """
        Applies all configured classifier functions to the provided content.
        Returns a list of classifier names (either dynamic or static) for which the pattern matched.
        """
        matches = []
        for name, classifier_func in self.classifiers.items():
            result = classifier_func(content)
            if result:
                matches.append(result)
        return matches
