# Nanda Sundaresan #

import requests
from multiprocessing import Manager, Pool
import json

# Access tokens in order to access all information needed
app_id = "*****"
app_secret = "*****"  # DO NOT SHARE WITH ANYONE!
group_id = "227341777331132"  # Just replace with any id of the group you want to scrape

access_token = app_id + "|" + app_secret

# input date formatted as YYYY-MM-DD, in case we will need a start date and an end date to the data we are retrieving
since_date = ""
until_date = ""

# number of posts the API call pulls at a time -- 100 is the max.
limit = 100

# first URL to retrieve just the IDs of each post, to give the rest of the code a starting point
first_url = "https://graph.facebook.com/v2.10/{}".format(group_id) + \
            "/feed/?fields=id&limit={}&access_token={}&since={}&until={}".format(limit, access_token, since_date, until_date)

def insert_info():
    """
    Obtains information about a page, and compiles it into a list of posts.
    Parameters: None
    Returns: final_list, a list of all the posts and relevant information.
    """
    final_list = list()                      # Final list of all the posts
    count = 0                                # To update us on how many posts we have gone through so far
    data = (requests.get(first_url)).json()  # Data from first API call to get things started
    go_next = True                           # Used as a marker to call the next page of data if there is one

    while go_next:
        manager = Manager()
        data_list = manager.list()

        for post in data["data"] :
            entry = dict()
            entry["id"] = str(post["id"])
            data_list.append(entry)

        pool = Pool(processes=10)
        result = pool.map(insert_message_info, data_list, 10)
        pool.close()
        pool.join()

        final_list.extend(result)

        if "paging" in data:
            count += len(data["data"])
            next_url = str(data["paging"]["next"])
            data = (requests.get(next_url)).json()
            print str(count) + " statuses added to list!"

        else:
            go_next = False

    return final_list

def get_basic_info():
    """Inserts basic information about the group such as group description, type, people in the group, etc."""

def insert_message_info(post):
    """
    Takes a post id, obtains information about that post, and compiles it into an entry. Information about a post includes:
    message, created time, type, link, name, author, comments, likes, and reactions.
    Parameters: post, a dictionary only including post id from which an API call can be executed to get additional
        information about the post.
    Returns: post, a dictionary that includes all the information about a post.
    """
    new_url = "https://graph.facebook.com/v2.10/{}".format(post["id"]) + \
              "/?fields=likes,reactions,message,link,created_time,type," + \
              "name,from,comments{}&limit=100".format("{message,from,likes,reactions,created_time,id,comments}") + \
              "&access_token={}".format(access_token)
    post_info = (requests.get(new_url)).json()
    if "message" in post_info:
        post["message"] = post_info["message"]
    if "created_time" in post_info:
        post["created_time"] = post_info["created_time"]
    if "type" in post_info:
        post["type"] = post_info["type"]
    if "link" in post_info:
        post["link"] = post_info["link"]
    if "name" in post_info:
        post["name"] = post_info["name"]
    if "from" in post_info:
        post["author"] = post_info["from"]["name"]
        post["author_id"] = post_info["from"]["id"]
    if "comments" in post_info:
        comments = insert_comment_info(post_info)
        post["comments"] = comments
    if "likes" in post_info:
        likes = insert_likes_info(post_info)
        post["likes"] = likes
    if "reactions" in post_info:
        reactions = insert_reactions_info(post_info)
        post["reactions"] = reactions
    return post


def insert_likes_info(post_info):
    """
    Inserts information about likes to the post, a comment, or a reply. Adds just names of each person who gave a like.
    Parameters: post_info, a post from the page OR a comment of a post.
    Returns: likes_list, a list of all the likes with their information (explained above).
    """
    likes_list = list()
    for like in post_info["likes"]["data"]:
        likes_list.append(like["name"])
    return likes_list


def insert_reactions_info(post_info):
    """
    Inserts information about reactions to the post, a comment, or a reply. Adds information including: name, and type.
    Parameters: post_info, a post from the page OR a comment of a post.
    Returns: reactions_list, a list of all the reactions with their information (explained above).
    """
    reactions_list = list()
    for reaction in post_info["reactions"]["data"]:
        entry = dict()
        entry["name"] = reaction["name"]
        entry["type"] = reaction["type"]
        entry["id"] = reaction["id"]
        reactions_list.append(entry)
    return reactions_list


def insert_comment_info(post_info):
    """
    Inserts information about each comment including: message, author, created time, id, replies (with message,
    author, created time, id, likes and reactions), likes, and reactions.
    Parameters: post_info, a post on the group page.
    Returns: comment_list, a list of comments with its information (explained above)
    """
    comment_list = list()
    for comment in post_info["comments"]["data"]:
        entry = dict()
        entry["message"] = comment["message"]
        entry["created_time"] = comment["created_time"]
        entry["author"] = comment["from"]["name"]
        entry["author_id"] = comment["from"]["id"]
        entry["id"] = comment["id"]
        if "comments" in comment:
            sub_comments = insert_comment_info(comment)
            entry["replies"] = sub_comments
        comment_list.append(entry)
        if "likes" in comment:
            sub_likes = insert_likes_info(comment)
            entry["likes"] = sub_likes
        if "reactions" in comment:
            sub_reactions = insert_reactions_info(comment)
            entry["reactions"] = sub_reactions
    return comment_list

def main():
    """
    Main method that runs the entire program.
    Parameters: None
    Returns: None
    """
    result = insert_info()

    new_json = json.dumps(result)
    final_file = open("dict.json", "w")
    final_file.write(new_json)
    final_file.close()

if __name__ == '__main__':
    main()
