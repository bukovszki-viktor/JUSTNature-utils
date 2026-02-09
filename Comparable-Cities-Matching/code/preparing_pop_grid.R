preparing_pop_grid <- function(file_grid_pop, utmcrs) {
    #' @title Preparation of population grid
    #' 
    #' @description This function prepares the population based on grids.
    #' 
    #' @param file_grid_pop File path to grid population data set
    #' @param utmcrs UTM projection
    #' 
    #' @author Patrick Thiel
    #' @return QS file with population on grid-level

    #----------------------------------------------
    # read data

    pop_grid <- st_read(
        file_grid_pop,
        quiet = TRUE
    )

    #----------------------------------------------
    # clean
    
    # keep only necessary columns
    pop_grid_prep <- pop_grid |>
        select(pop_2018 = TOT_P_2018, grid_id = GRD_ID, geometry) |>
        st_transform(utmcrs)

    #----------------------------------------------
    # export as QS

    qs::qsave(
        pop_grid_prep,
        file.path(
            data_path,
            "population_grids/population_grids_europe.qs"
        )
    )

    #----------------------------------------------
    # return
    
    return(pop_grid_prep)
}