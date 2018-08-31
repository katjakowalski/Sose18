import geopandas as gpd

def dissolve_polygons(root_folder, in_name, out_name):
    '''Function dissolves polygons by common attribute, fields have to be defined in function.
    Root folder, in- and output name have to be provided like this: '/rootfolder', '/in_or_out_name.shp' '''
    states = {}                                                         # create a dictionary
    counties = gpd.GeoDataFrame.from_file(root_folder + in_name)          # open file w geopandas

    for i in range(len(counties)):
        state_id = counties.at[i, 'NAME_0']
        county_geometry = counties.at[i, 'geometry']
        # if the feature's state doesn't yet exist, create it and assign a list
        if state_id not in states:
            states[state_id] = []
        # append the feature to the list of features
        states[state_id].append(county_geometry)

    # create a geopandas geodataframe, with columns for state and geometry
    states_dissolved = gpd.GeoDataFrame(columns=['state', 'geometry'], crs=counties.crs)

    # iterate your dictionary
    for state, county_list in states.items():
        # create a geoseries from the list of features
        geometry = gpd.GeoSeries(county_list)
        # use unary_union to join them, thus returning polygon or multi-polygon
        geometry = geometry.unary_union
        # set your state and geometry values
        states_dissolved.set_value(state, 'state', state)
        states_dissolved.set_value(state, 'geometry', geometry)

    # save to file
    states_dissolved.to_file(root_folder + out_name, driver="ESRI Shapefile")
