import os
import shutil

import pytest
from archiver import create_archive_folder, unarchive_folder
from archiver import FileCatalogsNotFoundError

DESTINATION_DIRECTORY = fr"C:\Users\asus\OneDrive\Рабочий стол\PythonTasks\HuffmanCompression\Tests\TestingArchiver\DestinationDirectory"


@pytest.mark.parametrize('fileCatalogNames', [
    ['big.txt'], ['empty.txt'], ['test1.txt'], ['test2.txt'],
    ['big.txt', 'empty.txt'], ['test1.txt', 'test2.txt'],
    ['big.txt', 'empty.txt', 'test1.txt', 'test2.txt']
])
def test_without_catalogs(fileCatalogNames, empty_directory,
                          delete_archive_file):
    working_directory = fr'C:\Users\asus\OneDrive\Рабочий стол\PythonTasks\HuffmanCompression\Tests\TestingArchiver\WorkingDirectoryWithoutCatalogs'
    _check(fileCatalogNames, working_directory)


@pytest.mark.parametrize('fileCatalogNames', [
    ['EmptyFolderOuter'],
    ['Folder1', 'test1.txt', 'test2.txt']
])
def test_with_catalogs(fileCatalogNames, empty_directory, delete_archive_file):
    working_directory = fr'C:\Users\asus\OneDrive\Рабочий стол\PythonTasks\HuffmanCompression\Tests\TestingArchiver\WorkingDirectoryWithCatalog'
    _check(fileCatalogNames, working_directory)


@pytest.mark.parametrize('fileCatalogNames', [
    ['test.txt'],
    ['Folder'],
    ['test3.txt', 'Folder2']
])
def test_not_found_file_or_catalog(fileCatalogNames, empty_directory,
                                   delete_archive_file):
    working_directory = fr'C:\Users\asus\OneDrive\Рабочий стол\PythonTasks\HuffmanCompression\Tests\TestingArchiver\WorkingDirectoryNotFoundFileCatalogs'
    with pytest.raises(FileCatalogsNotFoundError) as error:
        create_archive_folder(working_directory, 'archivePackage',
                              fileCatalogNames)
    assert str(error.value) == "No such file/catalog in working directory"


@pytest.mark.parametrize('fileCatalogNames', [
    ['Folder1', 'Folder2'],
    ['test1.txt']
])
def test_archiveFolder_outside_working_directory(fileCatalogNames, empty_directory,
                                                 delete_archive_file):
    working_directory = fr'C:\Users\asus\OneDrive\Рабочий стол\PythonTasks\HuffmanCompression\Tests\TestingArchiver\WorkingDirectory'
    pass


def _check(fileCatalogNames,
           working_directory,
           unarchive_folder_path=os.path.join(DESTINATION_DIRECTORY,
                                              'archivePackage(Unzip)')):
    create_archive_folder(working_directory, 'archivePackage', fileCatalogNames)
    archive_folder_path = os.path.join(working_directory, 'archivePackage')
    unarchive_folder(archive_folder_path, DESTINATION_DIRECTORY)
    for fileCatalogName in fileCatalogNames:
        assert os.path.exists(
            os.path.join(unarchive_folder_path, fileCatalogName))
        for file in _get_files(
                os.path.join(unarchive_folder_path, fileCatalogName)):
            source_file = os.path.join(working_directory, os.path.relpath(file,
                                                                          unarchive_folder_path))
            destination_file = file
            source_file_content = ''
            destination_file_content = ''
            with open(source_file, 'r', encoding='utf-8') as f_source, \
                    open(destination_file, 'r',
                         encoding='utf-8') as f_destination:
                for line in f_source:
                    source_file_content += line
                for line in f_destination:
                    destination_file_content += line
            assert source_file_content == destination_file_content


def _get_files(path):
    if not (os.path.isdir(path)):
        yield path
        return
    for root, _, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)