
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

# SEARCH LIST

LT04 = [i for i in LS_list if 'LT04' in i]
LT05 = [i for i in LS_list if 'LT05' in i]
LE07 = [i for i in LS_list if 'LE07' in i]
LC08 = [i for i in LS_list if 'LC08' in i]
#print(len(LT04))
#print(len(LT05))
#print(len(LE07))
#print(len(LC08))


#228_077
LT04_228_077 = len([i for i in LT04 if '228077' in i])
LT05_228_077 = len([i for i in LT05 if '228077' in i])
LE07_228_077 = len([i for i in LE07 if '228077' in i])
LC08_228_077 = len([i for i in LC08 if '228077' in i])

print('228_077: ', LT04_228_077, LT05_228_077, LE07_228_077, LC08_228_077)

#228_078
LT04_228_078 = len([i for i in LT04 if '228078' in i])
LT05_228_078 = len([i for i in LT05 if '228078' in i])
LE07_228_078 = len([i for i in LE07 if '228078' in i])
LC08_228_078 = len([i for i in LC08 if '228078' in i])

print('228_078: ', LT04_228_078, LT05_228_078, LE07_228_078, LC08_228_078)

#228_079
LT04_228_079 = len([i for i in LT04 if '228079' in i])
LT05_228_079 = len([i for i in LT05 if '228079' in i])
LE07_228_079 = len([i for i in LE07 if '228079' in i])
LC08_228_079 = len([i for i in LC08 if '228079' in i])

print('228_079: ', LT04_228_079, LT05_228_079, LE07_228_079, LC08_228_079)

#229_077
LT04_229_077 = len([i for i in LT04 if '229077' in i])
LT05_229_077 = len([i for i in LT05 if '229077' in i])
LE07_229_077 = len([i for i in LE07 if '229077' in i])
LC08_229_077 = len([i for i in LC08 if '229077' in i])

print('229_077: ', LT04_229_077, LT05_229_077, LE07_229_077, LC08_229_077)

#229_078
LT04_229_078 = len([i for i in LT04 if '229078' in i])
LT05_229_078 = len([i for i in LT05 if '229078' in i])
LE07_229_078 = len([i for i in LE07 if '229078' in i])
LC08_229_078 = len([i for i in LC08 if '229078' in i])

print('229_078: ', LT04_229_078, LT05_229_078, LE07_229_078, LC08_229_078)

#229_079
LT04_229_079 = len([i for i in LT04 if '229079' in i])
LT05_229_079 = len([i for i in LT05 if '229079' in i])
LE07_229_079 = len([i for i in LE07 if '229079' in i])
LC08_229_079 = len([i for i in LC08 if '229079' in i])

print('229_079: ', LT04_229_079, LT05_229_079, LE07_229_079, LC08_229_079)

#230_077
LT04_230_077 = len([i for i in LT04 if '230077' in i])
LT05_230_077 = len([i for i in LT05 if '230077' in i])
LE07_230_077 = len([i for i in LE07 if '230077' in i])
LC08_230_077 = len([i for i in LC08 if '230077' in i])

print('230_077: ',LT04_230_077, LT05_230_077, LE07_230_077, LC08_230_077)

#230_078
LT04_230_078 = len([i for i in LT04 if '230078' in i])
LT05_230_078 = len([i for i in LT05 if '230078' in i])
LE07_230_078 = len([i for i in LE07 if '230078' in i])
LC08_230_078 = len([i for i in LC08 if '230078' in i])

print('230_078: ',LT04_230_078, LT05_230_078, LE07_230_078, LC08_230_078)

#230_079
LT04_230_079 = len([i for i in LT04 if '230079' in i])
LT05_230_079 = len([i for i in LT05 if '230079' in i])
LE07_230_079 = len([i for i in LE07 if '230079' in i])
LC08_230_079 = len([i for i in LC08 if '230079' in i])

print('230_079: ', LT04_230_079, LT05_230_079, LE07_230_079, LC08_230_079)

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
#print('\n'.join('{}\t'.format(m) for m in L_error))

err_list = [x[0] for x in L_error]                # only first part of each tuple (file path)


# for LS 5 (with 19 files?!)

L5_list = [i for i in count_list if 'LT05' in i[0]] # check if there is substring in first tuple
L5_err = [i for i in L5_list if 21 not in i]        # check if there are directories with less than 21 files
#print(L5_err)                                       # empty


# writing text file
f = open('file.txt', 'w')
for t in err_list:
    line = ''.join(str(x) for x in t)
    f.write(line + '\n')
f.close()


#1. The number of SHP-files and the number of raster-files that are in the folder (again: for the purpose of data
# storage, these are only dummy files). Please make sure that you only count the number of layers and not the number
# of files (e.g., a SHP-file is composed of more than one file, the same may be true for raster-files). Once you have
# your results, please upload them for both layer types (vector and raster) into moodle under question 4.

# list all files in the directory
gd_list = list()
for root, dirs, files in os.walk("/Users/Katja/Documents/Studium/Sose18/Assignment01_data/Part02_GIS-Files/", topdown=False):
    for name in files:
        gd_list.append(os.path.join( name))

# list all items in gd_list that end with .shp
shp_list = list()
for i in gd_list:
    x=i
    if x.endswith('.shp'):
        shp_list.append(x)
#print('\n'.join('{}\t'.format(m) for m in shp_list))
#print(shp_list)

# list all items in gd_list that end with .tif
ras_list = list()
for i in gd_list:
    x=i
    if x.endswith('.tif'):
        ras_list.append(x)
#print(len(ras_list))


# list all items that end with dbf, shx, shp and prj
compl_list = list()
for i in gd_list:
    x = i
    if x.endswith('.dbf') or x.endswith('.shx') or x.endswith('.shp') or x.endswith('.prj'):
        compl_list.append(x)

compl_list = [i for i in compl_list if '.tif' not in i] # remove items that still contain .tif


# create list without file extensions
raw_list = list()
for i in compl_list:
    x=i
    name,ext = os.path.splitext(x)
    raw_list.append(name)

# count duplicates in list without extensions and write to new list
dupl_list = list()
for i in raw_list:
    x=i
    sum_i = raw_list.count(i)
    y = (i, sum_i)
    if y not in dupl_list:
        dupl_list.append(y)


#print('\n'.join('{}\t'.format(m) for m in dupl_list))

# only select files with more than 3 (=complete) occurences
incompl_list = [i for i in dupl_list if i[1]< 4 ]
sorted(incompl_list)
#print('\n'.join('{}\t'.format(m) for m in incompl_list))



f = open('incomplete_shape.txt', 'w')
for t in incompl_list:
    line = ''.join(str(x) for x in t)
    f.write(line + '\n')
f.close()