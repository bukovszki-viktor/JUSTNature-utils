make_railroads <- function(city_shapes, utmcrs) {
    #' @title Preparing railroad network
    #' 
    #' @description This function aggregates the railroad network on the
    #' city-level by year. It also plots the raw data. Year for plotting: 2020
    #' 
    #' @param city_shapes Shape file with city borders
    #' @param utmcrs UTM projection
    #' 
    #' @author Patrick Thiel
    #' @return Summarised railroad network on city-level
    
    #----------------------------------------------
    # load railroads

    railroads <- sf::st_read(
        file.path(
            data_path,
            "railroads/railroads.shp"
        ),
        quiet = TRUE
    )

    #----------------------------------------------
    # transform and adjust city names
    
    railroads <- railroads |>
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

    railroads_sum <- railroads |>
        # add length of each street segment
        dplyr::mutate(
            railroad_length_km = as.numeric(
                sf::st_length(geometry)
            ) / 1000
        ) |>
        sf::st_drop_geometry() |>
        dplyr::group_by(city_name, year, used_tag) |>
        # calcualate the length of the network for each street type
        dplyr::summarise(
            total_railroad_length_km = sum(railroad_length_km)
        )

    #----------------------------------------------
    # summarise by city and year

    railroads_sum_total <- railroads_sum |>
        dplyr::group_by(city_name, year) |>
        dplyr::summarise(
            total_railroad_length_km = sum(total_railroad_length_km)
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
            rel_total_railroad_length = total_railroad_length_km /
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
        length(unique(railroads$used_tag)),
        replace = FALSE
    )

    # define labels
    labs <- stringr::str_to_title(unique(railroads$used_tag))
    labs <- stringr::str_replace(labs, "_", " ")

    # loop through cities
    for (ct in cities) {
        # generate map
        map <- ggplot()+
            geom_sf(
                data = railroads |>
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

        filename <- paste0("railroads_2020_", ct, ".png")
        ggsave(
            plot = map,
            file.path(
                output_path,
                "maps/railroads",
                filename
            ),
            dpi = owndpi
        )
    }

    #----------------------------------------------
    # export

    data.table::fwrite(
        railroads_sum_total,
        file.path(
            data_path,
            "streets/railroads_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(railroads_sum_total)
}