import json
import twint
import sys
import twint.output
import twint.format
import os
import argparse
from pymongo import MongoClient

module = sys.modules["twint.storage.write"]

def error(_error, message):
    """ Print errors to stdout
    """
    print("[-] {}: {}".format(_error, message))
    sys.exit(0)

def options():
    """ Parse arguments
    """
    ap = argparse.ArgumentParser(prog="twint",
                                 usage="python3 %(prog)s [options]",
                                 description="TWINT - An Advanced Twitter Scraping Tool.")
    ap.add_argument("-u", "--username", help="User's Tweets you want to scrape.")
    ap.add_argument("-s", "--search", help="Search for Tweets containing this word or phrase.")
    ap.add_argument("-g", "--geo", help="Search for geocoded Tweets.")
    ap.add_argument("--near", help="Near a specified city.")
    ap.add_argument("--location", help="Show user's location (Experimental).", action="store_true")
    ap.add_argument("-l", "--lang", help="Search for Tweets in a specific language.")
    ap.add_argument("-o", "--output", help="Save output to a file.")
    ap.add_argument("-es", "--elasticsearch", help="Index to Elasticsearch.")
    ap.add_argument("--year", help="Filter Tweets before specified year.")
    ap.add_argument("--since", help="Filter Tweets sent since date (Example: \"2017-12-27 20:30:15\" or 2017-12-27).",
                    metavar="DATE")
    ap.add_argument("--until", help="Filter Tweets sent until date (Example: \"2017-12-27 20:30:15\" or 2017-12-27).",
                    metavar="DATE")
    ap.add_argument("--email", help="Filter Tweets that might have email addresses", action="store_true")
    ap.add_argument("--phone", help="Filter Tweets that might have phone numbers", action="store_true")
    ap.add_argument("--verified", help="Display Tweets only from verified users (Use with -s).",
                    action="store_true")
    ap.add_argument("--csv", help="Write as .csv file.", action="store_true")
    ap.add_argument("--json", help="Write as .json file", action="store_true")
    ap.add_argument("--hashtags", help="Output hashtags in seperate column.", action="store_true")
    ap.add_argument("--cashtags", help="Output cashtags in seperate column.", action="store_true")
    ap.add_argument("--userid", help="Twitter user id.")
    ap.add_argument("--limit", help="Number of Tweets to pull (Increments of 20).", default=20)
    ap.add_argument("--count", help="Display number of Tweets scraped at the end of session.",
                    action="store_true")
    ap.add_argument("--stats", help="Show number of replies, retweets, and likes.",
                    action="store_true")
    ap.add_argument("-db", "--database", help="Store Tweets in a sqlite3 database.")
    ap.add_argument("--to", help="Search Tweets to a user.", metavar="USERNAME")
    ap.add_argument("--all", help="Search all Tweets associated with a user.", metavar="USERNAME")
    ap.add_argument("--followers", help="Scrape a person's followers.", action="store_true")
    ap.add_argument("--following", help="Scrape a person's follows", action="store_true")
    ap.add_argument("--favorites", help="Scrape Tweets a user has liked.", action="store_true")
    ap.add_argument("--proxy-type", help="Socks5, HTTP, etc.")
    ap.add_argument("--proxy-host", help="Proxy hostname or IP.")
    ap.add_argument("--proxy-port", help="The port of the proxy server.")
    ap.add_argument("--tor-control-port", help="If proxy-host is set to tor, this is the control port", default=9051)
    ap.add_argument("--tor-control-password", help="If proxy-host is set to tor, this is the password for the control port", default="my_password")
    ap.add_argument("--essid",
                    help="Elasticsearch Session ID, use this to differentiate scraping sessions.",
                    nargs="?", default="")
    ap.add_argument("--userlist", help="Userlist from list or file.")
    ap.add_argument("--retweets",
                    help="Include user's Retweets (Warning: limited).",
                    action="store_true")
    ap.add_argument("--format", help="Custom output format (See wiki for details).")
    ap.add_argument("--user-full",
                    help="Collect all user information (Use with followers or following only).",
                    action="store_true")
    ap.add_argument("--profile-full",
                    help="Slow, but effective method of collecting a user's Tweets and RT.",
                    action="store_true")
    ap.add_argument("--debug",
                    help="Store information in debug logs", action="store_true")
    ap.add_argument("--resume", help="Resume from Tweet ID.", metavar="TWEET_ID")
    ap.add_argument("--videos", help="Display only Tweets with videos.", action="store_true")
    ap.add_argument("--images", help="Display only Tweets with images.", action="store_true")
    ap.add_argument("--media",
                    help="Display Tweets with only images or videos.", action="store_true")
    ap.add_argument("--replies", help="Display replies to a subject.", action="store_true")
    ap.add_argument("-pc", "--pandas-clean",
                    help="Automatically clean Pandas dataframe at every scrape.")
    ap.add_argument("-cq", "--custom-query", help="Custom search query.")
    ap.add_argument("-pt", "--popular-tweets", help="Scrape popular tweets instead of recent ones.", action="store_true")
    ap.add_argument("-sc", "--skip-certs", help="Skip certs verification, useful for SSC.", action="store_false")
    ap.add_argument("-ho", "--hide-output", help="Hide output, no tweets will be displayed.", action="store_true")
    ap.add_argument("-nr", "--native-retweets", help="Filter the results for retweets only.", action="store_true")
    ap.add_argument("--min-likes", help="Filter the tweets by minimum number of likes.")
    ap.add_argument("--min-retweets", help="Filter the tweets by minimum number of retweets.")
    ap.add_argument("--min-replies", help="Filter the tweets by minimum number of replies.")
    ap.add_argument("--links", help="Include or exclude tweets containing one o more links. If not specified"+
                    " you will get both tweets that might contain links or not.")
    ap.add_argument("--source", help="Filter the tweets for specific source client.")
    ap.add_argument("--members-list", help="Filter the tweets sent by users in a given list.")
    ap.add_argument("-fr", "--filter-retweets", help="Exclude retweets from the results.", action="store_true")
    ap.add_argument("--backoff-exponent", help="Specify a exponent for the polynomial backoff in case of errors.", type=float, default=3.0)
    ap.add_argument("--min-wait-time", type=float, default=15, help="specifiy a minimum wait time in case of scraping limit error. This value will be adjusted by twint if the value provided does not satisfy the limits constraints")
    args = ap.parse_args()
    
    return args

