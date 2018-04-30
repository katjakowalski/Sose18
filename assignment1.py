
# 1. The Landsat sensor family has now overall four satellites (L4, L5, L7, L8), and for each of the four we have a
# different number of scenes available. Please assess for each footprint, how many scenes from each individual sensor
# are located in the folders, and submit the numbers into moodle under question 1.

import os, csv

LS_list = list()            # list all subdirectories with file path and name of subfolders
file_list = list()
for root, dirs, files in os.walk("/Users/Katja/Documents/Studium/Sose18/Assignment01_data/Part01_Landsat/", topdown=False):
    for name in dirs:       # append each directory item to the list
        LS_list.append(os.path.join(root, name))
    for name in files:
        file_list.append(os.path.join(root ,name))

#print(len(LS_list))  # 5,876
#print(len(file_list))  # 116,708


# SEARCH LIST

LT04 = (len([i for i in LS_list if 'LT04' in i])) #
LT05 = (len([i for i in LS_list if 'LT05' in i])) # 2606
LE07 = (len([i for i in LS_list if 'LE07' in i])) # 2578
LC08 = (len([i for i in LS_list if 'LC08' in i])) # 671
print(LT04, LT05, LE07, LC08)


# 2.Although generally very reliable, in some rare cases not all files are being transferred by the USGS, or got lost
# during the extraction process. As a result, some scenes may be incomplete, which can have implications in later
# steps of a longer processing chain. This makes a pre-check of each individual scene necessary. The task here is to
# (a) count the number of scenes that do not have the “correct” number of files in them (caution: the number of
# files may vary between the different sensors!); and
# (b) generate a text-file, in which each corrupt scene (i.e., the entire file path) is written as an individual line.
# Submit the number of erroneous scenes into question 2 in moodle and upload a txt-file under question 3.

# LT04: 19 files
# LT05: 21 files
# LE07: 19 files
# LC08: 19 files


# get list of subdirectories with no of files contained in it
rootDir = '/Users/Katja/Documents/Studium/Sose18/Assignment01_data/Part01_Landsat/'
count_list = list()
for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
    y = (dirName, len(fileList))
    count_list.append(y)


# look for wrong no. of files in list for LS 4,7,8

L478_list = [i for i in count_list if 21 not in i]  # create list with all files that dont have 21
L_error = [i for i in L478_list if 19 not in i]     # create list with all files that dont have 21 or 19
L_error = [i for i in L_error if 1 not in i]        # ...
L_error = [i for i in L_error if 0 not in i]        #
print('\n'.join('{}\t'.format(m) for m in L_error))

err_list = [x[0] for x in L_error]                # only first part of each tuple (file path)


# for LS 5 (with 19 files?!)

L5_list = [i for i in count_list if 'LT05' in i[0]] # check if there is substring in first tuple
L5_err = [i for i in L5_list if 21 not in i]        # check if there are directories with less than 21 files
print(L5_err)


# writing text file
f = open('file.txt', 'w')
for t in err_list:
    line = ''.join(str(x) for x in t)
    f.write(line + '\n')
f.close()
