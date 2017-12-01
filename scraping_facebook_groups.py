# Nanda Sundaresan #

import requests, json
from multiprocessing import Manager, Pool

def unwrap_self_insert_message_info(arg, **kwarg):
    return ScrapePage.insert_message_info(*arg, **kwarg)

class ScrapePage():

    def __init__(self, group_id, app_id, app_secret, since_date = "", until_date = ""):
        self.group_id = group_id

        # Access token in order to access all information needed
        self.access_token = app_id + "|" + app_secret

        # (optional parameters)input date formatted as YYYY-MM-DD, in case we will need a start
        # date and an end date to the data we are retrieving
        self.since_date = since_date
        self.until_date = until_date

        # number of posts the API call pulls at a time -- 100 is the max.
        self.limit = 100

        self.general_info = ScrapePage.general_info(self)
        self.member_info = ScrapePage.member_info(self)

        result = ScrapePage.insert_info(self)
        self.post_dict = result

    def general_info(self):
        url = "https://graph.facebook.com/v2.10/{}".format(self.group_id) + \
        "/?fields=id,name,description,owner,privacy,updated_time,admins" + \
        "&access_token={}".format(self.access_token)

        data = (requests.get(url)).json()

        info_dict = dict()

        return(data)

    def member_info(self):
        """
        Obtains information about a page's members, and compiles it into a list.
        Parameters: None
        Returns: final_list, a list of all the members and their ids.
        """
        go_next = True
        final_list = list()
        count = 0
        url = "https://graph.facebook.com/v2.10/{}".format(self.group_id) + \
        "/?fields=members.limit(1000)&access_token={}".format(self.access_token)

        data = (requests.get(url)).json()["members"]

        while go_next:
            for member in data["data"]:
                final_list.append(member)
            if "paging" in data and "next" in data["paging"]:
                    count += len(data["data"])
                    next_url = str(data["paging"]["next"])
                    data = (requests.get(next_url)).json()
                    print str(count) + " members added to list!"
            else:
                count += len(data["data"])
                print str(count) + " members added to list!"
                go_next = False

        return(final_list)

    def insert_info(self):
        """
        Obtains information about a page, and compiles it into a list of posts.
        Parameters: None
        Returns: final_list, a list of all the posts and relevant information.
        """

        # first URL to retrieve just the IDs of each post, to give the rest of the code a starting point
        first_url = "https://graph.facebook.com/v2.10/{}".format(self.group_id) + \
                    "/feed/?fields=id&limit={}&access_token={}&since={}&until={}".format(self.limit,
                    self.access_token, self.since_date, self.until_date)

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
            result = pool.map(unwrap_self_insert_message_info, zip([self]*len(data_list), data_list), 10)
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

    def insert_message_info(self, post):
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
                  "&access_token={}".format(self.access_token)
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
            comments = ScrapePage.insert_comment_info(self, post_info)
            post["comments"] = comments
        if "likes" in post_info:
            likes = ScrapePage.insert_likes_info(self, post_info)
            post["likes"] = likes
        if "reactions" in post_info:
            reactions = ScrapePage.insert_reactions_info(self, post_info)
            post["reactions"] = reactions
        return post

    def insert_likes_info(self, post_info):
        """
        Inserts information about likes to the post, a comment, or a reply. Adds just names of each person who gave a like.
        Parameters: post_info, a post from the page OR a comment of a post.
        Returns: likes_list, a list of all the likes with their information (explained above).
        """
        likes_list = list()
        for like in post_info["likes"]["data"]:
            entry = dict()
            entry["name"] = like["name"]
            entry["id"] = like["id"]
            likes_list.append(entry)
        return likes_list

    def insert_reactions_info(self, post_info):
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

    def insert_comment_info(self, post_info):
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
                sub_comments = ScrapePage.insert_comment_info(self, comment)
                entry["replies"] = sub_comments
            comment_list.append(entry)
            if "likes" in comment:
                sub_likes = ScrapePage.insert_likes_info(self, comment)
                entry["likes"] = sub_likes
            if "reactions" in comment:
                sub_reactions = ScrapePage.insert_reactions_info(self, comment)
                entry["reactions"] = sub_reactions
        return comment_list

    def __str__(self):
        return("{}".format(self.final_dict))
