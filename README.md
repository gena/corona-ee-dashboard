## Dashboard

Live Version: https://gena.users.earthengine.app/view/corona-virus.

![dashboard](https://github.com/gena/corona-ee-dashboard/blob/master/media/dashboard.gif?raw=true|width=1024)

## Data

The main data source for this dashboard is: https://github.com/CSSEGISandData/COVID-19. 

## Description 

Death rate is calculate as follows:

![image](https://user-images.githubusercontent.com/169821/76144317-43a19f00-607f-11ea-95fb-040b5658a4a6.png)

The size of the circles is computed as a square root of the number of cases (confirmed, recovered, deaths), with the idea that the area of the circle should correspond to the number of cases. The size of the recovered cases circle (green) is computed as a the square root of the recovered + deaths cases. A more accurate formulae would be r = sqrt(N / pi), but I've skipped /pi part to ensure small changes increments can be distinguished in the radius changes.

## Roadmap

- [x] Implement Play / Pause buttons
- [x] Log scale
- [x] Increments vs. cumulative charts
- [ ] Forecasts (e.g. https://timchurches.github.io/blog/posts/2020-03-01-analysing-covid-19-2019-ncov-outbreak-data-with-r-part-2/)

## Terms of Use

This GitHub repo and its contents herein, including all mapping and analysis, copyright 2020 Gennadii Donchyts, all rights reserved, is provided to the public strictly for educational and academic research purposes. The Website relies upon publicly available data from multiple sources, that do not always agree. The authors of the dashboard hereby disclaims any and all representations and warranties with respect to the Website, including accuracy, fitness for use, and merchantability. Reliance on the Website for medical guidance or use of the Website in commerce is strictly prohibited.

## Contact

gennadiy.donchyts@gmail.com
