make_streets <- function(city_shapes, utmcrs) {
    #' @title Preparing street network
    #' 
    #' @description This function aggregates the street network on the
    #' city-level by year. It also plots the raw data. Year for plotting: 2020
    #' 
    #' @param city_shapes Shape file with city borders
    #' @param utmcrs UTM projection
    #' 
    #' @author Patrick Thiel
    #' @return Summarised street network on city-level
    
    #----------------------------------------------
    # read street data

    streets <- sf::st_read(
        file.path(
            data_path,
            "streets/streets.shp"
        ),
        quiet = TRUE
    )

    #----------------------------------------------
    # transform and adjust city names
    
    streets <- streets |>
        sf::st_transform(utmcrs) |>
        dplyr::rename(city_name = city) |>
        dplyr::mutate(
            city_name = case_when(
                city_name == "Khania" ~ "Chania",
                city_name == "Merano" ~ "Meran",
                TRUE ~ city_name
            ),
            # make names lower-case
            city_name = tolower(city_name)
        )

    #----------------------------------------------
    # summarise by city, year and tag

    streets_sum <- streets |>
        # add length of each street segment
        dplyr::mutate(
            street_length_km = as.numeric(
                sf::st_length(geometry)
            ) / 1000
        ) |>
        sf::st_drop_geometry() |>
        dplyr::group_by(city_name, year, used_tag) |>
        # calcualate the length of the network for each street type
        dplyr::summarise(
            total_street_length_km = sum(street_length_km)
        )

    #----------------------------------------------
    # summarise by city and year

    streets_sum_total <- streets_sum |>
        dplyr::group_by(city_name, year) |>
        dplyr::summarise(
            total_street_length_km = sum(total_street_length_km)
        ) |>
        # merge city information
        merge(
            city_shapes |>
                # remove geometry
                sf::st_drop_geometry() |>
                # keep only name and sizr
                dplyr::select(city_name, city_size_sqkm),
            by = "city_name",
            all.x = TRUE
        ) |>
        # calculate the relative length of the network
        # relative to the city size
        dplyr::mutate(
            rel_total_street_length = total_street_length_km /
                city_size_sqkm
        )

    #----------------------------------------------
    # plot raw data

    # get all city names
    cities <- unique(city_shapes$city_name)

    # define colors
    # randomly selecting a set of colors
    cols <- MetBrewer::met.brewer(name = "Redon", n = 12)
    set.seed(12345)
    cols <- sample(
        cols,
        length(unique(streets$used_tag)),
        replace = FALSE
    )

    # define labels
    labs <- stringr::str_to_title(unique(streets$used_tag))

    # loop through cities
    for (ct in cities) {
        # generate map
        map <- ggplot()+
            geom_sf(
                data = streets |>
                    # filter for plotting year (2020)
                    # filter for specific city
                    dplyr::filter(year == 2020 & city_name == ct),
                mapping = aes(
                    geometry = geometry,
                    col = used_tag
                ),
                linewidth = 1
            )+
            geom_sf(
                data = city_shapes |>
                    # filter for specific city
                    dplyr::filter(city_name == ct),
                mapping = aes(geometry = geometry),
                fill = NA,
                linewidth = 0.8,
                col = "black"
            )+
            scale_color_manual(
                name = "Feature type",
                values = cols,
                labels = labs 
            )+
            theme_void()

        filename <- paste0("streets_2020_", ct, ".png")
        ggsave(
            plot = map,
            file.path(
                output_path,
                "maps/streets",
                filename
            ),
            dpi = owndpi
        )
    }

    #----------------------------------------------
    # export

    data.table::fwrite(
        streets_sum_total,
        file.path(
            data_path,
            "streets/streets_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(streets_sum_total)
}