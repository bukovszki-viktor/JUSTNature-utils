make_public_transport <- function(city_shapes, city_pop, utmcrs) {
    #' @title Making education
    #' 
    #' @description This function aggregates the public transportation points
    #' on the city-level by year. It also plots the raw data.
    #' Year for plotting: 2020
    #' 
    #' @param city_shapes Shape file with city borders
    #' @param city_pop City population
    #' @param utmcrs UTM projection
    #' 
    #' @author Patrick Thiel
    #' @return Summarised public transportation on city-level
    
    #----------------------------------------------
    # read public transportation data

    transport <- sf::st_read(
        file.path(
            data_path,
            "public_transportation/public_transportation.shp"
        ),
        quiet = TRUE
    )

    #----------------------------------------------
    # transform and adjust city names
    
    transport <- transport |>
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

    transport_sum <- transport |>
        sf::st_drop_geometry() |>
        dplyr::group_by(city_name, year, used_tag) |>
        dplyr::summarise(
            count_trans = n()
        ) |>
        # add total count by year and city
        dplyr::group_by(city_name, year) |>
        dplyr::mutate(
            total_count_trans = sum(count_trans)
        ) |>
        # merge city population
        merge(
            city_pop,
            by = "city_name",
            all.x = TRUE
        ) |>
        # adjust total count by population
        dplyr::mutate(
            total_trans_per_tsd_pp = (total_count_trans / total_pop) * 1000
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
        length(unique(transport$used_tag)),
        replace = FALSE
    )

    # define labels and replace underscore in naming
    labs <- stringr::str_to_title(unique(transport$used_tag))
    labs <- stringr::str_replace(labs, "_", " ")

    # loop through cities
    for (ct in cities) {
        # generate map
        map <- ggplot()+
            geom_sf(
                data = transport |>
                    dplyr::filter(year == 2020 & city_name == ct),
                mapping = aes(
                    geometry = geometry,
                    col = used_tag
                ),
                size = 1.5
            )+
            geom_sf(
                data = city_shapes |>
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

        filename <- paste0("transport_2020_", ct, ".png")
        ggsave(
            plot = map,
            file.path(
                output_path,
                "maps/public_transportation",
                filename
            ),
            dpi = owndpi
        )
    }

    #----------------------------------------------
    # export

    data.table::fwrite(
        transport_sum,
        file.path(
            data_path,
            "public_transportation/public_transportation_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(transport_sum)
}