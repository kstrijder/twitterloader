import json
import twint
import sys

c = twint.Config()
c.Store_json = True
c.Output = "tweets.json"
c.Hide_output = True

# Load & process config.json
def loadConf(file="config.json"):
    with open('config.json', 'r') as myfile:
        data = myfile.read()
        obj = json.loads(data)


    #TODO: Cleanup these statements
    # Set values that are set in the config.json file
    for value in obj:

        if value == "username":
            c.Username = str(obj[value])
        if value == "hashtag":
            c.Search = str(obj[value])
        if value == "limit":
            c.Limit = str(obj[value])
        if value == "since":
            c.Since = str(obj[value])
        if value == "until":
            c.Until = str(obj[value])
        if value == "city":
            c.Near = str(obj[value])
        if value == "recipient":
            c.To = str(obj[value])            

    return obj


if __name__ == "__main__":
    try:
        obj = loadConf()
        print("name: " + str(obj['name']))
        twint.run.Search(c)

    except FileNotFoundError as identifier:
        print("Missing config.json")