def initialize(args):
    """ Set default values for config from args
    """
    c = twint.Config()
    c.Username = args.username
    c.User_id = args.userid
    c.Search = args.search
    c.Geo = args.geo
    c.Location = args.location
    c.Near = args.near
    c.Lang = args.lang
    c.Output = "mongo"
    c.Elasticsearch = args.elasticsearch
    c.Year = args.year
    c.Since = args.since
    c.Until = args.until
    c.Email = args.email
    c.Phone = args.phone
    c.Verified = args.verified
    c.Store_csv = args.csv
    c.Store_json = True
    c.Show_hashtags = args.hashtags
    c.Show_cashtags = args.cashtags
    c.Limit = args.limit
    c.Count = args.count
    c.Stats = args.stats
    c.Database = args.database
    c.To = args.to
    c.All = args.all
    c.Essid = args.essid
    c.Format = args.format
    c.User_full = args.user_full
    c.Profile_full = args.profile_full
    # c.Pandas_type = args.pandas_type
    # c.Index_tweets = args.index_tweets
    # c.Index_follow = args.index_follow
    # c.Index_users = args.index_users
    c.Debug = args.debug
    c.Resume = args.resume
    c.Images = args.images
    c.Videos = args.videos
    c.Media = args.media
    c.Replies = args.replies
    # # c.Pandas_clean = args.pandas_clean
    # c.Proxy_host = args.proxy_host
    # c.Proxy_port = args.proxy_port
    # c.Proxy_type = args.proxy_type
    # c.Tor_control_port = args.tor_control_port
    # c.Tor_control_password = args.tor_control_password
    c.Retweets = args.retweets
    c.Custom_query = args.custom_query
    c.Popular_tweets =  args.popular_tweets
    c.Skip_certs = args.skip_certs
    c.Hide_output = args.hide_output
    c.Native_retweets = args.native_retweets
    c.Min_likes = args.min_likes
    c.Min_retweets = args.min_retweets
    c.Min_replies = args.min_replies
    c.Links = args.links
    c.Source = args.source
    c.Members_list = args.members_list
    c.Filter_retweets = args.filter_retweets
    # c.Translate = args.translate
    # c.TranslateDest = args.translate_dest
    c.Backoff_exponent = args.backoff_exponent
    c.Min_wait_time = args.min_wait_time
    return c

