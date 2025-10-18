from typing import Dict

class SummarizerConfig:
    """Configuration for the summarizer service."""
    
    # Try a different model
    DEFAULT_MODEL = "google/pegasus-large"
    
    # Generation parameters for different models
    MODEL_PARAMS: Dict = {
        "google/pegasus-large": {
            "max_length": 150,
            "min_length": 30,
            "do_sample": True,
            "temperature": 0.8,
            "top_p": 0.95,
            "num_beams": 4,
            "no_repeat_ngram_size": 2
        }
    }
