from file_sorter import FileSorter
from helpers.directory_creator import DirectoryCreator
from registry_checker import Auditor
from services.ordered_files_repository import JsonOrderedFilesRepository
from services.path_repository import JsonPathRepository
from services.settings_repository import JsonSettingsRepository
from services.notification_service import PlyerNotificationService


def main():
    json_path = "data/settings.json"

    path_repository = JsonPathRepository(json_path)
    settings_repository = JsonSettingsRepository(json_path)
    ordered_files_repository = JsonOrderedFilesRepository(json_path)
    notification_service = PlyerNotificationService()

    # 1. Create the directories if they do not exist
    directory_creator = DirectoryCreator(path_repository, settings_repository)
    directory_creator.execute()

    # 2. Check the files
    auditor = Auditor(path_repository, ordered_files_repository, settings_repository, notification_service)
    auditor.check_files()

    # 3. Sort the files
    file_organizer = FileSorter(path_repository, settings_repository, ordered_files_repository, notification_service)
    file_organizer.sort()


if __name__ == "__main__":
    main()
