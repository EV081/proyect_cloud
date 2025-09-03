from fastapi import FastAPI, HTTPException
DB_PATH = "/data/app.db"
os.makedirs("/data", exist_ok=True)
_lock = threading.Lock()


# Crear tabla si no existe
with sqlite3.connect(DB_PATH) as conn:
c = conn.cursor()
c.execute(
"""
CREATE TABLE IF NOT EXISTS items (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
description TEXT DEFAULT ""
)
"""
)
conn.commit()


class ItemIn(BaseModel):
name: str
description: str = ""


class Item(ItemIn):
id: int


app = FastAPI(title="CRUD API", version="1.0.0")


@app.get("/")
def root():
return {"status": "ok"}


@app.get("/items", response_model=list[Item])
def list_items():
with _lock, sqlite3.connect(DB_PATH) as conn:
c = conn.cursor()
c.execute("SELECT id, name, description FROM items")
rows = c.fetchall()
return [Item(id=r[0], name=r[1], description=r[2]) for r in rows]


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
with _lock, sqlite3.connect(DB_PATH) as conn:
c = conn.cursor()
c.execute("SELECT id, name, description FROM items WHERE id=?", (item_id,))
r = c.fetchone()
if not r:
raise HTTPException(status_code=404, detail="Item not found")
return Item(id=r[0], name=r[1], description=r[2])


@app.post("/items", response_model=Item, status_code=201)
def create_item(data: ItemIn):
with _lock, sqlite3.connect(DB_PATH) as conn:
c = conn.cursor()
c.execute("INSERT INTO items(name, description) VALUES(?, ?)", (data.name, data.description))
conn.commit()
new_id = c.lastrowid
return Item(id=new_id, name=data.name, description=data.description)


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, data: ItemIn):
with _lock, sqlite3.connect(DB_PATH) as conn:
c = conn.cursor()
c.execute("UPDATE items SET name=?, description=? WHERE id=?", (data.name, data.description, item_id))
if c.rowcount == 0:
raise HTTPException(status_code=404, detail="Item not found")
conn.commit()
return Item(id=item_id, name=data.name, description=data.description)


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
with _lock, sqlite3.connect(DB_PATH) as conn:
c = conn.cursor()
c.execute("DELETE FROM items WHERE id=?", (item_id,))
if c.rowcount == 0:
raise HTTPException(status_code=404, detail="Item not found")
conn.commit()
return