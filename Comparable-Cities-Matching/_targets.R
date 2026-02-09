# NOTE:
    # Data on OSM data comes from the personal pipeline
    # on my local computer (PT)

#----------------------------------------------
# load libraries
suppressPackageStartupMessages(
    {
    library(targets)
    library(future)
    library(future.callr)
    library(tarchetypes)
    library(rlang)
    library(dplyr)
    library(tidyr)
    library(ggplot2)
    library(sf)
    library(data.table)
    library(readxl)
    library(openxlsx)
    library(qs)
    library(docstring)
    library(stringr)
    library(MetBrewer)
    library(fst)
    library(stars)
    }
)

#----------------------------------------------
# set up for future package

plan(callr)

#----------------------------------------------
# paths

main_path <- "N:/Just_Nature/comparable_cities"
data_path <- file.path(main_path, "data")
output_path <- file.path(main_path, "output")
code_path <- file.path(main_path, "code")

#----------------------------------------------
# set working directory

setwd(main_path)

#----------------------------------------------
# globals

owndpi <- 800
utmcrs <- 32632

#----------------------------------------------
# Read files

lapply(
    list.files(
        code_path,
        pattern = ".R$",
        full.names = TRUE,
        all.files = FALSE
    ),
    source
)

#----------------------------------------------
# preparation of geometries

target_prep_geo <- rlang::list2(
    # Extracting NBS cities
    tar_target(
        nbs_cities,
        extracting_nbs_cities()
    ),
    # Combine all geometries of included cities
    tar_qs(
        city_shapes,
        make_city_shapes(
            utmcrs
        )
    ),
    # Define the path to the population information
    # used as INSPIRE grid
    tar_files(
        file_grid_pop,
        "N:/Just_Nature/pop_eu/grid_1km_surf.gpkg"
    ),
    # Prepare shape of grids
    tar_qs(
        inspire_grid,
        preparing_inspire_grid(
            file_grid_pop,
            utmcrs
        )
    ),
    # Grids for included cities
    tar_qs(
        city_grids,
        make_city_grids(
            inspire_grid,
            city_shapes
        )
    )
)

#----------------------------------------------
# population grid

target_grid_pop <- rlang::list2(
    # Prepare population on grid-level
    tar_qs(
        grid_pop,
        preparing_pop_grid(
            file_grid_pop,
            utmcrs
        )
    ),
    # City grid population
    tar_qs(
        city_grid_pop,
        make_city_pop(
            grid_pop,
            city_grids
        )
    ),
    # Aggregate city population on city-level
    tar_fst_tbl(
        city_pop,
        aggregate_city_pop(
            city_grid_pop
        )
    )
)

#----------------------------------------------
# gpd data

target_gdp <- rlang::list2(
    tar_qs(
        city_gdp,
        preparing_gdp(
            city_grids,
            city_shapes,
            city_grid_pop,
            utmcrs
        )
    ),
    # aggregate grid-level city GDP to city-level
    tar_target(
        aggregated_city_gdp,
        aggregate_city_gdp(
            city_gdp
        )
    )
)

#----------------------------------------------
# point data
# including education, public transportation, and tourism

target_point <- rlang::list2(
    # Prepare and plot education opportunities
    tar_fst_tbl(
        education,
        make_education(
            city_shapes,
            city_pop,
            utmcrs
        )
    ),
    # Prepare and plot public transportation points
    tar_fst_tbl(
        transport,
        make_public_transport(
            city_shapes,
            city_pop,
            utmcrs
        )
    ),
    # Prepare and plot tourism spots
    tar_fst_tbl(
        tourism,
        make_tourism(
            city_shapes,
            city_pop,
            utmcrs
        )
    )
)

#----------------------------------------------
# line data
# including railroads, and streets

target_line <- rlang::list2(
    # Prepare and plot street network
    tar_fst_tbl(
        streets,
        make_streets(
            city_shapes,
            utmcrs
        )
    ),
    # Prepare and plot railroad network
    tar_fst_tbl(
        railroads,
        make_railroads(
            city_shapes,
            utmcrs
        )
    )
)

#----------------------------------------------
# polygon data
# including greenspace, and waterbodies

target_polygon <- rlang::list2(
    # Prepare and plot waterbodies
    tar_fst_tbl(
        waterbodies,
        make_waterbodies(
            city_shapes,
            utmcrs
        )
    ),
    # Prepare and plot greenspace
    tar_fst_tbl(
        greenspace,
        make_greenspace(
            city_shapes,
            utmcrs
        )
    )
)

#----------------------------------------------
# combine all information on the city-level

target_combine_cities <- rlang::list2(
    tar_fst_tbl(
        city_candidates,
        combine_all_resources(
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
        )
    )
)

#----------------------------------------------
# all together

rlang::list2(
    target_prep_geo,
    target_grid_pop,
    target_gdp,
    target_point,
    target_line,
    target_polygon,
    target_combine_cities
)
