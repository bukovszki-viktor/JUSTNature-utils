combine_all_resources <- function(
    city_pop,
    city_shapes,
    aggregated_city_gdp,
    education,
    transport,
    tourism,
    streets,
    railroads,
    waterbodies,
    greenspace
) {
    #' @title Combining all information
    #' 
    #' @description This function takes all the prepared information at the
    #' city-level and combines it in one table. It also compares each city
    #' with each other to find candidates of cities that match in key 
    #' characteristics.
    #' 
    #' @param city_pop Population at city-level
    #' @param city_shapes Borders of the cities
    #' @param aggregated_city_gdp GDP at city-level
    #' @param education Education opportunities at city-level
    #' @param transport Transportation density at city-level
    #' @param tourism Tourism spots at city-level
    #' @param streets Length of street network at city-level
    #' @param railroads Length of railroad network at city-level
    #' @param waterbodies Area of waterbodies at city-level
    #' @param greenspace Area of greenspace at city-level
    #' 
    #' @author Patrick Thiel
    #' @return DataFrame with city information and candidates
    
    #----------------------------------------------
    # merge all information

    all_data <- city_pop |>
        # merge city size and long/lat info
        merge(
            city_shapes |>
                sf::st_drop_geometry(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge GDP information
        merge(
            # keep only city name and relative GDP
            aggregated_city_gdp |>
                dplyr::select(city_name, rel_total_gdp_per_capita),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge education opportunities
        merge(
            education |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keep only total count
                dplyr::select(city_name, total_educ_per_tsd_pp) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge public transportation
        merge(
            transport |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keeply only total count
                dplyr::select(city_name, total_trans_per_tsd_pp) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge tourism information
        merge(
            tourism |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keep only total count
                dplyr::select(city_name, total_tourism_per_tsd_pp) |>
                # drop NAs because these are cities that are not in the project
                dplyr::filter(!is.na(total_tourism_per_tsd_pp)) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge street length
        merge(
            streets |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keep only length
                dplyr::select(city_name, rel_total_street_length) |>
                # drop NAs because these are cities that are not in the project
                dplyr::filter(!is.na(rel_total_street_length)) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge railroad length
        merge(
            railroads |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keep only length
                dplyr::select(city_name, rel_total_railroad_length) |>
                # drop NAs because these are cities that are not in the project
                dplyr::filter(!is.na(rel_total_railroad_length)) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge waterbodies areas
        merge(
            waterbodies |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keep only area
                dplyr::select(city_name, total_water_area_sqkm) |>
                # drop NAs because these are cities that are not in the project
                dplyr::filter(!is.na(total_water_area_sqkm)) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # merge greenspace areas
        merge(
            greenspace |>
                # keep only values of 2020
                dplyr::filter(year == 2020) |>
                # keep only area
                dplyr::select(city_name, total_green_area_sqkm) |>
                # drop NAs because these are cities that are not in the project
                dplyr::filter(!is.na(total_green_area_sqkm)) |>
                # keep only one value per city
                dplyr::distinct(),
            by = "city_name",
            all.x = TRUE
        ) |>
        # tranfrom long and lat into numbers
        dplyr::mutate(
            longitude = as.numeric(longitude),
            latitude = as.numeric(latitude)
        )

    #----------------------------------------------
    # define classifier

    # define percent threshold
    # threshold +/- the city values are comparable
    threshold <- 0.2

    # function classifies a list of candidates that are comparable within each
    # column
    comparison <- function(col) {
        lapply(
            # loop through all cities row-wise
            unique(all_data$city_name),
            FUN = function(city) {
                # row to consider (i.e. the specific city)
                row_city <- all_data |>
                    dplyr::filter(city_name == city)

                # go through rows in the col and check whether specific city
                # value falls into an interval of another city for that col
                # threshold for interval: 20%
                candidates_logical <- apply(
                    all_data,
                    1,
                    FUN = function(x) {
                        comparison_col <- as.numeric(x[col])
                        # checks whether city-specific value falls into the
                        # interval of another city
                        # performed for each col separately
                        data.table::between(
                            row_city[, col],
                            lower = comparison_col - (comparison_col * threshold),
                            upper = comparison_col + (comparison_col * threshold)
                        )
                    }
                )
            
                # subset city candidates that meet condition i.e. fall into
                # interval
                candidates <- all_data$city_name[candidates_logical]

                # turn city candidates which is a vector right now, into a
                # comma-separated string
                candidates_comma <- paste(candidates, collapse = ", ")

                # assign list of comma-separated candidates to specific city
                row_city$placeholder <- candidates_comma

                # rename placehold variable to make it column-specific
                names(row_city)[names(row_city) == "placeholder"] <- paste0("candidates_", col)
                
                # return city data
                return(row_city)
            }
        )
    }

    # empty list for storage
    city_candidates_list <- list()

    # define variables of interest
    # exclude city names because they are not numeric and are the ID
    # exclude long/ lat (for now) because the comparison would be too restrictive
    cols_of_interest <- all_data |>
        select(-c(city_name, longitude, latitude)) |>
        names()

    # loop through all variables of interest
    for (col in cols_of_interest) {
        # perform comparison for each column
        column_output <- comparison(col = col)

        # bind all cities together again
        city_output <- data.table::rbindlist(column_output)

        # only keep city name (ID) and the candidates lists
        final_output <- city_output |>
            dplyr::select(city_name, contains("candidates"))

        # store result
        city_candidates_list[[col]] <- final_output
    }

    # merge all the results based on city name
    candidates_table <- city_candidates_list |>
        purrr::reduce(
            left_join,
            by = "city_name"
        )

    # define columns names of candidates
    cols <- candidates_table |>
        dplyr::select(-city_name) |>
        names()

    # create new column where all the candidates are pasted together
    candidates_table$all_candidates <- apply(
        # only keep variables of interest (i.e. candidates columns)
        candidates_table |>
            dplyr::select(cols),
        1,
        paste,
        collapse = ", "
    )

    # loop through all cities to combine candidates information in one single
    # column
    candidates_list <- apply(
        candidates_table,
        1,
        FUN = function(row_data) {
            # separate candidates list by coma
            cities <- stringr::str_split_1(row_data["all_candidates"], ",")
            #print(cities)

            # remove white space
            cities <- stringr::str_trim(cities)

            # count the city candidates
            counts <- as.data.frame(
                table(cities)
            )

            # remove count of own city (i.e. avoid matching city to itself)
            # keep only cities with maximum frequencies, i.e. highest match
            counts <- counts |>
                dplyr::filter(cities != unique(row_data["city_name"])) |>
                dplyr::filter(Freq == max(Freq))

            # construct output dataframe
            output <- as.data.frame(
                cbind(
                    city_name = row_data["city_name"],
                    candidates = paste(unique(counts$cities), collapse = ", "),
                    candidates_counts =unique(counts$Freq)
                )
            ) |>
            # replace no match information
            dplyr::mutate(
                candidates = dplyr::case_when(
                    candidates == "NA" ~ "no match",
                    TRUE ~ candidates
                ),
                candidates_counts = as.numeric(candidates_counts),
                candidates_counts = dplyr::case_when(
                    candidates == "no match" ~ 0,
                    TRUE ~ candidates_counts
                )
            )
        }
    )

    # combine information into dataframe
    candidates <- data.table::rbindlist(candidates_list)

    #----------------------------------------------
    # combine original data table with comparison findings

    all_data <- all_data |>
        merge(
            candidates,
            by = "city_name",
            all.x = TRUE
        )

    #----------------------------------------------
    # export

    data.table::fwrite(
        all_data,
        file.path(
            data_path,
            "comparison/cities_and_candidates.csv"
        ),
        na = "NA"
    )

    #----------------------------------------------
    # return
    return(all_data)
}