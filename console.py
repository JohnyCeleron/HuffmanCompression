import argparse
import os
from archiver import create_archive_folder, unarchive_folder
from archiver import FileCatalogsNotFoundError

def _execute_archive_command(archiveFolderName, fileCatalogNames):
    working_directory = fr'{os.getcwd()}'
    if fileCatalogNames[0] in ('*' or '.'):
        fileCatalogNames = [fileCatalog for fileCatalog in os.listdir(working_directory)]

    try:
        create_archive_folder(working_directory, archiveFolderName, fileCatalogNames)
    except FileCatalogsNotFoundError as e:
        print(e)
    else:
        print(f'Файлы/Каталоги {fileCatalogNames} успешно заархивированы в папку {archiveFolderName}')


def _execute_unarchive_command(archiveFolder_path, destination=''):
    if destination == '':
        destination = os.path.split(archiveFolder_path)[0]

    try:
        unarchive_folder(archiveFolder_path, destination)
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    else:
        print(f'Папка {os.path.split(archiveFolder_path)[1]} успешно разархивирована в {destination}')


def main():
    parser = argparse.ArgumentParser(description=
                                     'Свой архиватор, написанный с '
                                     'использование алгоритма Хаффмана')
    # Команда архивирования
    subparsers = parser.add_subparsers(dest="command",
                                       help="Доступные команды")
    archive_parser = subparsers.add_parser('archive',
                                           help="Архивировать файлы/папки")
    archive_parser.add_argument("archiveFolderName", type=str,
                                help="Название папки, куда будут архивироваться файлы/папки")
    archive_parser.add_argument("fileCatalogNames", type=str, nargs='+',
                                help="Файлы/папки, которые будут архивироваться")

    # Команда разархивирования
    unarchive_parser = subparsers.add_parser('unarchive',
                                             help='Разархивировать файлы')
    unarchive_parser.add_argument('archiveFolderPath', type=str,
                                  help='Путь до папки, которую надо разархивировать')
    unarchive_parser.add_argument('destination', type=str,
                                  help='Место, куда ты будешь разархивировать файл',
                                  default='')

    args = parser.parse_args()
    if args.command == 'archive':
        _execute_archive_command(args.archiveFolderName, args.fileNames)
    elif args.command == 'unarchive':
        _execute_unarchive_command(args.archiveFolderPath, args.destination)
    else:
        pass


if __name__ == "__main__":
    main()