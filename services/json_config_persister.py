from models.app_config import AppConfig


class JsonConfigPersister:
    def __init__(self, json_path):
        self.json_file_path = json_path

    def save(self, config: AppConfig):
        json_data = config.model_dump_json(indent=4, by_alias=True)

        with open(self.json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)
