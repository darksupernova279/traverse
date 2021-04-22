''' A json helper module to keep common functions working with json in one place. '''
import json


class LoadJson:
    ''' All methods that deal with loading a josn file are stored here for easy reuse. '''
    @staticmethod
    def using_filepath(json_path):
        ''' Given the file path load the json file into memory and return it. '''
        with open(json_path, "r") as json_file:
            json_data = json_file.read()

        return json.loads(json_data)


class GetJsonValue:
    ''' Helper class which "Gets" a json value by a certain method, thus call this class and then a method of how you wish the get the json value. '''
    @staticmethod
    def by_key(json_obj, *keys, ignore_key_attr_error=0):
        ''' Pass in a json object, and the key names for which values you want. This function supports up to 5 keys, if you want the value in a json
            for key5 nested like: [key1][key2][key3][key4][key5] then pass in these keys and you will get the value of the deepest nested key '''
        try:
            if len(keys) == 0:
                raise Exception('Error: no arguments passed in!')
            elif len(keys) == 1:
                return json_obj[keys[0]]
            elif len(keys) == 2:
                return json_obj[keys[0]][keys[1]]
            elif len(keys) == 3:
                return json_obj[keys[0]][keys[1]][keys[2]]
            elif len(keys) == 4:
                return json_obj[keys[0]][keys[1]][keys[2]][keys[3]]
            elif len(keys) == 5:
                return json_obj[keys[0]][keys[1]][keys[2]][keys[3]][keys[4]]
            else:
                raise Exception('Error: More keys passed in than I can handle!')

        except (KeyError, AttributeError):
            if ignore_key_attr_error == 0:
                raise
            else:
                return None


class WriteJsonFile:
    ''' Methods for writing json files. '''
    @staticmethod
    def write(json_data, save_path, indent=4):
        ''' Pass in the json object, the path you want to save the file to including the .json extension.
            There is an optional parameter for indent which is defaulted to 4.  '''
        with open(save_path, 'w') as file_out:
            test = json.dumps(json_data, indent=indent)
            file_out.write(test)
