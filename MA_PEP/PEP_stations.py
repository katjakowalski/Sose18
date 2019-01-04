import time

starttime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
print("Starting process, date and time: " + starttime)
print("--------------------------------------------------------")
print("")

#####################################################################################

from osgeo import gdal, ogr, osr

########################################################################################################################
def fill_shapefile(x, y):
    '''fills shapefile with points (x,y), shapefile and fields have to be created before applying the function'''
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.AddPoint(x,y)                # use x and y of transformed sample coordinates
    feat = ogr.Feature(defn)
    feat.SetGeometry(pt)
    feat.SetField('UID', point_id)      # modify fields and values to be stored here
    feat.SetField('VCF', val_veg)
    layer.CreateFeature(feat)
    feat = None
########################################################################################################################

root_folder = "/Users/Katja/Documents/Studium/Sose18/MA_PEP/"

driver = ogr.GetDriverByName("ESRI Shapefile")

# PEP Stations
PEP_shp = driver.Open(root_folder + '/PEP_5km_dwd.shp', 1)
PEP_lyr = PEP_shp.GetLayer()

# DWD Stations
DWD_shp = driver.Open(root_folder + '/stat_dwd_5km_300px.shp',1)
DWD_lyr = DWD_shp.GetLayer()

# buffer 5 km

B_shp = driver.Open(root_folder + '/stat_dwd_b5000.shp', 1)
B_lyr = B_shp.GetLayer()


# create new shapefile
data_source = driver.CreateDataSource(root_folder + 'PEP_stat.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(3035)
layer = data_source.CreateLayer("PEP_stat", srs, ogr.wkbPoint)
defn = layer.GetLayerDefn()

# creates field in shapefile
field0 = ogr.FieldDefn("DWD_ID", ogr.OFTInteger)
layer.CreateField(field0)

field1 = ogr.FieldDefn("PEP_ID", ogr.OFTInteger)
layer.CreateField(field1)



# loop through PEP
# set spatial filter (PEP) on buffer
# set spatial filter (buffer) on DWD

pep_feat = PEP_lyr.GetNextFeature()
while pep_feat:

    pep_geom = pep_feat.geometry()
    PEP_ID = pep_feat.GetField('PEP_ID')

    B_lyr.SetSpatialFilter(pep_geom)

    B_feat = B_lyr.GetNextFeature()
    while B_feat:
        B_geom = B_feat.geometry()
        DWD_lyr.SetSpatialFilter(B_geom)
        for stat in DWD_lyr:
            DWD_stat = stat.GetField('Stations_i')
            print(DWD_stat)

            # store one feature (=PEP station) in new shapefile
            feat = ogr.Feature(defn)
            feat.SetGeometry(pep_geom)
            feat.SetField('DWD_ID', DWD_stat)  # modify fields and values to be stored here
            feat.SetField('PEP_ID', PEP_ID)
            layer.CreateFeature(feat)
            feat = None

        B_feat = B_lyr.GetNextFeature()

    pep_feat = PEP_lyr.GetNextFeature()

B_lyr.ResetReading()
PEP_lyr.ResetReading()

    # # create new shapefile
    # data_source = mem_driver.CreateDataSource(root_folder + 'stat_PEP.shp')
    # srs = osr.SpatialReference()
    # srs.ImportFromEPSG(3035)
    # layer = data_source.CreateLayer("stat_PEP", srs, ogr.wkbPolygon)
    # defn = layer.GetLayerDefn()
    # # store one feature (=country) in new shapefile
    # feat = ogr.Feature(defn)
    # feat.SetGeometry(o_geom)
    # layer.CreateFeature(feat)


#####################################################################################
# set ending time ###################################################################
print("")
endtime = time.strftime("%H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Process finished at: " + endtime)
print("")