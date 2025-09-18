This github repo was used to build an honest and accurate data set of all 
linkedin posts (not including reposts) of 9 of the top 10 clay experts. 
We only didnt include 1 due to the file of aggregated posts being corrupted.

All items referenced here are from publicly viewable LinkedIn posts. The dataset and code are available in the GitHub repo for anyone who wants to audit our methods.

input.py contains all the posts of the linkedin profiles below.

The linkedin profiles of the owners of top 10 (Minus Josh Whitefield due to corruption of file before aggregation) Clay Experts/Agencies as of Jun 9th 2025

https://www.linkedin.com/in/michel-lieben/
https://www.linkedin.com/in/patrickspychalski/
https://www.linkedin.com/in/outboundphd/
https://www.linkedin.com/in/mariellecamba/
https://www.linkedin.com/in/lanny-heiz/
https://www.linkedin.com/in/ai4sales/
https://www.linkedin.com/in/kellen-casebeer/
https://www.linkedin.com/in/growthwithjoel/
https://www.linkedin.com/in/janivrancsik/

We first cleaned up data to remove formatting issues, as well as reposts, to create our input.csv 
of all posts across all people (except joshwhitfieldai) due to corruption of file.

We then used sort.py to remove all posts older than 12 months by using OpenAI's API to fuzzymatch
all date ranges.

We then used promotingclayyesorno.py to process all raw content of posts to identify 3 things...

1. Are they mentioning clay?
2. Is the mention an endorsement or otherwise promotion?
3. Are they endorsing other sales tools?

This returned a "clayanalysis.csv" which add yes/no answers as additional columns for all 3 questions.

We then used aggregate.py to then add up how many posts for every single unique posters, as well
as how many posts were yes/no for all 3 questions. This summary was delivered as clay_summary.csv

We then did some manual edits to the file, not to the data, but rather just adding columns for
calculations of the percentage of posts that 

