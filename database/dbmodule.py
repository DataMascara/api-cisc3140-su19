import mysql.connector
import json
import datetime
import os


def dbconnection():
    #database connection details are hidden. .env file is required 
    mydb = mysql.connector.connect(
        host=os.environ.get('HOST'),
        user=os.environ.get('USERDB'),
        password=os.environ.get('PW'),
        database=os.environ.get('DB'),
    )
    return mydb


class subscriptions_db:
    
    #get subscriptions by username, portname, or portid
    def all_subscriptions_by(column_name, data_value):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        # sql statement
        sql = f"SELECT * FROM subscriptions_vw WHERE {column_name} = '{data_value}'"

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection

        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'all_subscriptions for {data_value}': json_data}, default=myconverter)

    # input: email (string), password (hashed string), username (string), first (String), last (string), description (string), avatarUrl (string)
    # email and username must be unique (use find_user)
    # password should be hashed
    # all fields are required!!
    def add_subscription(username, port_name):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"INSERT INTO subscriptions (userId, portId) VALUES ((SELECT id FROM users WHERE username = '{username}'), (SELECT id FROM ports WHERE name = '{port_name}'))"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return subscriptions_db.all_subscriptions_by('username', username)

    #input: username (string)
    def update_subscription(username, port_name, value):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"UPDATE subscriptions SET isActive = {value} WHERE userId = (SELECT id FROM users WHERE username = '{username}') and portId = (select id from ports where name = '{port_name}')"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return f"subscription {username} to port {port_name} is updated"


class ports_db:

    def all_ports():
        #connect to db
        mydb = dbconnection()
        # create db cursor
        cursor = mydb.cursor(buffered=True)    #open db cursor
        # sql statement
        sql = '''SELECT id, name, description FROM ports where isActive = 1'''

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection

        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'all_ports': json_data}, default=myconverter)

    def add_port(name, description):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"INSERT INTO ports (name, description) VALUES ('{name}', '{description}')"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return posts_db.all_ports()


class users_db:
    # no input, returns all active users
    # returns fields: userid, username, email, first, last, avatarUrl
    def all_users():
        #connect to db
        mydb = dbconnection()
        # create db cursor
        cursor = mydb.cursor(buffered=True)    #open db cursor
        # sql statement
        sql = '''SELECT * FROM users_vw'''

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection

        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'all_users': json_data}, default=myconverter)

    # input: column_name (string), data_value (string or int)
    # options and types:
    #column_name: data_value
    #user_id: int
    #username: string
    #email: string
    # output: userid, username, email, first, last, avatarUrl
    # e.g. http://localhost:5000/find_users?column=username&value=chalshaff12
    # or http://localhost:5000/find_users?column=email&value=chalshaff12@gmail.com
    def find_users(column_name, data_value):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"SELECT * FROM users_vw WHERE {column_name} = '{data_value}'"

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json

        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return json.dumps({'user': json_data}, default=myconverter)

    # input: email (string), password (hashed string), username (string), first (String), last (string), description (string), avatarUrl (string)
    # email and username must be unique (use find_user)
    # password should be hashed
    # all fields are required!!
    def add_user(email, password, username, first, last, avatarurl, description):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"INSERT INTO users (email, password, username, first, last, description, avatarurl) VALUES ('{email}','{password}','{username}','{first}','{last}', '{description}', '{avatarurl}')"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return users_db.find_users('username', username)

#input: username (string)
    def update_user(username, column_name, value_name):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"UPDATE users SET {column_name} = '{value_name}' WHERE username = '{username}'"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return users_db.find_users('username', username)

    #input: username (string)
    def delete_user(username):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"UPDATE users SET isActive = 0 WHERE username = '{username}'"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return f"user {username} deactivated"


