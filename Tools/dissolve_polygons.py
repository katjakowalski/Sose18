import geopandas as gpd

def dissolve_polygons(root_folder, in_name, out_name):
    '''Function dissolves polygons by common attribute, fields have to be defined in function.
    Root folder, in- and output name have to be provided like this: '/rootfolder', '/in_or_out_name.shp' '''
    dict = {}                                                         # create a dictionary
    countries = gpd.GeoDataFrame.from_file(root_folder + in_name)          # open file w geopandas

    for i in range(len(countries)):
        id = countries.at[i, 'NAME_0']
        i_geometry = countries.at[i, 'geometry']
        # if the feature's state doesn't yet exist, create it and assign a list
        if id not in dict:
            dict[id] = []
        # append the feature to the list of features
        dict[id].append(i_geometry)

    # create a geopandas geodataframe, with columns for state and geometry
    co_dissolved = gpd.GeoDataFrame(columns=['state', 'geometry'], crs=countries.crs)

    # iterate your dictionary
    for dict, county_list in dict.items():
        # create a geoseries from the list of features
        geometry = gpd.GeoSeries(county_list)
        # use unary_union to join them, thus returning polygon or multi-polygon
        geometry = geometry.unary_union
        # set dict and geometry values
        co_dissolved.set_value(dict, 'name', dict)
        co_dissolved.set_value(dict, 'geometry', geometry)
    # save to file
    co_dissolved.to_file(root_folder + out_name, driver="ESRI Shapefile")
