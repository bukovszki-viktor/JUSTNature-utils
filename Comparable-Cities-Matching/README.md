# Comparable Cities in Europe

## Abstract

Finding a feasible control group is central to many empirical methods in order to obtain reliable results as described above. This section describes an applied strategy for identifying comparable cities that can be used as a control group in further analytical steps.

Since randomized control trials are not feasible for studying the impact of Nature-based Solutions (NbS), we need to develop a strategy for identifying a good comparison group that serves as a proxy for the NbS-treated city. Since perfect comparability is not feasible in real-world examples, we rely on an applied matching strategy where we aim to identify a comparison city for each city included in the project. We focus on CiPeLs, which are the project cities including e.g. Munich (Germany) and Leuven (Belgium), as well as cities that have already implemented NbS measures. These cities and the corresponding information on the NbS strategies adopted have been collected by the experts of this project.[^complete_list_cities]

[^complete_list_cities]: The complete list includes 34 cities which are: Antwerp, Augsburg, Balatonfuzfo, Barcelona, Bari, Basel, Belgrade, Bolzano, Bratislava, Brussels, Budapest, Chania, Eindhoven, Genova, Gyor, Gzira, Hamburg, Krakow, Leipzig, Leuven, Malmo, Meran, Montpellier, Munich, Nicosia, Paris, Poznan, Prague, Szeged, Szombathely, Tampere, Utrecht, Valladolid, Vienna.

## Constructed Measures of Comparability

We focus on socio-economic variables such as GDP, but mainly on urban infrastructure variables. The reason is that the variables should be independent of potential outcome variables related to the NbS strategy.

<div role="region" tabindex="0">
<table style="border-bottom:2px solid;border-top:2px solid">
    <caption>
        <p><b>Table 1: Description of constructed measures of comparability</b></p>
    </caption>
    <thead>
        <tr>
            <th>Measure</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Population size</td>
            <td>Absolute number of people per city</td>
        </tr>
        <tr>
            <td>City size</td>
            <td>Absolute city size measured in square kilometer</td>
        </tr>
        <tr>
            <td>Relative local GDP</td>
            <td>Local GDP per capita on the city-level adjusted by the average real GDP per capita of the European Union (EU-28 in 2015)<div>
                    <div> </div>
                </div>
            </td>
        </tr>
        <tr>
            <td>Relative number of education opportunities</td>
            <td>Number of education buildings (e.g., schools, universities) relative to the absolute number of people</td>
        </tr>
        <tr>
            <td>Relative number of tourist attractions</td>
            <td>Number of tourist attractions (e.g., galleries) relative to the absolute number of people</td>
        </tr>
        <tr>
            <td>Relative number of access points to public transport</td>
            <td>Number of access points to the public transport network (e.g., subway entrances, bus stops) relative to the absolute number of people</td>
        </tr>
        <tr>
            <td>Relative length of the street network</td>
            <td>Length of the street network (measured in kilometer) relative to the city size</td>
        </tr>
        <tr>
            <td>Relative length of the railroad network</td>
            <td>Relative length of the railroad network Length of the railroad network (measured in kilometer) relative to the city size</td>
        </tr>
        <tr>
            <td>Relative area covered by water bodies</td>
            <td>Area covered by water bodies (e.g., rivers, lakes) relative to the city size</td>
        </tr>
        <tr>
            <td>Relative area covered by green space</td>
            <td>Area covered by green space (e.g., parks, gardens) relative to the city size</td>
        </tr>
    </tbody>
</table>
</div>

