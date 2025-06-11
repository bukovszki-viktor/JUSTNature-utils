make_city_pop <- function(grid_pop, city_grids) {
    #' @title Preparing city population
    #' 
    #' @description This function intersects the population grids with the
    #' geographical information of cities in the project (on grid level).
    #' 
    #' @param grid_pop Grid populaton
    #' @param city_grids Grids of included cities
    #' 
    #' @author Patrick Thiel
    #' @return QS file with all city grids

    #----------------------------------------------
    # merge city grids and population grids

    city_pop_grids <- merge(
        city_grids |> sf::st_drop_geometry(),
        grid_pop,
        by = "grid_id",
        all.x = TRUE
    )

    # make sure that merged data set and input city data set have same length
    tar_assert_true(
        all.equal(
            nrow(city_pop_grids),
            nrow(city_grids)
        )
    )

    # set geometry
    city_pop_grids <- sf::st_set_geometry(
        city_pop_grids,
        city_pop_grids$geometry    
    )

    #----------------------------------------------
    # export

    qs::qsave(
        city_pop_grids,
        file.path(
            data_path,
            "grids/population_grids_city.qs"
        )
    )

    #----------------------------------------------
    return(city_pop_grids)
}