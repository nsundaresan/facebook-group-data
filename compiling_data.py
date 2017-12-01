# Nanda Sundaresan #

from scraping_facebook_groups import ScrapePage
import json
import requests
import pandas as pd
import csv

group_ids = ["*****"]  # Just replace with any id of the group you want to scrape

app_id = "*****"
app_secret = "*****"  # DO NOT SHARE WITH ANYONE!

# Gets number of likes for a post
def addLikes(post):
    if 'likes' in post.keys():
        return(len(post['likes']))
    else:
        return(0)

# Gets number of reactions for a post
def addReactions(post, reactions):
    reaction_dict = {"LIKE": 0, "HAHA": 0, "LOVE": 0, "WOW": 0, "SAD": 0, "ANGRY": 0}

    if 'reactions' in post.keys():
        for reaction in post['reactions']:
                reaction_dict[reaction['type']] += 1

    return(reaction_dict)

# Gets total number of comments and replies for a post
def addCommentCount(post):
    if 'comments' in post.keys():
        comment_count = len(post['comments'])
        for comment in post['comments']:
            if 'replies' in comment:
                comment_count += len(comment['replies'])
        return(comment_count)
    else:
        return(0)


# From all the group ids, scrape group data, then make a json and csv file that
# compiles the information.
for id in group_ids:
    # Get basic information from the group page. Creates ScrapePage object
    page_info = ScrapePage(id, app_id, app_secret, "2017-10-04", "2017-10-05")

    # Different aspects of a page, including post information, general information and members.
    result = page_info.post_dict
    general_info = page_info.general_info
    member_info = page_info.member_info
    new_json = json.dumps(result)

    # Write the post information into a new json file
    with open("{}.json".format(id), "w") as final_file:
        final_file.write(new_json)

    # Open up json file to work with to create dataframe
    data = json.load(open("{}.json".format(id)))

    # Take page's json data and convert to csv for easy transfer to pandas dataframe.
    with open('{}.csv'.format(id), 'a') as csv_file:
        writer = csv.writer(csv_file)
        # Column names
        writer.writerow(["id", "type", "author", "created time", "likes count", "LIKE",
            "HAHA", "LOVE", "WOW", "SAD", "ANGRY", "number of comments and replies",
            "number of likes and reactions" ])

        for post in data:
            # Initial information
            row = [id, post['type'], post['author'], post['created_time']]

            # Add count for likes
            likes_count = addLikes(post)
            row.append(likes_count)

            # Add reaction information
            reactions = ["LIKE", "HAHA", "LOVE", "WOW", "SAD", "ANGRY"]
            reaction_dict = addReactions(post, reactions)
            reaction_count = 0

            for reaction_name in reactions:
                row.append(reaction_dict[reaction_name])
                reaction_count += reaction_dict[reaction_name]

            # Total comment and reply count for post
            row.append(addCommentCount(post))

            # Total likes and reaction count for post
            row.append(likes_count + reaction_count)

            writer.writerow(row)

df = pd.read_csv("*****.csv")
print(df)
