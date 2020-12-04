''' A helper utility for managing files. '''

class FileUtils:
    ''' Utilities to assist with file management for the operating system. '''
    @staticmethod
    def write_file(filepath, file):
        ''' Writes a file to disk, given the full file path and the actual file (in memory). '''
        with open(filepath, "wb") as f_data:
            f_data.write(file)

    @staticmethod
    def read_file(filepath):
        '''  '''
        with open(filepath) as open_file:
            contents = open_file.read()
        return contents
