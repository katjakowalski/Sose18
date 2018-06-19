import ogr
baseFolder = "/Users/Katja/Documents/Studium/Sose18/week10/Assignment08_data/"
parcels = ogr.Open(baseFolder + "Parcels.shp", 1)
parcels_lyr = parcels.GetLayer()

roads = ogr.Open(baseFolder + "Roads.shp", 1)
roads_lyr = roads.GetLayer()

thp = ogr.Open(baseFolder + "TimberHarvestPlan.shp", 1)
thp_lyr = thp.GetLayer()

parcels_cs = parcels_lyr.GetSpatialRef()
feat = parcels_lyr.GetNextFeature()
while feat:
    geom = feat.GetGeometryRef()
    apn = feat.GetField('APN')
    #
    # ############################################################# #
    ######### Group 3 ############

    # Set filter for relevant road types
    roads_lyr.SetAttributeFilter("FUNCTIONAL IN ('Local Roads', 'Private')")
    # loop through two categories
    road_feat = roads_lyr.GetNextFeature()
    while road_feat:
        functional = road_feat.GetField('FUNCTIONAL')
        geom_roads = road_feat.GetGeometryRef()
        intersection = geom.Intersection(geom_roads)        # calculate intersection of road types and individual parcel
        length = intersection.Length()                      # get length of intersection
        #print(functional, length)
        road_feat = roads_lyr.GetNextFeature()
    area_parcel = geom.GetArea()

    # timber harvest plan > only use one year (overlapping geometries)
    thp_lyr.SetAttributeFilter("THP_YEAR = '1999'")
    thp_lyr.SetSpatialFilter(geom)                  # Set filter for parcel
    thp_feat = thp_lyr.GetNextFeature()
    area_parcel = geom.GetArea()                    # area of parcel
    thp_list = []

    # loop through selected features
    while thp_feat:
        geom_thp = thp_feat.GetGeometryRef()
        intersect_thp = geom.Intersection(geom_thp) # intersection of parcel and selected thp features
        area = intersect_thp.GetArea()              # area of intersected thp feature
        thp_list.append(area)                       # add area of thp feature to list
        thp_feat = thp_lyr.GetNextFeature()

    thp_sum = sum(thp_list)                         # sum up all thp features in parcel
    thp_prop = thp_sum/area_parcel
    print(thp_prop)

    # ############################################################# #
    #
    feat = parcels_lyr.GetNextFeature()
