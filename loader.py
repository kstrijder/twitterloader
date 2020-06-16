import json
import twint
import sys
import twint.output
import twint.format
import os
from pymongo import MongoClient


module = sys.modules["twint.storage.write"]

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

module.Json = Json
c = twint.Config()
c.Store_json = True
c.Hide_output = True
c.Store_object = True
c.Stats = True
c.Count = True
c.Show_hashtags = True
c.User_full = True


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
    try:
        print("Starting")
        # Load the config.json object
        obj = loadConf()
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
