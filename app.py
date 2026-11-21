
import json
import pickle
import random
import sqlite3

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DB_NAME = "foodchain.db"

# Load trained ML model
with open("chatbot_model.pkl", "rb") as file:
    model = pickle.load(file)

# Load intent responses
with open("intents.json", "r", encoding="utf-8") as file:
    intents_data = json.load(file)

responses = {
    intent["tag"]: intent["responses"]
    for intent in intents_data["intents"]
}

# Initial Fast-Food menu
MENU_ITEMS = [
    ("Classic Burger", "Burgers", 129, "Classic burger with fresh vegetables"),
    ("Cheese Burger", "Burgers", 159, "Burger with melted cheese"),
    ("Double Burger", "Burgers", 199, "Double patty burger"),
    ("Margherita Pizza", "Pizza", 199, "Classic cheese pizza"),
    ("Farmhouse Pizza", "Pizza", 299, "Pizza with fresh vegetables"),
    ("Pepperoni Pizza", "Pizza", 349, "Pizza topped with pepperoni"),
    ("White Sauce Pasta", "Pasta", 219, "Creamy white sauce pasta"),
    ("Red Sauce Pasta", "Pasta", 199, "Tomato-based pasta"),
    ("Veg Sandwich", "Sandwiches", 99, "Fresh vegetable sandwich"),
    ("French Fries", "Sides", 89, "Crispy golden fries"),
    ("Cold Coffee", "Beverages", 119, "Chilled coffee"),
    ("Lemon Soda", "Beverages", 69, "Refreshing lemon soda")
]

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            predicted_intent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    """)

    # Insert menu only if it is empty
    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO menu (name, category, price, description)
            VALUES (?, ?, ?, ?)
        """, MENU_ITEMS)

    conn.commit()
    conn.close()

# Retrieve menu from database
def get_menu():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    items = conn.execute("""
        SELECT id, name, category, price, description
        FROM menu
        ORDER BY category, name
    """).fetchall()

    conn.close()
    return [dict(item) for item in items]

# Save chat
def save_chat(user_message, bot_response, intent):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        INSERT INTO chat_history (user_message, bot_response, predicted_intent)
        VALUES (?, ?, ?)
    """, (user_message, bot_response, intent))
    conn.commit()
    conn.close()

# ML response function
def get_bot_response(message):
    probabilities = model.predict_proba([message])[0]
    best_index = probabilities.argmax()

    intent = model.classes_[best_index]
    confidence = float(probabilities[best_index])

    if confidence < 0.25:
        intent = "unknown"
        response = (
            "Sorry, I didn't understand that. You can ask me about "
            "our menu, food, prices or recommendations."
        )
    else:
        response = random.choice(responses[intent])

    return response, intent, confidence

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Menu API
@app.route("/menu", methods=["GET"])
def menu():
    return jsonify(get_menu())

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a message."}), 400

    response, intent, confidence = get_bot_response(user_message)
    save_chat(user_message, response, intent)

    return jsonify({
        "response": response,
        "intent": intent,
        "confidence": round(confidence, 2)
    })

# Initialize database
init_db()

if __name__ == "__main__":
    app.run(debug=True)
