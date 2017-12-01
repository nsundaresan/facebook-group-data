# Nanda Sundaresan #

from scraping_facebook_groups import ScrapePage
import json, requests, csv
import pandas as pd

group_ids = ["*****"]  # Just replace with any id of the group you want to scrape

app_id = "*****"
app_secret = "*****"  # DO NOT SHARE WITH ANYONE!

# Gets number of reactions for a post
def addReactions(post):
    reaction_dict = {"LIKE": 0, "HAHA": 0, "LOVE": 0, "WOW": 0, "SAD": 0, "ANGRY": 0, "PRIDE": 0,
                    "THANKFUL": 0}

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
    page_info = ScrapePage(id, app_id, app_secret, "2017-11-01", "2017-11-27")

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
    with open('{}.csv'.format(id), 'w') as csv_file:
        writer = csv.writer(csv_file)
        # Column names
        writer.writerow(["id", "type", "author", "created_time", "LIKE",
            "HAHA", "LOVE", "WOW", "SAD", "ANGRY", "PRIDE", "THANKFUL",
            "total_comments_and_replies", "total_reaction_count" ])

        for post in data:
            # Initial information
            row = [id, post['type'], post['author'], post['created_time']]

            # Add reaction information
            reactions = ["LIKE", "HAHA", "LOVE", "WOW", "SAD", "ANGRY", "PRIDE", "THANKFUL"]
            reaction_dict = addReactions(post)
            reaction_count = 0

            for reaction_name in reactions:
                row.append(reaction_dict[reaction_name])
                reaction_count += reaction_dict[reaction_name]

            # Total comment and reply count for post
            row.append(addCommentCount(post))

            # Total reaction count for post
            row.append(reaction_count)

            # To ensure proper encoding
            writer.writerow([val.encode('utf-8') if type(val) is not int else val for val in row])

df = pd.read_csv("*****.csv")
print(df)
