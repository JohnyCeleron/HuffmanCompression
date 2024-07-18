import datetime
import os
import shutil

import pytest
from archiver import create_archive_folder, unarchive_folder
from archiver import ArchivedObjectsNotFoundError

DESTINATION_DIRECTORY = fr"DestinationDirectory"


@pytest.mark.parametrize('archived_objects', [
    ['big.txt'], ['empty.txt'], ['test1.txt'], ['test2.txt'],
    ['big.txt', 'empty.txt'], ['test1.txt', 'test2.txt'],
    ['big.txt', 'empty.txt', 'test1.txt', 'test2.txt']
])
def test_without_catalogs(archived_objects, empty_directory,
                          delete_archive_file):
    working_directory = fr'WorkingDirectoryWithoutCatalogs'
    _check(archived_objects, working_directory)


@pytest.mark.parametrize('archived_objects', [
    ['EmptyFolderOuter'],
    ['Folder1', 'test1.txt', 'test2.txt']
])
def test_with_catalogs(archived_objects, empty_directory, delete_archive_file):
    working_directory = fr'WorkingDirectoryWithCatalog'
    _check(archived_objects, working_directory)


@pytest.mark.parametrize('archived_objects', [
    ['test.txt'],
    ['Folder'],
    ['test3.txt', 'Folder2']
])
def test_not_found_file_or_catalog(archived_objects, empty_directory,
                                   delete_archive_file):
    working_directory = fr'WorkingDirectoryNotFoundFileCatalogs'
    with pytest.raises(ArchivedObjectsNotFoundError) as error:
        create_archive_folder(working_directory, 'archivePackage',
                              archived_objects)
    assert str(error.value) == "No such file/catalog in working directory"


@pytest.mark.parametrize('archived_objects,count_folders', [
    (['Folder1', 'Folder2'], 2),
    (['Folder1'], 1),
    (['Folder1'], 3)
])
def test_multiple_unarchived_identical_folders(archived_objects,
                                                 count_folders,
                                                 empty_directory,
                                                 delete_archive_file):
    working_directory = fr'WorkingDirectory'
    create_archive_folder(working_directory, 'archivePackage', archived_objects)
    archive_folder_path = os.path.join(working_directory, 'archivePackage')
    for _ in range(count_folders):
        unarchive_folder(archive_folder_path, DESTINATION_DIRECTORY)
    assert os.path.exists(os.path.join(DESTINATION_DIRECTORY, 'archivePackage(Unzip)'))
    _check(archived_objects, working_directory, is_archived_folder=False)
    for i in range(1, count_folders):
        unarchive_folder_path = os.path.join(DESTINATION_DIRECTORY, f'archivePackage(Unzip{i})')
        assert os.path.exists(unarchive_folder_path)
        _check(archived_objects, working_directory, unarchive_folder_path, is_archived_folder=False)


def _check(archived_objects,
           working_directory,
           unarchive_folder_path=os.path.join(DESTINATION_DIRECTORY,'archivePackage(Unzip)'),
           is_archived_folder=True):
    if is_archived_folder:
        create_archive_folder(working_directory, 'archivePackage', archived_objects)
        archive_folder_path = os.path.join(working_directory, 'archivePackage')
        unarchive_folder(archive_folder_path, DESTINATION_DIRECTORY)
    for archived_object in archived_objects:
        assert os.path.exists(
            os.path.join(unarchive_folder_path, archived_object))
        _check_catalogs(archived_object, unarchive_folder_path, working_directory)
        _check_files(archived_object, unarchive_folder_path, working_directory)


def _check_catalogs(archived_object, unarchive_folder_path, working_directory):
    path = os.path.join(working_directory, archived_object)
    for catalog_path in _get_catalogs(path):
        relative_path = os.path.relpath(catalog_path, working_directory)
        assert os.path.exists(
            os.path.join(unarchive_folder_path, relative_path))
        source_path = catalog_path
        destination_path = os.path.join(unarchive_folder_path, relative_path)
        assert abs(os.path.getctime(source_path) - os.path.getctime(destination_path)) < 10**(-5)
        assert abs(os.path.getmtime(source_path) - os.path.getmtime(destination_path)) < 10**(-5)


def _check_files(archived_object, unarchive_folder_path, working_directory):
    path = os.path.join(working_directory, archived_object)
    for source_file_path in _get_files(path):
        relative_path = os.path.relpath(source_file_path, working_directory)
        destination_file = os.path.join(unarchive_folder_path, relative_path)

        #assert abs(os.path.getctime(source_file_path) - os.path.getctime(destination_file)) < 10**(-5)
        #assert abs(os.path.getmtime(source_file_path) - os.path.getmtime(destination_file)) < 10**(-5)

        source_file_content = ''
        destination_file_content = ''
        with open(source_file_path, 'r', encoding='utf-8') as f_source, \
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
    for root, dirs, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)


def _get_catalogs(path):
    if not(os.path.isdir(path)):
        return
    for root, dirs, _ in os.walk(path):
        for dir in dirs:
            yield os.path.join(root, dir)