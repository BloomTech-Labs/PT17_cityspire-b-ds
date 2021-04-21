### NEW ENDPOINTS:
GET:
  - */all_cities* Retrieves cities available from database

POST:
  - */api/housing_price_averages*:      Retrieve housing price averages per city. 
                                        The averages includes single family homes, condos, one bedroom, two bedroom, three bedroom, four bedroom, and five and up bedroom averages.
                                        
  - */api/weather_historical*:          Retrieve daily historical weather for target city (date range 2017/01/01 - 2021/03/16)
  
  - */api/weather_daily_forecast*:      Retrieve daily weather forecast for target city Forecasted daily temperature for the next two years (2021/03/17 - 2023/03/16)
  
  - */api/weather_monthly_forecast*:    Retrieve monthly weather forecast for target city Forecasted monthly temperature for next two years (2021/03/17 - 2023/03/16)
   
  - */api/weather_conditions*:          Retrieve weather conditions sunny/cloudy/rainy/snowy days for target city. 
                                        Average number of days based on 4 year historical data (from 2017-01-01 to 2020-12-31)
                                        
  - */api/jobs*:                        Retrieve jobs for target city Uses Beautiful Soup args: job, city, state.
                                        returns: List of the current job openings for that city, which is converted by fastAPI to a json object.
                                        
  - */api/school_district_information*: Retrieve school district information per city. This includes the total number of schools, 
                                        the total number of students in that school district, the total number of teachers in that school district, 
                                        and the pupil/teacher ratio in that school district.
