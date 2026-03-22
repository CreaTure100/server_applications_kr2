from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

sample_product_1 = {
    "product_id": 1001,
    "name": "Ноутбук Lenovo ThinkPad",
    "category": "Электроника",
    "price": 89999.99
}
sample_product_2 = {
    "product_id": 1002,
    "name": "Беспроводные наушники Sony",
    "category": "Аудио",
    "price": 14999.99
}
sample_product_3 = {
    "product_id": 1003,
    "name": "Кожаный рюкзак",
    "category": "Аксессуары",
    "price": 5499.99
}
sample_product_4 = {
    "product_id": 1004,
    "name": "Игровая мышь Logitech",
    "category": "Компьютерные аксессуары",
    "price": 3999.99
}
sample_product_5 = {
    "product_id": 1005,
    "name": "Монитор Samsung 27\"",
    "category": "Электроника",
    "price": 24999.99
}

sample_products = [sample_product_1, sample_product_2, sample_product_3,
sample_product_4, sample_product_5]

@app.get("/product/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/search", response_model=List[Product])
async def search_products(
    keyword: str = Query(..., description="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество результатов")
):
    results = []
    
    for product in sample_products:
        if category and product["category"].lower() != category.lower():
            continue
        
        if keyword.lower() in product["name"].lower():
            results.append(product)
        
        if len(results) >= limit:
            break
    
    return results
