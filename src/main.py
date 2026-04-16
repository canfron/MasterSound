from fastapi import FastAPI
from src.database import engine
from src.api.v1 import products, sales, orders, stock

app = FastAPI(
    title="MasterSound API",
    description="API for MasterSound electronics store management",
    version="0.1.0"
)

# Include API routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(sales.router, prefix="/api/v1", tags=["sales"])
app.include_router(orders.router, prefix="/api/v1", tags=["orders"])
app.include_router(stock.router, prefix="/api/v1", tags=["stock"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MasterSound API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
