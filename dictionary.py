import json
from typing import Dict, List, Tuple
from config import settings

def load_dictionary(file_path: str) -> Dict[str, Tuple[str, List[str]]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            dict_list = json.load(f)
            converted_dict = {}
            for item in dict_list:
                for word, (pinyin, meanings) in item.items():
                    converted_dict[word] = (pinyin, meanings)
            return converted_dict
    except FileNotFoundError:
        raise Exception(f"Dictionary file not found: {file_path}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON format in dictionary file: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading dictionary: {str(e)}")

CHINESE_DICT = load_dictionary(settings.DICTIONARY_PATH)