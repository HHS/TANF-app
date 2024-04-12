The elastic router and Kibana app are created using ```create-es-kibana.sh``` script. This script creates one elastic router and one kibana app per cloud space.
The Kibana app will connect to the ES router, which connects to the ES service (created by terraform) at the space level.

## Running create-es-kibana.sh
This script accepts six inputs:
1: Deploy strategy      e.g.: rolling, initial, ...
2: Space name           e.g.: dev, staging, prod

an example of deploying kibana and elastic for dev env:
```./create-es-kibana.sh initial dev```