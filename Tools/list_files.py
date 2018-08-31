import os

def list_files(root_folder):
    '''returns list of files in all subdirectories of root folder'''
    file_list = []
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for name in files:
            file_list.append(os.path.join(root ,name))
    return(file_list)