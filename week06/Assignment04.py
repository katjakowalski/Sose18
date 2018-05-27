
# SQL query:
#   MARINE == 0
#   STATUS == established OR designated

# set spatial filter (intersect) loop over countries and append variables of PA's

# needed variables:
#   country
#   MARINE      (string)    [0 (terrestrial),1 (coastal),2 (marine)]
#   IUCN_CAT    (string)    [I-IV, not reported, not applicable]
#   NAME        (string)
#   STATUS_YR   (string)
#   GIS_AREA    (double)
#   STATUS      (string)    [only designated & established]

###############################################################################################
from osgeo import gdal, ogr, osr
import pandas as pd
import os
import numpy as np
import geopandas as gpd


root_folder = '/Users/Katja/Documents/Studium/Sose18/week06/'
os.chdir('/Users/Katja/Documents/Studium/Sose18/week06/')

driver = ogr.GetDriverByName("ESRI Shapefile")
CO = driver.Open(root_folder + '/GER_SUI_subset.shp')
PA = driver.Open(root_folder + '/subset_WDPA.shp')

CO_lyr = CO.GetLayer()
PA_lyr = PA.GetLayer()

sql = "SELECT name, iucn_cat, status_yr, gis_area, status  " \
      "FROM subset_WDPA WHERE marine = '0' AND (status = 'Designated' OR 'Established')"
PA_subset = PA.ExecuteSQL(sql)

# create prj file
spatialRef = osr.SpatialReference()
spatialRef.ImportFromEPSG(4326)
spatialRef.MorphToESRI()
file = open('PA_subset.prj', 'w')
file.write(spatialRef.ExportToWkt())
file.close()

# write subset to disk
drv = ogr.GetDriverByName( 'ESRI Shapefile' )
outds = drv.CreateDataSource( "PA_subset.shp" )
outlyr = outds.CopyLayer(PA_subset,'PA_subset')

# close shapefile
PA_subset = None
del outlyr,outds

# open subset again
PA_in = driver.Open(root_folder + '/PA_subset.shp')
PA_subset = PA_in.GetLayer()

# add fields for country and country id
layer_defn = PA_subset.GetLayerDefn()
field_defn = ogr.FieldDefn("country", ogr.OFTString) # define new field for shapefile
field_defn2 = ogr.FieldDefn("country_id", ogr.OFTString)
PA_subset.CreateField(field_defn)

#get field names
field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
print(field_names)


# loop through country layer, set spatial filter and then loop through PA layer and set variable to country
PA_df = list()
for country in CO_lyr:
    co_geom = country.geometry().Clone()  # duplicate geometry of respective country
    co_name = country.GetField('NAME_0')  # get country name
    co_id = country.GetField('ID_0')
    PA_subset.SetSpatialFilter(co_geom) # set spatial filter for country
    print(co_name, PA_subset.GetFeatureCount())
    for i in PA_subset:
        PA_subset.SetFeature(i)
        i.SetField("country_id", co_name)       # I dont know if it works to set two fields at once, otherwise the three lines have to be copied for each field
        i.SetField("country", co_id)
        PA_subset.SetFeature(i)
        PA_df.append([i.GetField('name'), i.GetField('iucn_cat'), i.GetField('status_yr'), i.GetField('gis_area')]) # we need to get country and country id here as well
    PA_subset.SetSpatialFilter(None)

#print(PA_df)

## PANDAS DATAFRAME ##

field_names = list(('name', 'iucn_cat',  'status_yr', 'gis_area'))
PA_dff = pd.DataFrame.from_records(PA_df, columns = field_names)

# change all iucn cat Ia,b,c ... to I


PA_dff = PA_dff.replace(to_replace = ['Ia','Ib', 'Ic', 'Id'], value = 'I') # check what categories have to replaced as well


# category ALL, by country = columns "mean area", 'max area',
all_mean = PA_dff.groupby("status_yr")['gis_area'].mean().reset_index() # mean area; group by country instead of year
all_max = PA_dff.groupby("status_yr")['gis_area'].max().reset_index() # max area; group by country instead of year

# name max? year max?

# category IUCN and by country: columns 'mean area', 'max area'
iucn_max = PA_dff.groupby(['iucn_cat', 'status_yr'])['gis_area'].max().reset_index()  # here we want to group by iucn_cat and country
iucn_mean = PA_dff.groupby(['iucn_cat', 'status_yr'])['gis_area'].mean().reset_index()

# number of PA's per country and per IUCN category + country
iucn_count = PA_dff.groupby(['iucn_cat', 'status_yr']).count().reset_index()
all_count = PA_dff.groupby(['status_yr']).count().reset_index()
print(iucn_count)
print(all_count)

PA_dff.loc[PA_dff.reset_index().groupby(['status_yr'])['to_date'].idxmax()]