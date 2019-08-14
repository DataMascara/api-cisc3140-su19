import requests
import json
import os
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_cors import CORS
from database import dbmodule


# This is the file that is invoked to start up a development server. It gets a copy of the app from your package and runs it. This won’t be used in production, but it will see a lot of mileage in development.
app = Flask(__name__)
CORS(app)

"""
ALPHA Back-end API with CRUD(Create, read, update, delete)
for a user-based loggin website.
"""


"""
-------------Endpoint to login-------------
1)Get the user details from front end (either from form or json)
    -Front end will do validation on length and ensure client-side error checking
    -Check to see if the email is taken
2)Send json with success response or error if error (implement try blocks?)
"""

@app.route("/")
def welcome():
    return jsonify({"msg": "Welcome to the api"})

@app.route("/login/", methods=["POST"])
def login():
    res = request.get_json()
    print(res)
    # Grab the user and pw
    user = res["username"]
    password = res["password"]

    # Get the db query into a python dict
    db_result = json.loads(dbmodule.users_db.find_users("username", user))
    print(db_result)
    # Grab the first result of users that match
    db_usr = list(db_result["user"])

    # User Validation to DB goes here
    if len(db_usr) > 0:
        #     #Now that we know the user exists, validate the password
        if db_usr[0]["password"] == password:
            #         #Send token to allow user to login and advance

            return jsonify({"user": db_usr[0]}), 200
        else:
            return jsonify({"err": "Credentials Not Valid!"})
    return jsonify({"err": "User Not Valid!"})


"""
-------------Endpoint to CREATE a new user------------- #CREATE (C)RUD
1)Get the user details from front end (either from form or json)
    -Front end will do validation on length and ensure client-side error checking
2)Send json with success response or error if error (implement try blocks?)
"""


