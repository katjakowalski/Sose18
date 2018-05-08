import gdal
import glob
import os

root_folder = "/Users/Katja/Documents/Studium/Sose18/week04/Week04Assignment/"

file_list = glob.glob(os.path.join(root_folder, '*.tif'))



def rasteroverlap(file_list):
    UL_x_list = list()
    UL_y_list = list()
    LR_x_list = list()
    LR_y_list = list()
    for i in file_list:
        LS = gdal.Open(i)
        gt = LS.GetGeoTransform()
        UL_x, UL_y = gt[0], gt[3]
        LR_x = UL_x + gt[1]* LS.RasterXSize
        LR_y = UL_y + gt[5]* LS.RasterYSize
        UL_x_list.append(UL_x)
        UL_y_list.append(UL_y)
        LR_x_list.append(LR_x)
        LR_y_list.append(LR_y)
        print(os.path.basename(i), 'Upper Left X:',UL_x, 'Upper Left Y:', UL_y, 'Lower Right X:', LR_x, 'Lower Right Y:', LR_y)
    print('UL X:', max(UL_x_list),'UL Y:', min(UL_y_list))
    print('LR X:', min(LR_x_list),'LR Y:', max(LR_y_list))


rasteroverlap(file_list)



