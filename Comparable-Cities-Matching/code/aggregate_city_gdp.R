aggregate_city_gdp <- function(city_gdp) {
    #' @title Aggregating city GDP
    #' 
    #' @description This function aggregates the given grid-level city GDP to
    #' the city-level.
    #' 
    #' @param city_gdp Grid-level city GDP
    #' 
    #' @author Patrick Thiel
    #' @return File with city-level GDP
    
    #----------------------------------------------
    # specify GDP per capita on Europe-level
    # Eurostat Info "Real GDP per capita" (Code: SDG_08_10)
    # info from: https://ec.europa.eu/eurostat/databrowser/view/sdg_08_10/default/table
    # use info for 2015 European Union (with 28 states since UK was still member
    # in 2015)
    # 2015 because the city level data is from 2015 as well
    # Accessed: 15.08.2023 (PT)
    
    europe_gdp <- 26710

    #----------------------------------------------
    # aggregate GDP at city-level

    aggregated_gdp <- city_gdp |>
        st_drop_geometry() |>
        group_by(city_name) |>
        summarise(
            total_gdp = sum(total_gdp, na.rm = TRUE),
            total_pop = sum(pop_2018, na.rm = TRUE),
            total_gdp_per_capita = total_gdp / total_pop
        ) |>
        mutate(
            rel_total_gdp_per_capita = (total_gdp_per_capita / europe_gdp) * 100
        ) |>
        as.data.frame()

    #----------------------------------------------
    # export

    data.table::fwrite(
        aggregated_gdp,
        file.path(
            data_path,
            "gdp/gdp_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(aggregated_gdp)
}