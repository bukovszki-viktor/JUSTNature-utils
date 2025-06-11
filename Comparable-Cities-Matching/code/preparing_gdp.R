preparing_gdp <- function(city_grids, city_shapes, city_grid_pop, utmcrs) {
    #' @title Preparing GDP data
    #' 
    #' @description This function prepares the GDP data and brings it on the
    #' same grid (INSPIRE) as the other data.
    #' 
    #' @param city_grids City-specific grids
    #' @param city_shapes Shape of cities
    #' @param city_grid_pop City-specific population+
    #' @param utmcrs UTM projection
    #' 
    #' @return QS file with city-specific GDP on grid-level
    #' @author Patrick Thiel
    
    #----------------------------------------------
    # read data

    # GDP data
    # use the version of 30 Arc seconds resolution
    # NOTE: 5 arc minutes resolution is too large for analysis
    gdp_data <- raster::stack(
        file.path(
            data_path,
            "gdp/GDP_PPP_30arcsec_v2.nc"
        )
    )

    #----------------------------------------------
    # prepare GDP

    # subet for latest year
    gdp_latest <- gdp_data[["X2015"]]

    #----------------------------------------------
    # join raster data on city level

    # get all city names
    cities <- unique(city_shapes$city_name)
    
    # empty list for storage
    grid_gdp_list <- list()

    for(city in cities) {
        # subset city shapes
        city_shape <- city_shapes |>
            dplyr::filter(city_name == city) |>
            sf::st_transform(crs = st_crs(gdp_data))

        # subset city grids
        city_grid <- city_grids |>
            dplyr::filter(city_name == city) |>
            sf::st_transform(crs = st_crs(gdp_data))

        # subset city grid population
        city_pop <- city_grid_pop |>
            st_drop_geometry() |>
            dplyr::filter(city_name == city) |>
            select(grid_id, pop_2018)

        # extract data from raster
        extracted_values <- raster::extract(
            gdp_latest,
            city_shape,
            df = TRUE,
            cellnumbers = TRUE,
            exact = TRUE
        )

        # get cell information
        cell_info <- raster::xyFromCell(
            gdp_latest,
            cell = extracted_values$cell,
            spatial = FALSE
        ) |>
        as.data.frame()

        # cell number from extracted value
        cell_info$cell <- extracted_values$cell

        # merge both data frames
        complete_values <- merge(extracted_values, cell_info)

        # make sf
        complete_values_sf <- complete_values |>
            select(-ID) |>
            st_as_sf(coords = c("x", "y"), crs = st_crs(gdp_data)) |>
            rename(cell_id = cell, total_gdp = X2015)

        # join with city grids
        suppressWarnings(
            joint <- st_join(
                complete_values_sf,
                city_grid,
                left = TRUE,
                largest = TRUE
            )
        )

        # calculate the average GDP per grid cell
        avg_grid_gdp <- joint |>
            st_drop_geometry() |>
            group_by(grid_id) |>
            summarise(
                total_gdp = mean(total_gdp, na.rm = TRUE)
            ) |>
            as.data.frame()

        # merge city population
        avg_grid_gdp_pp <- merge(
            avg_grid_gdp,
            city_pop,
            by = "grid_id"
        ) |>
        mutate(
            # calculate GDP per capita (only for populated grids)
            gdp_per_capita = case_when(
                pop_2018 != 0 ~ total_gdp / pop_2018,
                TRUE ~ NA
            )
        )

        # add back geo info
        avg_grid_gdp_sf <- merge(
            avg_grid_gdp_pp,
            city_grid,
            by = "grid_id"
        )

        avg_grid_gdp_sf <- st_set_geometry(
            avg_grid_gdp_sf, avg_grid_gdp_sf$geometry
        )

        # define groups based on deciles for better comparison
        groups <- as.numeric(
            quantile(
                avg_grid_gdp_sf[["total_gdp"]],
                prob = seq(0, 1, 0.1),
                na.rm = TRUE
            )
        )

        # add groups
        avg_grid_gdp_sf <- avg_grid_gdp_sf |>
            mutate(
                total_gdp_group = case_when(
                    total_gdp >= groups[1] & total_gdp < groups[2] ~ 1,
                    total_gdp >= groups[2] & total_gdp < groups[3] ~ 2,
                    total_gdp >= groups[3] & total_gdp < groups[4] ~ 3,
                    total_gdp >= groups[4] & total_gdp < groups[5] ~ 4,
                    total_gdp >= groups[5] & total_gdp < groups[6] ~ 5,
                    total_gdp >= groups[6] & total_gdp < groups[7] ~ 6,
                    total_gdp >= groups[7] & total_gdp < groups[8] ~ 7,
                    total_gdp >= groups[8] & total_gdp < groups[9] ~ 8,
                    total_gdp >= groups[9] & total_gdp < groups[10] ~ 9,
                    total_gdp >= groups[10] & total_gdp <= groups[11] ~ 10,
                )
            ) |>
            relocate(
                total_gdp_group, .after = total_gdp
            )

        # store data
        grid_gdp_list[[city]] <- avg_grid_gdp_sf

        #----------------------------------------------
        # generate map

        map <- ggplot()+
            geom_sf(
                data = avg_grid_gdp_sf,
                mapping = aes(
                    geometry = geometry,
                    fill = factor(total_gdp_group, levels = seq(1, 10, 1))
                )
            )+
            geom_sf(
                data = city_shape,
                mapping = aes(geometry = geometry),
                fill = NA,
                linewidth = 0.8,
                col = "black"
            )+
            scale_fill_viridis_d(
                option = "magma",
                direction = -1,
                name = "GDP\n(Decile groups)"
            )+
            theme_void()

        filename <- paste0("gdp_", city, ".png")
        ggsave(
            plot = map,
            file.path(
                output_path,
                "maps/gdp",
                filename
            ),
            dpi = owndpi
        )
    }
    
    # combine all
    grid_gdp <- data.table::rbindlist(grid_gdp_list)
    grid_gdp <- st_set_geometry(grid_gdp, grid_gdp$geometry)

    # transform to general projection
    grid_gdp <- st_transform(grid_gdp, utmcrs)

    #----------------------------------------------
    # export

    qs::qsave(
        grid_gdp,
        file.path(
            data_path,
            "gdp/gdp_grid_cities.qs"
        )
    )

    #----------------------------------------------
    # return

    return(grid_gdp)
}