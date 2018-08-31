from osgeo import gdal


def return_raster_values(x1, y1, tile_list):
    '''returns raster values at x and y coordinates, define rows and cols of raster files in line 12'''
    dat_list = []
    for i in tile_list:                                             # loop through all tiles
        tile = gdal.Open(i)
        gt_tile = tile.GetGeoTransform()                            # get information from tile
        px_tile = int((x1 - gt_tile[0]) / gt_tile[1])               # calculate absolute raster coordinates of sample
        py_tile = int((y1 - gt_tile[3]) / gt_tile[5])
        if px_tile < 1000 and px_tile >= 0 and py_tile < 1000 and py_tile >= 0:     # if pt lies within tile
            data = tile.ReadAsArray()                               # get array from raster
            if tile.RasterCount == 1:                               # extract values from raster depending on number of bands in raster
                val_band = data[py_tile, px_tile]                   # extract raster value from single band
                dat_list.append(val_band)                          # to include id, filename, band: [point_id, os.path.basename(os.path.normpath(i)),1,
            else:
                for x in range(tile.RasterCount):                   # extract raster value from each band
                    val_bands = data[x,py_tile, px_tile]
                    dat_list.append(val_bands)                      # to include id, filename, band: [point_id, os.path.basename(os.path.normpath(i)), x,
    return(dat_list)