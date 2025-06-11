extracting_nbs_cities <- function() {
    #' @title Extracting NBS cities
    #' 
    #' @description This function extracts from the given database
    #' cities that implemented a NBS strategy and lay within the
    #' European Union.
    #' 
    #' @author Patrick Thiel
    #' @return Returns file with city list
    
    #----------------------------------------------
    # read data
    
    nbs_cities <- openxlsx::read.xlsx(
        file.path(
            data_path,
            "benchmark_database/3.1 Benchmark Database.xlsx"
        ),
        sheet = "NbS Intervention database"
    )

    #----------------------------------------------
    # clean cities

    nbs_cities_prep <- nbs_cities |>
        dplyr::select(1, 17) |>
        slice(2:nrow(nbs_cities)) |>
        rename("city" = 1, "country" = 2) |>
        # filter out unknown cities
        filter(city != "?") |>
        mutate(
            # add or replace country
            country = case_when(
                city == "Leipzig" ~ "Germany",
                city == "Bratislava" ~ "Slovakia",
                TRUE ~ country
            ),
            # rename city
            city = case_when(
                city == "Tampare" ~ "Tampere",
                TRUE ~ city
            )
        ) |>
        # exclude for now interventions that are not within one clearly defined
        # city
        filter(
            !city %in% c(
                "Valley of Gudbrandsdalen", "Serchio River Basin",
                "Tullstorp Stream", "Between Cannes and Nice",
                "Köngäs village", "Kiskunsag"
            )
        ) |>
        # exclude duplicates
        distinct(city, .keep_all = TRUE) |>
        # exclude non-European countries
        filter(
            !country %in% c(
                "Egypt", "England", "United Kingdom",
                "Kuwait", "South Africa", "Israel"
            )
        )

    #----------------------------------------------
    # export

    data.table::fwrite(
        nbs_cities_prep,
        file.path(
            data_path,
            "benchmark_database/benchmark_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(nbs_cities_prep)
}