@app.route("/signup/", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        # Grab the form
        res = request.get_json()
        email = res["email"]
        username = res["username"]
        password = res["password"]
        first = res["first"]
        last = res["last"]
        avatarurl = res["avatarurl"]
        description = res["description"]
        added_user = dbmodule.users_db.add_user(
            email, password, username, first, last, description, avatarurl
        )
    try:
        # Returning the added user
        return added_user, 201
    except:
        return jsonify({"err": added_user}), 401


"""
-------------Endpoint to GET an existing user-------------#READ from C(R)UD
1)Get the user details from front end (either from form or json)
    -Front end will do validation on length and ensure client-side error checking
    -Check to see if the email is taken
2)Send json with success response or error if error (implement try blocks?)

"""


@app.route("/user/", methods=["GET"])
def user():
    res = request.get_json()  # Grab the response as a python dict from json sent
    # User Validation to DB goes here
    user_wanted = res["username"]
    response = json.loads(dbmodule.users_db.find_users("username", user_wanted))
    print(response)
    found = len(response["user"]) > 0
    if found:
        return jsonify(response), 200
    else:
        return jsonify({"error": "User Not Found!"}), 404


"""
-------------Endpoint to update a user's info-------------
1)Get the user ID
    -Get things they want to change
        -We'll assume one thing changes at a time!
    -Update the database with the things they wanted to edit
        -Front end will do validation?
2)Send json with success response or error if error (implement try blocks?)
"""


@app.route("/update/", methods=["PUT"])
def update_user():
    # Grab the form data(could also be a json, if we front end sends that instead)
    res = request.get_json()
    username = res["username"]
    field_to_update = res["field"]
    value = res["value"]
    # Grab the DB result
    db_res = json.loads(dbmodule.users_db.update_user(username, field_to_update, value))
    # If the user exists
    if len(db_res["user"]) > 0:
        # Call db to do the update on that user's data
        return jsonify({"msg": "Update Success"}), 202
    else:
        # Signal DB Error
        return jsonify({"err": "User Invalid"}), 409
    # return jsonify({"err": "Bad request"}), 400


"""
-------------Endpoint to delete a user-------------
1)Get the user ID
    -Update the database with removing the delete
2)Send json with success response or error if error (implement try blocks?)
TODO:
-> Add check to see if user exists first.
"""
@app.route("/delete-user/", methods=["DELETE"])
def delete_user():
    # Grab the form data(could also be a json, if we front end sends that instead)
    res = request.get_json()  # Grab the request's form
    user = res["username"]
    # Check if user exists
    user_exist = (
        len(json.loads(dbmodule.users_db.find_users("username", user))["user"]) > 0
    )
    if user_exist:
        # Call db to delete that user's data
        dbmodule.users_db.find_users("username", user)
        return jsonify({"msg": f"Deactivated {user} successfully"}), 202
    else:
        # Signal that the user is invalid
        return jsonify({"err": "User Invalid"}), 409


@app.route("/allports/", methods=["GET"])
def get_all_ports():
    ports = dbmodule.ports_db.all_ports()
    print(ports)
    # Simply return the json of ports.
    return ports


# Returns All ports from database
@app.route("/newpost/", methods=["POST"])
def new_post():
    res = request.get_json()  # Grab the response as a python dict from json sent
    # User Validation to DB goes here
    img = res['image']
    title = res["title"]
    text = res["text"]
    portname = res["portname"]
    username = res["username"]
    user_id = json.loads(dbmodule.users_db.find_users("username", username))["user"][0]["userId"]
    # Returns the added post from this user
    response = json.loads(
        dbmodule.posts_db.add_post(title, text, portname, username, img))
    # Grab the added post
    db_res = json.loads(dbmodule.posts_db.find_posts_by_text("postText", text))
    # Send that back to the calling_api
    return db_res


# Function dbmodule.posts_db.all_posts_by(column_name, data_value)
# dbmodule.posts_db.all_posts_by('portId', 1)

# dbmodule.posts_db.all_posts_by('portName', 'main')
@app.route("/posts-by-portname/", methods=["GET"])
def get_posts():
    res = request.get_json()
    port_name = res["portname"]
    posts = json.loads(dbmodule.posts_db.all_posts_by("portname", port_name))["posts"]
    # posts.sort(key= lambda x:x["votes"], reverse=True)
    # will sort by newest since thats the default
    posts.sort(key=lambda x: x["dateCreated"], reverse=True)
    port = {"name": port_name, "posts": posts}
    return port

@app.route("/post-by-title/", methods= ["GET"])
def get_post():
    req = request.get_json()
    title = req['title']
    print(title)
    db_res = json.loads(dbmodule.posts_db.all_posts_by('postTitle', title))['posts'][0]
    print(db_res) 
    return db_res

@app.route("/my-posts/", methods=["GET"])
def get_posts_username():
    res = request.get_json()
    username = res["username"]
    posts = json.loads(dbmodule.posts_db.all_posts_by("author", username))["posts"]
    print(posts)
    # will sort by newest since thats the default
    posts.sort(key=lambda x: x["dateCreated"], reverse=True)
    port = {"name": "user history", "posts": posts}
    return port


# Display Posts Relevant to User Given a User id
# Obtain the ids of all the Ports to which the User is subscribed
@app.route("/ports-for-username/", methods=["GET"])
def get_ports_username():
    res = request.get_json()
    username = res["username"]
    # Clean up result here
    return dbmodule.subscriptions_db.all_subscriptions_by("username", username)


@app.route("/subscribe-to-port/", methods=["POST"])
def subscribe_to_port():
    res = request.get_json()
    username = res["username"]
    portname = res["portname"]
    # Clean up result here
    # We first try to add subscription to db
    response = json.loads(
        dbmodule.subscriptions_db.add_subscription(username, portname)
    )
    try:
        # If there is an error then that means there is already an subscription so we will have to set it to active
        print(response["error"])
        return dbmodule.subscriptions_db.update_subscription(username, portname, True)
    except:
        return response


@app.route("/unsubscribe-to-port/", methods=["POST"])
def unsubscribe_to_port():
    res = request.get_json()
    username = res["username"]
    portname = res["portname"]
    return dbmodule.subscriptions_db.update_subscription(username, portname, False)


@app.route("/posts-from-subscribed-ports/")
def get_subscribed_posts():
    res = request.get_json()
    username = res["username"]
    ports = json.loads(
        dbmodule.subscriptions_db.all_subscriptions_by("username", username)
    )
    ports = ports["all_subscriptions for {data_value}"]
    # print(ports)
    # creates a empty list where the post will be stored
    posts = []
    # iterates through the ports
    for i in ports:
        # print(i)
        # iterates through the posts of the ports
        for j in json.loads(dbmodule.posts_db.all_posts_by("portName", i["portName"]))[
            "posts"
        ]:
            # print(j)
            posts.append(j)
    # will sort by newest since thats the default
    posts.sort(key=lambda x: x["dateCreated"], reverse=True)
    return json.dumps({"posts": posts})


@app.route("/votes-for-username/", methods=["GET"])
def get_votes():
    res = request.get_json()
    username = res['username']
    print(username)
    upvotes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "post", "<>"))
    print(upvotes)
    return upvotes


