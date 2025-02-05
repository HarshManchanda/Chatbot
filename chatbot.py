from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor(dictionary=True)

app = FastAPI()

# CORS allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserQuery(BaseModel):
    query: str

def fetch_data(query: str):
    print(f"Received query: {query}")
    query_lower = query.lower()
    
    # Fetch products by brand
    if "brand" in query_lower:
        words = query_lower.split()
        brand = words[words.index("brand") + 1] if len(words) > words.index("brand") + 1 else None
        print(f"Extracted brand: {brand}")
        if not brand:
            return "Please specify a brand."
        cursor.execute("SELECT name, brand, price, category, description FROM products WHERE brand LIKE %s", (f"%{brand}%",))
        data = cursor.fetchall()
        return format_response(data, "Products")

    # Fetch suppliers by category
    elif "suppliers" in query_lower and "provide" in query_lower:
        words = query_lower.split()
        category = words[words.index("provide") + 1] if len(words) > words.index("provide") + 1 else None
        if not category:
            return "Please specify a category."
        cursor.execute("SELECT id, name, contact_info, product_categories_offered FROM suppliers WHERE JSON_CONTAINS(product_categories_offered, %s)", (f'"{category}"',))
        data = cursor.fetchall()
        return format_response(data, "Suppliers")

    # Fetch product details
    elif "details" in query_lower:
        words = query_lower.split()
        product_name = words[words.index("details") + 2] if "of" in words and len(words) > words.index("of") + 1 else None
        if not product_name:
            return "Please specify a product name."
        cursor.execute("SELECT name, brand, price, category, description FROM products WHERE name LIKE %s", (f"%{product_name}%",))
        data = cursor.fetchall()
        return format_response(data, "Product Details")

    return "Invalid query. Please refine your request."

def format_response(data, data_type):
    """Formats database response for user readability."""
    if not data:
        return "No relevant data found."
    
    print(f"Recieved Data: {data}")
    print(f"Recieved Data Types: {data_type}")
    
    if data_type == "Products":
        return "\n".join([f"'{row['name']}' by {row['brand']} - {row['description']}. Price: ${row['price']}" for row in data])

    if data_type == "Suppliers":
        return "\n".join([f"Supplier: {row['name']}, Contact: {row['contact_info']}" for row in data])

    if data_type == "Product Details":
        return "\n".join([f"'{row['name']}' is a {row['category']} made by {row['brand']}. It costs ${row['price']}. {row['description']}" for row in data])

    return "No relevant data found."

@app.post("/chatbot")
async def chatbot(query: UserQuery):
    try:
        response = fetch_data(query.query)
        return {"response": response}
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
