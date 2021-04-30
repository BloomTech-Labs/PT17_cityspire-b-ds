## Bugs
- */api/get_data* endpoint if target city is not in DB, throws an error
- */api/weather_historical* endpoint may take longer to respond and can cause unresponsive web page

## Incomplete Features
- Livability score has to be re-calculated due to added new features: weather, housing prices, job listings, school data

### Jobs to do's
- Job scraper should work locally but seems to not work on the deployed app.
- Ultimately the job scraper in the notebooks path = notebooks/datasets/data/labor_statistics/Labs17_Jobs_AndrewRust.ipynb needs to be reworked to collect at least 15 jobs for each city.  Also, some cities have the same name i.e. Portland OR and Portland ME so you need to specify "state."  There is code in said notebook that needs to be fixed.  Random_jobs.csv is an incomplete attempt at accruing jobs into a CSV file.
- Another way to get jobs would be a current count of how many jobs would be available for a particular job title.
- This could tie into the livability score as could the LQ (see below).
- "Location quotient (LQ) is basically a way of quantifying how concentrated a particular industry, cluster,
occupation, or demographic group is in a region as compared to the nation. It can reveal what makes a
particular region 'unique' in comparison to the national average." - https://www.economicmodeling.com/wp-content/uploads/2007/10/emsi_understandinglq.pdf 
- One of the CSV files has this LQ that could be used for livability path = notebooks/datasets/data/labor_statistics/bls.csv
