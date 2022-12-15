from fastapi import FastAPI,Response,HTTPException
from starlette import status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

# my_posts = [{
#     "title":"title1",
#     "content":"content1",
#     "id" : 0
# },{
#     "title":"title2",
#     "content":"content2",
#     "id" : 2
# }]


class Post(BaseModel):
    title:str
    content:str
    published : bool


while True:
    try:
        conn = psycopg2.connect(host="localhost", database = "fastapi", user= "postgres", password = "bytestrone", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('database connected successfully')
        break
    except Exception as error:
        print("database connection failed")
        print("error: ",error)
        time.sleep(2)


def find_post(id):
    for post in my_posts:
        if post["id"]==id:
            return post


def find_index(id):
    for post in my_posts:
        if post["id"]==id:
            return my_posts.index(post)



@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts=cursor.fetchall()
    return {"data":posts}


@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_post(post : Post):
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"posted":new_post}


@app.get("/posts/{id}")
def get_post(id: str):
    cursor.execute("""SELECT * FROM posts WHERE id= %s""",(str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} not found")
    return {"data":post}

@app.get("/posts/recent/latest")
def get_latest():
    cursor.execute("""Select * From posts Order By id Desc LIMIT 1""")
    post=cursor.fetchone()
    print(post)
    return {"data",post}


@app.delete("/posts/delete/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""",(str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id:int,post:Post):
    cursor.execute("""UPDATE posts SET title=%s, content=%s, published = %s WHERE id=%s RETURNING *""",(post.title,post.content,post.published,str(id),))
    post=cursor.fetchone()
    conn.commit()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} not found")
    return {"updated":post}

