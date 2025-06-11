make_city_shapes <- function(utmcrs) {
    #' @title Prepare city shapes
    #' 
    #' @description This function prepares the city shapes of the included
    #' cities.
    #' 
    #' @param utmcrs UTM projection
    #' 
    #' @author Patrick Thiel
    #' @return QS file of city shapes

    #----------------------------------------------
    # read and clean

    # empty list for storage
    city_shapes_list <- list()

    # get all file paths
    cities <- list.files(
        file.path(
            data_path,
            "cities"
        ),
        pattern = ".shp$",
        full.names = TRUE
    )

    # loop through file paths
    for (city in cities) {
        # extract city name
        base_length <- nchar(file.path(data_path, "cities"))
        city_name <- substr(city, start = base_length + 2, stop = nchar(city) - 4)

        # read data
        dta <- sf::st_read(
            city,
            quiet = TRUE
        ) |>
        sf::st_transform(utmcrs) |>
        dplyr::mutate(
            city_name = city_name,
            name = NULL,
            name_en = NULL,
            # add the size of the city
            city_size_sqkm = as.numeric(
                sf::st_area(geometry)
            ) / 1000000
        ) |>
        sf::st_cast("MULTIPOLYGON")

        # store data
        city_shapes_list[[city_name]] <- dta
    }

    # combine all and set geometry
    all_cities <- data.table::rbindlist(city_shapes_list)
    all_cities <- sf::st_set_geometry(all_cities, all_cities$geometry)

    #----------------------------------------------
    # determining longitude and latitude

    # calculate centroid of each city
    cents <- suppressWarnings(
        sf::st_centroid(all_cities)
    )

    # transform to WGS (GPS)
    cents <- sf::st_transform(cents, 4326)

    # extract coordinates
    cents_coords <- cents |>
        dplyr::select(-city_size_sqkm) |>
        dplyr::mutate(
            longitude = as.character(sf::st_coordinates(cents)[, 1]),
            latitude = as.character(sf::st_coordinates(cents)[, 2]),
            # remove everything after do to keep only broad long and lat
            longitude = stringr::str_replace(longitude, "\\..*", ""),
            latitude = stringr::str_replace(latitude, "\\..*", "")
        ) |>
        sf::st_drop_geometry()

    # merge back to city shapes
    all_cities <- all_cities |>
        merge(
            cents_coords,
            by = "city_name"
        )

    #----------------------------------------------
    # export

    qs::qsave(
        all_cities,
        file.path(
            data_path,
            "cities/cities_combined.qs"
        )
    )

    #----------------------------------------------
    # return
    return(all_cities)
}