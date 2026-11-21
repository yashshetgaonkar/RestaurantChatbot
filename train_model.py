
import json
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Load training data
with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

X = []
y = []

# Extract patterns and labels
for intent in data["intents"]:
    for pattern in intent["patterns"]:
        X.append(pattern)
        y.append(intent["tag"])

# Build the ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Train model
model.fit(X, y)

# Save trained model
with open("chatbot_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Chatbot model trained successfully!")
print(f"Training examples: {len(X)}")
print(f"Intent categories: {len(set(y))}")
