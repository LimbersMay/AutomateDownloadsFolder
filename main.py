from services.ordered_files_repository import JsonOrderedFilesRepository


def main():
    ordered_files_repository = JsonOrderedFilesRepository("data/settings.json")

if __name__ == "__main__":
    main()
