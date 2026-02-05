# train_classifier.py
# Trains a small CNN to classify medicine package images as real vs fake.

import tensorflow as tf
from tensorflow.keras import layers, models
import os

# --- Configuration ---
DATASET_DIR = "dataset"
BATCH_SIZE = 16
IMG_SIZE = (224, 224)
EPOCHS = 10
MODEL_OUT = "model.h5"

# --- Load datasets ---
train_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATASET_DIR, "train"),
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATASET_DIR, "val"),
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
)

# --- Prefetch (faster loading) ---
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.shuffle(100).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# --- Model: use MobileNetV2 as base (pretrained on ImageNet) ---
base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False  # freeze base for quick training

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(64, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid")  # binary classification
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# --- Train ---
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# --- Save model ---
model.save(MODEL_OUT)
print(f"\n✅ Model saved as {MODEL_OUT}")