class posts_db:

    #column_name = port_id or author
    # data_value depends on the column (always a string)
    #You can do this with all_posts_by(column_name, data_value)
    # posts_db.all_posts_by('postId', 1)
    # posts_db.all_posts_by('postTitle', 'Textbooks for Cheap!')
    def all_posts_by(column_name, data_value):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"SELECT * FROM posts_vw where {column_name} = '{data_value}'"

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection

        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'posts': json_data}, default=myconverter)

   #column_name = port_id or author
    # data_value depends on the column (always a string)
    # e.g. http://localhost:5000/all_posts_by?column=author&value=chalshaff12
    # or http://localhost:5000/all_posts_by?column=port_id&value=1
    def find_posts_by_text(postText, text):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"SELECT * FROM posts_vw where {postText} = '{text}'"

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection

        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'posts': json_data}, default=myconverter)

    def add_post(title, text, port_name, author, image):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"SELECT add_post('{title}','{text}','{port_name}','{author}', '{image}')"
        #sql = f"INSERT INTO posts (title, text, portid, userid, imageUrl) VALUES ('{title}','{text}',(select id from ports where name = '{port_name}'), (select id from users where username = '{author}'), '{image}')"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        
        cursor.close()
        mydb.close()

    
        return posts_db.all_posts_by('postId',result_set[0][0])


    def delete_post(post_id):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"UPDATE posts SET isDeleted = 1 WHERE id = {post_id}"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return f"post {post_id} deleted"

    def update_post(post_id, column_name, data_value):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"UPDATE posts SET {column_name} = '{data_value}' where id = {post_id}"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return posts_db.all_posts_by('author', post_id)


class comments_db:

    def all_comments_by(column_name, data_value):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"SELECT * FROM comments_vw where {column_name} = '{data_value}'"

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection

        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'comments': json_data}, default=myconverter)

    def add_comment(text, post_id, parent_id, author):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"INSERT INTO comments (text, postId, parentId, userId) VALUES ('{text}', {post_id}, {parent_id}, (select id from users where username = '{author}'))"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps([{'error': str(err)},sql])

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return comments_db.all_comments_by('author', author)

    def delete_comment(comment_id):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"UPDATE comments SET isDeleted = 1 WHERE id = {comment_id}"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json        
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return f"comment {comment_id} deleted"

    def update_comment(comment_id, text):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"UPDATE comments SET text = '{text}' where id = {comment_id}"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()

        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return posts_db.all_comments_by('comment_id', comment_id)


class votes_db:

    #type = 'post' or 'comment'
    #column_name = 'saved' or 'vote'
    # data_value = '1' for saved, '1' for upvotes, '-1' for downvotes
    def all_votes_by(username, column_name, data_value, type, operation):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"SELECT * FROM votes_vw where voteUsername = '{username}' and {column_name} {operation} '{data_value}' and type = '{type}'"

        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        result_set = cursor.fetchall()  # save sql result set
        # convert columns and rows into json data
        json_data = [dict(zip([key[0] for key in cursor.description], row))
                     for row in result_set]
        # close database connection
        cursor.close()
        mydb.close()

        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        return json.dumps({'voted_data': json_data}, default=myconverter)

    #saved = 1 or 0
    #vote = -1, 0 or 1
    #type = 'post' or 'comment'
    # item_id = the post or comment ID
    # if saving the post or comment, set vote = 0 or null.
    def add_vote(username, post_id, comment_id, save, vote):
        #connect to db
        mydb = dbconnection()
        cursor = mydb.cursor(buffered=True)    #open db cursor
        sql = f"INSERT INTO votes (userId, postId, commentId, isSaved, vote) VALUES ((select id from users where username = '{username}'), {post_id}, {comment_id}, {save}, {vote})"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return votes_db.all_votes_by(username, 'vote', 0, 'post', '<>')

        # if it is a post, put null for comment_id
        # if it is a comment, put null for post_id
        #column_name = 'isSaved' or 'vote'
        # data_value = 1 or 0 for 'isSaved', 1,0,-1 for 'vote'

    def update_vote(username, post_id, comment_id, column_name, data_value):
        #connect to db
        mydb = dbconnection()

        cursor = mydb.cursor(buffered=True)    #open db cursor

        sql = f"UPDATE votes SET {column_name} = {data_value} WHERE userId = (select id from users where username = '{username}') AND postId = {post_id} or commentId = {comment_id}"

        try:
            cursor.execute(sql)
            mydb.commit()
        except mysql.connector.Error as err:
            return json.dumps({'error': str(err)})

        # close database connection
        cursor.close()
        mydb.close()
        # catch datetime datatype error for json
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return f"vote updated"
