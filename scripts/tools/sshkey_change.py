"""Script to change EOL with _ which is required for the key to be used as env variable."""

import sys

if __name__ == "__main__":
    key_file_name = sys.argv[1]
    with open(key_file_name, 'r') as key_file:
        key_string = key_file.read()
        key_string = key_string.replace('\n','_')
        with open(key_file_name + '_', 'w') as key_file:
            key_file.write(key_string)
            print('The key is saved in: ', key_file_name + '_')