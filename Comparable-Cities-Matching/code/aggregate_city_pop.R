aggregate_city_pop <- function(city_grid_pop) {
    #' @title Aggregating city population
    #' 
    #' @description Thsi function aggregates the given grid-level city
    #' population to the city-level.
    #' 
    #' @param city_grid_pop Grid-level city population
    #' 
    #' @author Patrick Thiel
    #' @return File with city-level population
    
    #----------------------------------------------
    # aggregate population at city-level

    aggregated_pop <- city_grid_pop |>
        st_drop_geometry() |>
        group_by(city_name) |>
        summarise(
            total_pop = sum(pop_2018, na.rm = TRUE)
        ) |>
        as.data.frame()

    #----------------------------------------------
    # export

    data.table::fwrite(
        aggregated_pop,
        file.path(
            data_path,
            "population/population_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(aggregated_pop)
}

