# airport route
Project for search short air routing travel.

=== Product Requirements Document ===

This programm find short route between two City.
For searching are used three famous airline - Airbaltic, Ryanair, Wizzair.

On web-site input two City-name (start/end travels) in relevamt form, press button 'Search' and take result.

Realisation:

1. Load data from json-files 'airbaltic.json', 'ryanair.json', 'wizzair.json' to variable a_data, r_data, w_data
2. Create dict of Cities by using functions : 
   load_airbaltic_city(), load_ryanair_city(), load_wizzair_city()
3. Create dict of direction for each City of airline by using function :
   airbaltic_direction(), ryanair_direction(), wizzair_direction()
4. Main task: use function index()
5. Get City-name from web-form (index.html) to variable: airsrc, airdest.
6. Search shortest route use function calculate_route(), where translate each City-name to IATA-code.
   In last function called subfunction find_path() for make chain airports for each airlines. 
7. Creation of printable route with convert IATA-code to City-name by using function city_route().
8. Put result in index.html
