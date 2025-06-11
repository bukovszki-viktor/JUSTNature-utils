preparing_inspire_grid <- function(file_grid_pop, utmcrs) {
    #' @title Preparation of INSPIRE grid
    #' 
    #' @description This function prepares the grid shapes according to INSPIRE.
    #' 
    #' @param file_grid_pop File path to grid population data set
    #' @param utmcrs UTM projection
    #' 
    #' @note This function uses the population grid even though population
    #' values are not of interest here. The data set comes with the geographical
    #' information of INSPIRE grids though.
    #' 
    #' @author Patrick Thiel
    #' @return QS file with grid information

    #----------------------------------------------
    # read data

    pop_grid <- st_read(
        file_grid_pop,
        quiet = TRUE
    )

    #----------------------------------------------
    # clean
    
    # keep only necessary columns
    grid_prep <- pop_grid |>
        select(grid_id = GRD_ID, geometry) |>
        st_transform(utmcrs)

    #----------------------------------------------
    # export as QS

    qs::qsave(
        grid_prep,
        file.path(
            data_path,
            "grids/inspire_grids_europe.qs"
        )
    )

    #----------------------------------------------
    # return
    
    return(grid_prep)
}