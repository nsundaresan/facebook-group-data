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
        return(comment_count)
    else:
        return(0)

def addRepliesCount(post):
    if 'comments' in post.keys():
        replies_count = 0
        for comment in post['comments']:
            if 'replies' in comment:
                replies_count += len(comment['replies'])
        return(replies_count)
    else:
        return(0)

def checkAuthorContrib(post):
    if 'comments' in post.keys():
        author_contrib = False
        author = post['author']

        for comment in post['comments']:
            if comment['author'] == author:
                author_contrib = True
            elif 'replies' in comment:
                for reply in comment['replies']:
                    if reply['author'] == author:
                        author_contrib = True

        return(author_contrib)

    else:
        return(False)

def checkAuthorReaction(post):
    if 'reactions' in post.keys():
        author_contrib = False
        author = post['author']

        for reaction in post['reactions']:
            if reaction['name'] == author:
                author_contrib = True
            elif 'comments' in post.keys():
                for comment in post['comments']:
                    if 'reactions' in comment:
                        for com_reaction in comment['reactions']:
                            if com_reaction['name'] == author:
                                author_contrib = True
                    if 'replies' in comment and author_contrib == False:
                        for reply in comment['replies']:
                            if 'reactions' in reply:
                                for rep_reaction in reply['reactions']:
                                    if rep_reaction['name'] == author:
                                        author_contrib = True

        return(author_contrib)

    else:
        return(False)

# From all the group ids, scrape group data, then make a json and csv file that
# compiles the information.
for id in group_ids:
    # Get basic information from the group page. Creates ScrapePage object
    page_info = ScrapePage(id, app_id, app_secret) #,since_date = "2017-10-04",until_date = "2017-10-05"

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
            "total_comments", "total_replies", "total_comments_and_replies",
            "total_reaction_count", "comments", "author_comment_contrib", "author_reaction_contrib"])

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
            comment_count = addCommentCount(post)
            replies_count = addRepliesCount(post)
            comment_reply_count = comment_count + replies_count
            row.extend([comment_count, replies_count, comment_reply_count])

            # Total reaction count for post
            row.append(reaction_count)

            row = [val.encode('utf-8') if type(val) is not int else val for val in row]

            # Add comment information
            if 'comments' in post.keys():
                comments = post['comments']
                row.append(comments)
            else:
                row.append([])

            # T/F if author replied or reacted to their post or any comments or replies to their post.
            row.append(checkAuthorContrib(post))
            row.append(checkAuthorReaction(post))

            # To ensure proper encoding
            writer.writerow(row)

df = pd.read_csv("227341777331132.csv")
print(df)