@app.route("/vote/", methods=['POST'])
def vote():
    res = request.get_json()
    username = res['username']
    postId = res['postId']
    value = res['value']
    originalValue = res['originalValue']

    # if originalValue == 1 and value == ++ you're removing the vote
    # if originalValue == -1 and value == -- you're removing the vote
    if originalValue == '1' and value == '++' or originalValue == '-1' and value == '--':
        new_votes = json.loads(dbmodule.votes_db.add_vote(username, postId, 'null', 0, 0))
        try:
            new_votes['voted_data']
        except:
            dbmodule.votes_db.update_vote(username, postId, 'null', 'vote', 0)
            new_votes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "post", "<>"))
    # if originalValue == '' and value == ++ you're upvoting
    # if originalValue == '-1' and value == ++ you're upvoting
    elif originalValue == '' and value == '++' or originalValue == '-1' and value == '++':
        new_votes = dbmodule.votes_db.add_vote(username, postId, 'null', 0, 1)
        try:
            new_votes['voted_data']
        except:
            response = dbmodule.votes_db.update_vote(username, postId, 'null', 'vote', 1)
            new_votes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "post", "<>"))
    # if originalValue == '' and value == -- you're downvoting
    # if originalValue == '-1' and value == -- you're downvoting
    elif originalValue == '' and value == '--' or originalValue == '1' and value == '--':
        new_votes = json.loads(dbmodule.votes_db.add_vote(username, postId, 'null', 0, -1))
        try:
            new_votes['voted_data']
        except:
            dbmodule.votes_db.update_vote(username, postId, 'null', 'vote', -1)
            new_votes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "post", "<>"))
    return new_votes


@app.route("/comment-votes-for-username/", methods=["GET"])
def get_comment_votes():
    res = request.get_json()
    username = res['username']
    print(username)
    upvotes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "comment", "<>"))
    print(upvotes)
    return upvotes

@app.route("/vote-comment/", methods=['POST'])
def vote_comment():
    res = request.get_json()
    username = res['username']
    commentId = res['commentId']
    value = res['value']
    originalValue = res['originalValue']

    # if originalValue == 1 and value == ++ you're removing the vote
    # if originalValue == -1 and value == -- you're removing the vote
    if originalValue == '1' and value == '++' or originalValue == '-1' and value == '--':
        new_votes = json.loads(dbmodule.votes_db.add_vote(username, 'null', commentId, 0, 0))
        try:
            new_votes['voted_data']
        except:
            dbmodule.votes_db.update_vote(username, "null", commentId, 'vote', 0)
            new_votes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "comment", "<>"))
    # if originalValue == '' and value == ++ you're upvoting
    # if originalValue == '-1' and value == ++ you're upvoting
    elif originalValue == '' and value == '++' or originalValue == '-1' and value == '++':
        new_votes = dbmodule.votes_db.add_vote(username, "null", commentId, 0, 1)
        try:
            new_votes['voted_data']
        except:
            response = dbmodule.votes_db.update_vote(username, "null", commentId, 'vote', 1)
            new_votes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "comment", "<>"))
    # if originalValue == '' and value == -- you're downvoting
    # if originalValue == '-1' and value == -- you're downvoting
    elif originalValue == '' and value == '--' or originalValue == '1' and value == '--':
        new_votes = json.loads(dbmodule.votes_db.add_vote(username, "null", commentId, 0, -1))
        try:
            new_votes['voted_data']
        except:
            dbmodule.votes_db.update_vote(username, "null", commentId, 'vote', -1)
            new_votes = json.loads(dbmodule.votes_db.all_votes_by(username, "vote", 0, "comment", "<>"))
    return new_votes

'''
-----COMMENTS FROM POST
'''
@app.route("/comments-by-post/", methods=["GET"])
def get_comments():
    res = request.get_json()
    # Get's comments given post ID
    post_id = res['id']
    db_comm = json.loads(dbmodule.comments_db.all_comments_by('postId',post_id))
    comments = []
    for comment in db_comm['comments']:
        if comment['parentId'] == None:
         comments.append(comment)
    print(comments)
    replies = []
    for comment in db_comm['comments']:
        print("PID:")
        print(comment['parentId'])
        if comment['parentId'] != None:
         {"reply":comment}   
         replies.append(comment)
    print(replies)
    # print(comments)
    return jsonify({"comments":comments, "replies":replies})
'''
---- ADD COMMENT -----
'''
@app.route("/add-comment/", methods = ["POST"])
def add_comment_post():
    res = request.get_json()
    text = res['text']
    post_id = res['postId']
    author = res['author']
    
    try:
        parent_id = res['parentId']
    except: 
        parent_id = "NULL"
    

    comment = dbmodule.comments_db.add_comment(text, post_id, parent_id, author)
    print("okay")
    print(comment)
    return comment
'''
---- POST BY ID  -----
'''
@app.route("/post-by-id/", methods = ["GET"])
def post_by_id():
    res = request.get_json()
    post_id = res['id']
    post = json.loads(dbmodule.posts_db.all_posts_by("postId", post_id))
    print(post)
    return post




"""
---- Getting All Users ----
"""


@app.route("/allusers/")
def all_users():
    return json.loads(dbmodule.users_db.all_users())


if __name__ == "__main__":
    app.run(debug=True)
