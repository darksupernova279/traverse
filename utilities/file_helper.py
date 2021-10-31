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
        ''' Pass in the filepath and this method will return the contents to you. '''
        with open(filepath) as open_file:
            contents = open_file.read()
        return contents


    @staticmethod
    def load_file_with_tokens(file_path, identifier=None, **tokens_n_values):
        '''
            Pass in the full path to the file then a dictionary of tokens and their values. Returns the file with tokens replaced.
            If you use an identifier for your tokens then pass in the identifier you use, for example $$user_id$$ where the $ signs are the
            identifier, you must pass in '$$' so it is added to the start and end of the token value. Or leave blank and no identifier is assumed.
            E.G. FileUtils.load_file_with_tokens('c:\\test\\myfile.txt', identifier='$$', user_id=123, firstName='Harry')
        '''
        file = open(file_path, 'r')
        contents = file.read()
        file.close()

        for key, value in tokens_n_values.items():
            if identifier is not None:
                contents = contents.replace(f'{identifier}{key}{identifier}', str(value))
            else:
                contents = contents.replace(key, value)

        return contents
