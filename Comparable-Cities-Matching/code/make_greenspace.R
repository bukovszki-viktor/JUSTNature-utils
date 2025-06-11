make_greenspace <- function(city_shapes, utmcrs) {
    #' @title Preparing greenspace
    #' 
    #' @description This function aggregates the greenspace on the
    #' city-level by year. It also plots the raw data. Year for plotting: 2020
    #' 
    #' @param city_shapes Shape file with city borders
    #' @param utmcrs UTM projection
    #' 
    #' @author Patrick Thiel
    #' @return Summarised greenspace on city-level
    
    #----------------------------------------------
    # read greenspace

    greenspace <- sf::st_read(
        file.path(
            data_path,
            "greenspace/greenspace.shp"
        ),
        quiet = TRUE
    )

    #----------------------------------------------
    # transform and adjust city names
    
    greenspace <- greenspace |>
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

    greenspace_sum <- greenspace |>
        # add area of each greenspace
        dplyr::mutate(
            green_area_sqkm = as.numeric(
                sf::st_area(geometry)
            ) / 1000000
        ) |>
        sf::st_drop_geometry() |>
        dplyr::group_by(city_name, year, used_tag) |>
        # calcualate the area of each water type
        dplyr::summarise(
            total_green_area_sqkm = sum(green_area_sqkm)
        )

    #----------------------------------------------
    # summarise by city and year

    greenspace_sum_total <- greenspace_sum |>
        dplyr::group_by(city_name, year) |>
        dplyr::summarise(
            total_green_area_sqkm = sum(total_green_area_sqkm)
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
        # calculate the relative area of the greenspace
        # relative to the city size
        dplyr::mutate(
            rel_total_green_area = total_green_area_sqkm /
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
        length(unique(greenspace$used_tag)),
        replace = FALSE
    )

    # define labels
    labs <- stringr::str_to_title(unique(greenspace$used_tag))
    labs <- stringr::str_replace(labs, "_", " ")

    # loop through cities
    for (ct in cities) {
        # generate map
        map <- ggplot()+
            geom_sf(
                data = greenspace |>
                    # filter for plotting year (2020)
                    # filter for specific city
                    dplyr::filter(year == 2020 & city_name == ct),
                mapping = aes(
                    geometry = geometry,
                    fill = used_tag
                )
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
            scale_fill_manual(
                name = "Feature type",
                values = cols,
                labels = labs 
            )+
            theme_void()

        filename <- paste0("greenspace_2020_", ct, ".png")
        ggsave(
            plot = map,
            file.path(
                output_path,
                "maps/greenspace",
                filename
            ),
            dpi = owndpi
        )
    }

    #----------------------------------------------
    # export

    data.table::fwrite(
        greenspace_sum_total,
        file.path(
            data_path,
            "greenspace/greenspace_cities.csv"
        )
    )

    #----------------------------------------------
    # return
    return(greenspace_sum_total)
}