make_city_grids <- function(inspire_grid, city_shapes) {
    #' @title Preparing city grids
    #' 
    #' @description This function intersects the INSPIRE grids
    #' with the geographical information of cities in the project.
    #' 
    #' @param inspire_grid INSPIRE grids for Europe
    #' @param city_shapes Shapes of included cities
    #' 
    #' @author Patrick Thiel
    #' @return QS file with all city grids

    #----------------------------------------------
    # intersect city shapes and grids

    # get all city names
    cities <- unique(city_shapes$city_name)

    # empty list for storage
    city_grids_list <- list()

    # loop through all cities
    for (city in cities) {
        # get city shape
        city_shape <- city_shapes |>
            dplyr::filter(city_name == city)

        # intersect city shape with grids
        suppressWarnings(
            joint <- sf::st_join(
                inspire_grid,
                city_shape,
                left = TRUE,
                largest = TRUE
            )
        )

        joint <- joint |>
            dplyr::filter(!is.na(city_name)) |>
            dplyr::relocate(city_name, .after = grid_id)

        # store data
        city_grids_list[[city]] <- joint
    }

    # combine all and set geometry
    all_cities <- data.table::rbindlist(city_grids_list)
    all_cities <- sf::st_set_geometry(all_cities, all_cities$geometry)
    
    #----------------------------------------------
    # export

    qs::qsave(
        all_cities,
        file.path(
            data_path,
            "grids/city_grids.qs"
        )
    )

    #----------------------------------------------
    return(all_cities)
}