import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import pickle

# Dataset path
DATASET_PATH = 'dataset'
IMG_SIZE = 48  # Standard size for facial expression datasets

def load_dataset():
    """Load images and labels from the dataset folder."""
    images = []
    labels = []

    emotion_folders = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

    for emotion in emotion_folders:
        folder_path = os.path.join(DATASET_PATH, 'train', emotion)
        if not os.path.exists(folder_path):
            print(f"Warning: {folder_path} does not exist")
            continue

        print(f"Loading {emotion} images...")
        count = 0
        for filename in os.listdir(folder_path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(folder_path, filename)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                    images.append(img)
                    labels.append(emotion)
                    count += 1
        print(f"Loaded {count} {emotion} images")

    return np.array(images), np.array(labels)

def create_model():
    """Create a CNN model for facial expression recognition."""
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        MaxPooling2D((2, 2)),
        Dropout(0.25),

        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.25),

        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.25),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(7, activation='softmax')  # 7 emotions
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

def train_model():
    """Train the facial expression recognition model."""
    print("Loading dataset...")
    images, labels = load_dataset()

    if len(images) == 0:
        print("No images found in dataset!")
        return

    print(f"Dataset loaded: {len(images)} images")

    # Normalize images
    images = images.astype('float32') / 255.0
    images = images.reshape(images.shape[0], IMG_SIZE, IMG_SIZE, 1)

    # Encode labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    categorical_labels = to_categorical(encoded_labels)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        images, categorical_labels, test_size=0.2, random_state=42, stratify=encoded_labels
    )

    print(f"Training set: {len(X_train)} images")
    print(f"Test set: {len(X_test)} images")

    # Create model
    model = create_model()
    print(model.summary())

    # Callbacks
    early_stopping = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True)
    model_checkpoint = ModelCheckpoint('best_emotion_model.h5', monitor='val_accuracy', save_best_only=True)

    # Train model
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping, model_checkpoint]
    )

    # Save model and label encoder
    model.save('emotion_model.h5')
    with open('label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)

    print("Model trained and saved!")

    # Evaluate
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_accuracy:.4f}")

    return model, label_encoder

if __name__ == "__main__":
    train_model()