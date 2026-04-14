from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from . import models
from .config import MODE, DOCS_USER, DOCS_PASSWORD
from .exceptions import CustomExceptionA, CustomExceptionB, ErrorResponse
from .db import get_db, Product
from typing import Dict
from pydantic import BaseModel

app = FastAPI(title="KR4")

if MODE == "PROD":
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None

#9.1
@app.post("/products", response_model=models.ProductInDB, status_code=201)
def create_product(product: models.ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/{product_id}", response_model=models.ProductInDB)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise CustomExceptionB(detail="Product not found")
    return product

#10.1
@app.get("/error-a")
def raise_error_a():
    raise CustomExceptionA(
        detail="Хахаха вы ошиблись 400",
        status_code=400
    )

@app.get("/error-b")
def raise_error_b():
    raise CustomExceptionB(
        detail="Хихихи вы ошиблись 404",
        status_code=404
    )

#10.2
@app.post("/validate-user")
def validate_user(user: models.UserValidation):
    return {"message": "User is valid", "user": user.model_dump()}

#11.1, 11.2 
class Item(BaseModel):
    id: int
    name: str
    price: float

class ItemCreate(BaseModel):
    name: str
    price: float

fake_db: Dict[int, Item] = {}
current_id = 1

@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    global current_id
    new_item = Item(id=current_id, **item.model_dump())
    fake_db[current_id] = new_item
    current_id += 1
    return new_item

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in fake_db:
        raise CustomExceptionB(detail="Item not found")
    return fake_db[item_id]

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in fake_db:
        raise CustomExceptionB(detail="Item not found")
    del fake_db[item_id]
    return



@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            status_code=exc.status_code,
            error_type="CustomExceptionA"
        ).model_dump()
    )

@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            status_code=exc.status_code,
            error_type="CustomExceptionB"
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="Ошибка валидации данных",
            status_code=422,
            error_type="ValidationError"
        ).model_dump()
    )