Most of these measures are constructed in relative terms (e.g., relative to the city's population or size) to make the variables comparable across space. 

## Matching Cities

After constructing these measures, we define a matching algorithm to assign a comparison city (or multiple cities in the case of multiple cities with similar characteristics) to each of the target cities. Since it is unlikely that there will be a perfect match, i.e. the measure of city A is exactly equal to the measure of city B, we define a <b>matching threshold (degree of similarity)</b> of 20%. Thus, if City A's measure falls within ±20% of City B's measure, we consider both cities to be similar for that particular characteristic. The 20% match threshold can be debated, as any other number could work. A lower number would ensure that two cities have a higher degree of similarity, while a higher number would make them less comparable. Beyond these theoretical considerations, it is important to note that from an applied perspective, the number of potential comparison candidates decreases with a lower matching threshold, which could lead to finding no matching city at all. For reliable empirical results, both arguments need to be considered. On the one hand, the comparison city should be a good proxy for the target city, i.e., a good match, which argues for a lower matching threshold, but on the other hand, the sample size must be sufficient, i.e., which argues for a higher matching threshold, to apply different empirical methods.
In addition to the matching threshold, we also constrain the algorithm to exclude the scenario of self-matching. Thus, a city cannot be matched to itself as a comparison group. Although one could argue that a city itself would be the best possible comparison group, this also raises the problem of spillovers, as discussed above, which would confound the results.

## Mapping Input Data (Examples)

### GDP data

<div style="text-align: center;">
  <img src="selective_outputs/gdp_basel.jpg" alt="GDP Basel (Switzerland)" width="400"/> 
  <img src="selective_outputs/gdp_prague.jpg" alt="GDP Prague (Czech Republic)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 1: GPD Basel (Switzerland) and Prague (Czech Republic) (Source: Own Figure)</strong></h6>

### Education opportunities

<div style="text-align: center;">
  <img src="selective_outputs/education_2020_augsburg.jpg" alt="Education opportunities 2020 Augsburg (Germany)" width="400"/> 
  <img src="selective_outputs/education_2020_barcelona.jpg" alt="Education oppurtunities 2020 Barcelona (Spain)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 2: Education opportunities Augsburg (Germany) and Barcelona (Spain) - 2020 (Source: Own Figure)</strong></h6>

### Tourist attractions

<div style="text-align: center;">
  <img src="selective_outputs/tourism_2020_brussels.jpg" alt="Tourist attractions 2020 Brussels (Belgium)" width="400"/> 
  <img src="selective_outputs/tourism_2020_budapest.jpg" alt="Tourist attractions 2020 Budapest (Hungary)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 3: Tourist attractions Brussels (Belgium) and Budapest (Hungary) - 2020 (Source: Own Figure)</strong></h6>

### Public transportation network

<div style="text-align: center;">
  <img src="selective_outputs/transport_2020_leipzig.jpg" alt="Public transportation network 2020 Leipzig (Germany)" width="400"/> 
  <img src="selective_outputs/transport_2020_vienna.jpg" alt="Public transportation network 2020 Vienna (Austria)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 4: Public transportation network Leipzig (Germany) and Vienna (Austria) - 2020 (Source: Own Figure)</strong></h6>

### Street network

<div style="text-align: center;">
  <img src="selective_outputs/streets_2020_antwerp.jpg" alt="Street network 2020 Antwerp (Belgium)" width="400"/> 
  <img src="selective_outputs/streets_2020_eindhoven.jpg" alt="Street network 2020 Eindhoven (Netherlands)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 5: Street network Antwerp (Belgium) and Eindhoven (Netherlands) - 2020 (Source: Own Figure)</strong></h6>

### Railroad network

<div style="text-align: center;">
  <img src="selective_outputs/railroads_2020_budapest.jpg" alt="Railroad network 2020 Budapest (Hungary)" width="400"/> 
  <img src="selective_outputs/railroads_2020_vienna.jpg" alt="Railroad network 2020 Vienna (Austria)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 6: Railroad network Budapest (Hungary) and Vienna (Austria) - 2020 (Source: Own Figure)</strong></h6>

### Water bodies

<div style="text-align: center;">
  <img src="selective_outputs/waterbodies_2020_antwerp.jpg" alt="Water bodies 2020 Antwerp (Belgium)" width="400"/> 
  <img src="selective_outputs/waterbodies_2020_krakow.jpg" alt="Water bodies 2020 Krakow (Poland)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 7: Water bodies Antwerp (Belgium) and Krakow (Poland) - 2020 (Source: Own Figure)</strong></h6>

### Green space

<div style="text-align: center;">
  <img src="selective_outputs/greenspace_2020_montpellier.jpg" alt="Green space 2020 Montpellier (France)" width="400"/> 
  <img src="selective_outputs/greenspace_2020_munich.jpg" alt="Green space 2020 Munich (Germany)" width="400"/>
</div>
<h6 style="text-align: center;"><strong>Figure 8: Green space Montpellier (France) and Munich (Germany) - 2020 (Source: Own Figure)</strong></h6>

## Final Result (An Example)

We would select the matching city/cities based on the majority rule, i.e., the highest number of similar characteristics. Munich (Germany) matches with two cities, Prague (Czech Republic) and Augsburg (Germany), in five out of ten measures (marked in bold). In a next step, the matched cities (control sites) could be grouped into a synthetic control group, which would be (potentially) even closer to Munich (Germany) than the individual cities.

<div role="region" tabindex="0">
<table style="border-bottom:2px solid;border-top:2px solid">
    <caption>
        <p>Table 2: Matching outcome for Munich (Germany)</p>
    </caption>
    <thead>
        <tr>
            <th></th>
            <th>Munich</th>
            <th>Prague</th>
            <th>Augsburg</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <p>Population size</p>
            </td>
            <td>
                <div>&nbsp;1,517,793&nbsp;</div>
            </td>
            <td>
                <div>&nbsp;<b>1,316,551</b>&nbsp;</div>
            </td>
            <td>
                <div>&nbsp;333,059&nbsp;</div>
            </td>
        </tr>
        <tr>
            <td>
                <p>City size (km<sup>2</sup>)</p>
            </td>
            <td>
                <div>310.7</div>
            </td>
            <td>
                <div>497.7</div>
            </td>
            <td>
                <div>146.8</div>
            </td>
        </tr>
        <tr>
            <td>
                <p>Relative local GDP</p>
            </td>
            <td>
                <div>106.5</div>
            </td>
            <td>
                <div>135.9</div>
            </td>
            <td>
                <div><b>102.5</b></div>
            </td>
        </tr>
        <tr>
            <td>
                <p>Relative number of education opportunities (per Tsd. people)</p>
            </td>
            <td>
                <div>0.9</div>
            </td>
            <td>
                <div>0.7</div>
            </td>
            <td>
                <div><b>0.8</b></div>
            </td>
        </tr>
        <tr>
            <td>
                <p>Relative number of access points to public transport (per Tsd. people)</p>
            </td>
            <td>
                <div>2.1</div>
            </td>
            <td>
                <div>2.8</div>
            </td>
            <td>
                <div><b>2.0</b></div>
            </td>
        </tr>
        <tr>
            <td>
                <div>Relative number of tourist attractions (per Tsd. people)</div>
            </td>
            <td>
                <div>0.3</div>
            </td>
            <td>
                <div><b>0.3</b></div>
            </td>
            <td>
                <div><b>0.3</b></div>
            </td>
        </tr>
        <tr>
            <td>
                <div>Relative length of the street network</div>
            </td>
            <td>
                <div>2.8</div>
            </td>
            <td>
                <div><b>2.6</b></div>
            </td>
            <td>
                <div>1.6</div>
            </td>
        </tr>
        <tr>
            <td>
                <div>Relative length of the railroad network</div>
            </td>
            <td>
                <div>4.2</div>
            </td>
            <td>
                <div>2.4</div>
            </td>
            <td>
                <div>2.2</div>
            </td>
        </tr>
        <tr>
            <td>
                <div>Relative area covered by water bodies (km<sup>2</sup>)</div>
            </td>
            <td>
                <div>2.4</div>
            </td>
            <td>
                <div><b>2.8</b></div>
            </td>
            <td>
                <div><b>2.3</b></div>
            </td>
        </tr>
        <tr>
            <td>
                <div>Relative area covered by green space (km2)</div>
            </td>
            <td>
                <div>36.4</div>
            </td>
            <td>
                <div><b>37.7</b></div>
            </td>
            <td>
                <div>1.8</div>
            </td>
        </tr>
        <tr style="border-top:2px solid;">
            <td>
                <div>Number of total matches</div>
            </td>
            <td></td>
            <td>5</td>
            <td>5</td>
        </tr>
    </tbody>
</table>
</div>

## Sources

- European Environmental Agency (EEA) (2017). France Administrative Boundaries. [Data set]. [Accessed: July 2023].

- Eurostat (2021). European Grid Data Based on Eurostat-GISCO Database and GEOSTAT. [Data set]. [Accessed July 2023].

- Eurostat (2023). Real GDP Per Capita. Data code: SDG_08_10. [Data set]. [Accessed: August 2023].

- Kummu, M., Taka, M., & Guillaume (2018). Data Descriptor: Gridded Global Datasets for Gross Domestic Product and Human Development Index over 1990–2015. [Data set].

- OSM Data for 2020, including streets, greenspace, public transportation, railroads, tourism, waterbodies, education facilities.

## Disclaimer
This repository and the corresponding output have been part of the project: Activation of NATURE-based solutions for a JUST low carbon transition funded by European Commission, Horizon 2020. All rights reserved the author of the code [Dr. Patrick Thiel](https://www.rwi-essen.de/rwi/team/person/patrick-thiel).