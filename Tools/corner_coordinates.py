from osgeo import gdal

def corner_coordinates(file_list):
    '''returns corner coordinates of all raster input files'''
    UL_x_list = []
    UL_y_list = []
    LR_x_list = []
    LR_y_list = []
    for i in file_list:
        LS = gdal.Open(i)
        gt = LS.GetGeoTransform()
        UL_x, UL_y = gt[0], gt[3]
        LR_x = UL_x + gt[1] * LS.RasterXSize
        LR_y = UL_y + gt[5] * LS.RasterYSize
        UL_x_list.append(UL_x)
        UL_y_list.append(UL_y)
        LR_x_list.append(LR_x)
        LR_y_list.append(LR_y)
    x_min = max(UL_x_list)
    x_max = min(LR_x_list)
    y_min = min(LR_y_list)
    y_max = max(UL_y_list)
    return(x_min, x_max, y_min, y_max)