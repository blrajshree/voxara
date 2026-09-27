import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ==========================================
# VOXARA - MODEL TRAINING
# ==========================================

DATASET_PATH = r"E:\voxara\dataset\isl_landmarks.csv"
MODEL_PATH = r"E:\voxara\training\voxara_model.pkl"


# Load dataset
print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded!")
print("Total samples:", len(df))


# ==========================================
# Separate features and labels
# ==========================================

X = df.drop("label", axis=1)
y = df["label"]


print("\nClasses:")
print(y.value_counts())


# ==========================================
# Train / Test Split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# Random Forest Model
# ==========================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ==========================================
# Test Model
# ==========================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n==========================================")
print("VOXARA MODEL RESULTS")
print("==========================================")

print(f"Accuracy: {accuracy * 100:.2f}%")


print("\nClassification Report:")
print(classification_report(y_test, y_pred))


print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# ==========================================
# Save Model
# ==========================================

joblib.dump(model, MODEL_PATH)

print("\n==========================================")
print("MODEL SAVED SUCCESSFULLY!")
print("==========================================")
print(MODEL_PATH)