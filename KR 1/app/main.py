from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import os
from . import models

blog_app = FastAPI(title="Мой мини-блог")

posts_db: list[models.BlogPost] = []

author_info = models.Author(name="Дмитрий Волков", id=1, age=20)

@blog_app.get("/")
async def root():
    return {"message": "Добро пожаловать в мой личный блог!"}

@blog_app.get("/about")
async def about_page():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)

@blog_app.post("/combine-words")
async def combine_words(word1: str, word2: str):
    combined = f"{word1} {word2}"
    return {"word1": word1, "word2": word2, "combined": combined}

@blog_app.get("/author")
async def get_author():
    return JSONResponse(content=author_info.model_dump())

@blog_app.post("/check-author")
async def check_author(author: models.Author):
    is_adult = author.age >= 18
    response = author.model_dump()
    response["can_post"] = is_adult
    return response

@blog_app.post("/posts")
async def create_post(post: models.BlogPost):
    posts_db.append(post)
    return {"message": f"Спасибо, {post.author_name}! Ваш пост опубликован."}

@blog_app.get("/posts")
async def get_all_posts():
    return posts_db