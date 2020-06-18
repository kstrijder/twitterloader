# Twitterloader
(Docker)Python script to scrape tweets.

# Usage
Configure config.json so a hashtag/username/limit is present.

Set the ENV mongoCS in the Dockerfile to point at your MongoDB instance. 
 
You can run the container with the following options:

Scrape only tweets from a certain account:

-u **username**

Limit tweets

--limit 40(Scrapes 40 tweets)
