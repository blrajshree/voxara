import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score


# ==========================================
# 1. LOAD YOUR EXISTING VOXARA DATASET
# ==========================================

DATASET_PATH = "../dataset/isl_landmarks.csv"

df = pd.read_csv(DATASET_PATH)

print("\nDataset loaded successfully!")
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())


# ==========================================
# 2. FEATURES AND LABEL
# ==========================================

# Last column = sign label
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

print("\nFeature shape:", X.shape)
print("Labels:", np.unique(y))


# ==========================================
# 3. CONVERT LABELS TO NUMBERS
# ==========================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

class_names = label_encoder.classes_

print("\nClass names:")
for i, name in enumerate(class_names):
    print(i, "=", name)


# ==========================================
# 4. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# 5. CREATE SMALL NEURAL NETWORK
# ==========================================

model = tf.keras.Sequential([
    
    tf.keras.layers.Input(
        shape=(X_train.shape[1],)
    ),

    tf.keras.layers.Dense(
        128,
        activation="relu"
    ),

    tf.keras.layers.Dropout(0.2),

    tf.keras.layers.Dense(
        64,
        activation="relu"
    ),

    tf.keras.layers.Dropout(0.2),

    tf.keras.layers.Dense(
        len(class_names),
        activation="softmax"
    )
])


# ==========================================
# 6. COMPILE
# ==========================================

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


print("\nModel created successfully!")


# ==========================================
# 7. TRAIN
# ==========================================

print("\nStarting TensorFlow training...\n")

model.fit(
    X_train,
    y_train,
    validation_split=0.20,
    epochs=30,
    batch_size=32,
    verbose=1
)


# ==========================================
# 8. TEST MODEL
# ==========================================

loss, accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print("\n================================")
print("TENSORFLOW TEST RESULT")
print("================================")

print("Accuracy:", accuracy * 100, "%")


# ==========================================
# 9. SAVE TENSORFLOW MODEL
# ==========================================

model.save("voxara_tf_model.keras")

print("\nTensorFlow model saved:")
print("voxara_tf_model.keras")


# ==========================================
# 10. CONVERT TO TENSORFLOW LITE
# ==========================================

print("\nConverting to TensorFlow Lite...")

converter = tf.lite.TFLiteConverter.from_keras_model(model)

tflite_model = converter.convert()


# ==========================================
# 11. SAVE TFLITE MODEL
# ==========================================

with open("voxara_model.tflite", "wb") as f:
    f.write(tflite_model)


print("\n================================")
print("TFLITE MODEL CREATED!")
print("================================")

print("voxara_model.tflite")


# ==========================================
# 12. SAVE CLASS NAMES
# ==========================================

with open("class_names.txt", "w") as f:
    for name in class_names:
        f.write(str(name) + "\n")


print("\nClass names saved:")
print("class_names.txt")

print("\nDONE!")