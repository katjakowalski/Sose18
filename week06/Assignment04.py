
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

# load shapefiles
driver = ogr.GetDriverByName("ESRI Shapefile")
CO = driver.Open(root_folder + '/GER_SUI_subset.shp')
PA = driver.Open(root_folder + '/subset_WDPA.shp')

CO_lyr = CO.GetLayer()
PA_lyr = PA.GetLayer()


# select terrestrial and designated and established PAs with SQL
sql = "SELECT name, iucn_cat, status_yr, gis_area, status  " \
      "FROM subset_WDPA WHERE marine = '0' AND (status = 'Designated' OR 'Established')"
PA_subset = PA.ExecuteSQL(sql)

# load into memory to make changes to the shapefile
drv = ogr.GetDriverByName( 'Memory' )
outds = drv.CreateDataSource( '' )
PA_subset = outds.CopyLayer(PA_subset,'test2')

layer_defn = PA_subset.GetLayerDefn()

# create two new fields (country and country id):
field_defn = ogr.FieldDefn("country", ogr.OFTString) # define new field for shapefile
field_defn.SetWidth(20) # set length of string
PA_subset.CreateField(field_defn)

field_defn2 = ogr.FieldDefn("country_id", ogr.OFTInteger)
field_defn2.SetWidth(5)
PA_subset.CreateField(field_defn2)


#get field names to check if it worked
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
        i.SetField("country_id", co_id)      # set values for country and country id
        i.SetField("country", co_name)
        PA_subset.SetFeature(i)
        PA_df.append([i.GetField('name'), i.GetField('iucn_cat'),
                      i.GetField('status_yr'), i.GetField('gis_area'),
                      i.GetField('country'), i.GetField('country_id')]) # add all variables which we need to list (each 'row' is a list)
    PA_subset.SetSpatialFilter(None)


## PANDAS DATAFRAME ##

# create pandas DF with column names
field_names = list(('name', 'iucn_cat',  'status_yr', 'gis_area', 'country', 'country_id'))
PA_dff = pd.DataFrame.from_records(PA_df, columns = field_names)

# change all iucn cat Ia,b,c ... to I:
PA_dff = PA_dff.replace(to_replace = ['Ia','Ib', 'Ic', 'Id'], value = 'I') # Check if there are more categories like IIa, IIb etc.


# category ALL, by country = columns "mean area", 'max area'
all_mean = PA_dff.groupby("status_yr")['gis_area'].mean().reset_index() # mean area; group by country instead of year
all_max = PA_dff.groupby("status_yr")['gis_area'].max().reset_index() # max area; group by country instead of year

# name max? year max?

# category IUCN and by country: columns 'mean area', 'max area'
iucn_max = PA_dff.groupby(['iucn_cat', 'status_yr'])['gis_area'].max().reset_index()  # here we want to group by iucn_cat and country
iucn_mean = PA_dff.groupby(['iucn_cat', 'status_yr'])['gis_area'].mean().reset_index()

# number of PA's per country and per IUCN category + country
iucn_count = PA_dff.groupby(['iucn_cat', 'status_yr']).count().reset_index()
all_count = PA_dff.groupby(['status_yr']).count().reset_index()
#print(iucn_count)
#print(all_count)

# max gis area per country and per iucn cat with all variables
print(PA_dff.loc[PA_dff.reset_index().groupby(['country'])['gis_area'].idxmax()])
print(PA_dff.loc[PA_dff.reset_index().groupby(['country', 'iucn_cat'])['gis_area'].idxmax()])