def check(args):
    """ Error checking
    """
    if args.username is not None or args.userlist or args.members_list:
        if args.verified:
            error("Contradicting Args",
                  "Please use --verified in combination with -s.")
        if args.userid:
            error("Contradicting Args",
                  "--userid and -u cannot be used together.")
        if args.all:
            error("Contradicting Args",
                  "--all and -u cannot be used together")
    elif args.search is None:
        if (args.geo or args.near) is None and not (args.all or args.userid):
            error("Error", "Please use at least -u, -s, -g or --near.")
    elif args.all and args.userid:
        error("Contradicting Args",
              "--all and --userid cannot be used together")
    if args.output is None:
        if args.csv:
            error("Error", "Please specify an output file (Example: -o file.csv).")
        elif args.json:
            error("Error", "Please specify an output file (Example: -o file.json).")
    if args.backoff_exponent <= 0:
        error("Error", "Please specifiy a positive value for backoff_exponent")
    if args.min_wait_time < 0:
        error("Error", "Please specifiy a non negative value for min_wait_time")

# Overrides the default Json function from the twint library
def Json(obj, config):
    "Outputs the passed tweet to the Output configured in c.Output"
    tweet = obj.__dict__
        
    if c.Output == "mongo":
        mongoCol.insert_one(tweet)
        pass
    else:
        # TODO: Implement other outputs.
        print("Only mongodb is currently supported.")
        pass

# c = twint.cli
module.Json = Json
c = twint.Config()

# Load & process config.json
def loadConf(file="config.json"):
    with open('config.json', 'r') as myfile:
        data = myfile.read()
        obj = json.loads(data)


    #TODO: Cleanup these statements
    # Set values that are set in the config.json file
    for value in obj:

        
        if value == "hashtag":
            c.Search = str(obj[value])
        if value == "limit":
            c.Limit = str(obj[value])
        if value == "output":
            c.Output = str(obj[value])
        if value == "since":
            c.Since = str(obj[value])
        if value == "until":
            c.Until = str(obj[value])
        if value == "city":
            c.Near = str(obj[value])
        if value == "recipient":
            c.To = str(obj[value])
        if value == "username":
            c.Username = str(obj[value])   

    return obj


if __name__ == "__main__":

    args = options()
    check(args)
    c = initialize(args)
    try:
        # Load the config.json object
        obj = loadConf()
        args = options()
        check(args)
        c = initialize(args)
        c.Hide_output = True
        c.Store_object = True
        c.Stats = True
        c.Count = True
        # Retrieve mongoDB Connection String from the environment variable called mongoCS
        cs = os.environ['mongoCS']

        # Setup the mongoDB connection
        mongoCl = MongoClient(cs)
        mongoDB = mongoCl["twtdb"]
        mongoCol = mongoDB["tweets"]

        # Scrape tweets and send them to mongoDB
        twint.run.Search(c)

    except FileNotFoundError as identifier:
        print("Missing config.json")
    except KeyError:
        print("Missing \"mongoCS\" environment variable.")
