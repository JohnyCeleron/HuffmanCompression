import os
import json
import Huffman
import bitarray


def create_archive_folder(working_directory, name, fileNames):
    if os.path.exists(f'{working_directory}/{name}'):
        raise FileExistsError("An archived folder with this name has already "
                              "been created in the current directory")
    archive_folder = os.path.join(f'{working_directory}', name)
    encoding_meta_file = os.path.join(archive_folder, 'encoding_meta.json')
    decoding_meta_file = os.path.join(archive_folder, 'decoding_meta.json')
    os.makedirs(archive_folder)

    encoding_json_dict = dict()
    decoding_json_dict = dict()
    for file in fileNames:
        if file.endswith('.txt'):
            _archive_txt(decoding_json_dict, encoding_json_dict,
                         file,
                         working_directory,
                         archive_folder)
        else:
            raise ValueError('Unknown format type for archive file')
    _save_meta(encoding_meta_file, encoding_json_dict)
    _save_meta(decoding_meta_file, decoding_json_dict)


def unarchive_folder(archive_folder_path, destination):
    if not(os.path.exists(archive_folder_path)):
        raise FileNotFoundError("No such archive folder")
    for file in os.listdir(archive_folder_path + '/'):
        file = str(file)
        if file.endswith('.bin'):
            _unarchive_txt(archive_folder_path, file, destination)
        elif file.endswith('.json'):
            continue
        else:
            raise ValueError(f'Unknown format type for unarchive file {file}')


def _save_meta(json_file, meta):
    with open(json_file, 'w+', encoding='UTF-8') as f:
        json.dump(meta, indent=4, ensure_ascii=False, fp=f)


def _get_meta(json_file):
    with open(json_file, 'r+', encoding='utf-8') as f:
        return json.load(f)


def _archive_txt(decoding_json_dict, encoding_json_dict, fileName,
                 working_directory,
                 archive_folder):
    text = ''
    file = os.path.join(working_directory, fileName)
    with open(file, 'r+', encoding='utf-8') as f:
        for line in f:
            text += line
    encoding_table = Huffman.get_encoding_table(text)
    file = fileName.removesuffix('.txt')
    fileZip_path = os.path.join(archive_folder + '\\', f'{file}.bin')
    decoding_json_dict[fileZip_path] = Huffman.swap_dictionary(encoding_table)
    encoding_json_dict[fileZip_path] = encoding_table
    bit_array = bitarray.bitarray(Huffman.encode(text, encoding_table))
    decoding_json_dict[fileZip_path]['len'] = len(bit_array)
    with open(fileZip_path, 'wb') as f:
        bit_array.tofile(f)


def _unarchive_txt(archive_folder, filename, destination):
    filepath = os.path.join(archive_folder, filename)
    decoding_meta_file = os.path.join(archive_folder, 'decoding_meta.json')
    decoding_table = _get_meta(decoding_meta_file)[filepath]
    binary_code = bitarray.bitarray()
    with open(filepath, 'rb') as f:
        binary_code.fromfile(f)
    binary_code = binary_code.to01()[:decoding_table['len']]
    decoded_text = Huffman.decode(binary_code, decoding_table)
    unarchived_path = os.path.join(destination,
                                   filename.removesuffix('.bin') + '-unzip.txt')
    with open(unarchived_path, 'w+', encoding='utf-8') as f:
        f.write(decoded_text)