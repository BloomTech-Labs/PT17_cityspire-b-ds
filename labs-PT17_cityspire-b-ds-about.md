### NEW ENDPOINTS:
**GET:**
   ``/all_cities``                     Retrieves cities available from database
   
   ```
   [
  {
    "City": "Akron",
    "State": "OH"
  },
  {
    "City": "Albany",
    "State": "GA"
  },
  {
    "City": "Albany",
    "State": "NY"
  },
  {
    "City": "Albany",
    "State": "OR"
  },
  {
    "City": "Albuquerque",
    "State": "NM"
  },
  {
    "City": "Alexandria",
    "State": "LA"
  }, ...
   ```

POST:
  ``/api/housing_price_averages``      Retrieve housing price averages per city. 
                                       The averages includes single family homes, condos, one bedroom, two bedroom, three bedroom, four bedroom, and five and up bedroom averages.                              (Bedroom averages are based off of single family homes AND condos.)
  
  ```
  {
  "City": "New York",
  "State": "NY",
  "single_family_housing_avg_price": 694367,
  "condo_avg_price": 602846,
  "1_bedroom_avg_price": 575173,
  "2_bedroom_avg_price": 726108,
  "3_bedroom_avg_price": 677892,
  "4_bedroom_avg_price": 815457,
  "5_and_up_bedroom_avg_price": 1088310
  }
  ```
                                        
  ``/api/weather_historical``          Retrieve daily historical weather for target city (date range 2017/01/01 - 2021/03/16)
  
  ``/api/weather_daily_forecast``      Retrieve daily weather forecast for target city Forecasted daily temperature for the next two years (2021/03/17 - 2023/03/16)
  
  ```
  {
  "City": "New York",
  "State": "NY",
  "weather_temperature": [
    {
      "date": "2021-03-17",
      "average_temperature": 42.18277023032904,
      "min_temperature": 33.93951544061078,
      "max_temperature": 50.871546250320776
    },
    {
      "date": "2021-03-18",
      "average_temperature": 42.12605721215456,
      "min_temperature": 34.47574551004795,
      "max_temperature": 49.94850853870516
    },
    {
      "date": "2021-03-19",
      "average_temperature": 42.33482945708372,
      "min_temperature": 33.86577905543652,
      "max_temperature": 50.3229295032063
    }, 
    ...
        {
      "date": "2023-03-14",
      "average_temperature": 41.35213695472042,
      "min_temperature": 33.465711906373215,
      "max_temperature": 49.80247835524322
    },
    {
      "date": "2023-03-15",
      "average_temperature": 41.525024417086925,
      "min_temperature": 33.127419812279086,
      "max_temperature": 49.51111001046587
    },
    {
      "date": "2023-03-16",
      "average_temperature": 41.37162983207661,
      "min_temperature": 33.28046726740097,
      "max_temperature": 49.82323919057672
    }
  ]
}
  ```
  
  ``/api/weather_monthly_forecast``    Retrieve monthly weather forecast for target city Forecasted monthly temperature for next two years (2021/03/17 - 2023/03/16)
  
  ```
  {
  "City": "New York",
  "State": "NY",
  "weather_temperature": [
    {
      "date": "2021-04-01",
      "average_temperature": 48.13833939000883,
      "min_temperature": 39.98219445314486,
      "max_temperature": 56.07476607752713
    },
    {
      "date": "2021-05-01",
      "average_temperature": 56.77959812674579,
      "min_temperature": 48.497817031728985,
      "max_temperature": 65.57741611688107
    },
    {
      "date": "2021-06-01",
      "average_temperature": 68.21293396276369,
      "min_temperature": 60.24948158839838,
      "max_temperature": 76.52519658659372
    },
    {
      "date": "2021-07-01",
      "average_temperature": 77.92146207209926,
      "min_temperature": 69.4472693830679,
      "max_temperature": 85.86617975873759
    },
    ...
        {
      "date": "2022-12-01",
      "average_temperature": 43.7983610155837,
      "min_temperature": 35.19713652503212,
      "max_temperature": 51.729998803893956
    },
    {
      "date": "2023-01-01",
      "average_temperature": 36.633151376311645,
      "min_temperature": 28.731242148581888,
      "max_temperature": 45.09037890599299
    },
    {
      "date": "2023-02-01",
      "average_temperature": 35.994204979164266,
      "min_temperature": 27.711807303727603,
      "max_temperature": 44.08978246347866
    },
    {
      "date": "2023-03-01",
      "average_temperature": 41.985758823454546,
      "min_temperature": 33.85600305585458,
      "max_temperature": 50.38039912322065
    }
  ]
}
  ```
   
  ``/api/weather_conditions``          Retrieve weather conditions sunny/cloudy/rainy/snowy days for target city. 
                                       Average number of days based on 4 year historical data (from 2017-01-01 to 2020-12-31)
  
  ```
  {
  "City": "New York",
  "State": "NY",
  "weather_conditions": {
    "sunny_days_avg_year": 92,
    "cloudy_days_avg_year": 35,
    "rainy_days_avg_year": 212,
    "snowy_days_avg_year": 28
  }
}
  ```
                                        
  ``/api/jobs``                        Retrieve jobs for target city Uses Beautiful Soup args: job, city, state.
                                       returns: List of the current job openings for that city, which is converted by fastAPI to a json object.
  
  ```
  {
  "scraped_jobs": [] # 10 random listings
}
  ```
                                        
  ``/api/school_district_information`` Retrieve school district information per city. This includes the total number of schools, 
                                       the total number of students in that school district, the total number of teachers in that school district, 
                                       and the pupil/teacher ratio in that school district.
  ```
  {
  "City": "New York",
  "State": "NY",
  "total_number_of_schools": 4699,
  "total_students": 2720050,
  "total_teachers": "213463.87",
  "ratio": "12.74"
  }
  ```
