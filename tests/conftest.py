import pytest
import os
import shutil


DESTINATION_DIRECTORY = fr"DestinationDirectory"


@pytest.fixture
def empty_directory():
    for filename in os.listdir(DESTINATION_DIRECTORY):
        file_path = os.path.join(DESTINATION_DIRECTORY, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


@pytest.fixture
def delete_archive_file():
    working_directory_paths = [fr'WorkingDirectoryWithoutCatalogs',
                               fr'WorkingDirectoryWithCatalog',
                               fr'WorkingDirectoryNotFoundFileCatalogs',
                               fr'WorkingDirectory',
                               fr'UnknownExtensions']
    for working_directory_path in working_directory_paths:
        archive_path = os.path.join(working_directory_path, 'archivePackage')
        if os.path.exists(archive_path):
            shutil.rmtree(archive_path)