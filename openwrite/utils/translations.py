import json
import importlib.resources

def load_translations():
    data = importlib.resources.files(__package__).joinpath("i18n.json").read_text(encoding="utf-8")
    return json.loads(data)
