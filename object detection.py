import tensorflow as tf
import numpy as np
from typing import List, Dict

class FCWObjectDetector:
    def __init__(self, input_shape=(224, 224, 3)):
        self.input_shape = input_shape
        self.model = self._build_model()
    
    def _build_model(self):
        # Create a simple CNN for object detection
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(5, activation='softmax')  # 5 object classes
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, X_train, y_train, epochs=10):
        """Train the object detection model"""
        history = self.model.fit(
            X_train, 
            y_train, 
            epochs=epochs,
            validation_split=0.2
        )
        return history
    
    def detect_objects(self, image):
        """Detect objects in an image"""
        preprocessed_image = self._preprocess_image(image)
        predictions = self.model.predict(preprocessed_image)
        return self._interpret_predictions(predictions)
    
    def _preprocess_image(self, image):
        # Resize and normalize image
        resized_image = tf.image.resize(image, self.input_shape[:2])
        normalized_image = resized_image / 255.0
        return np.expand_dims(normalized_image, axis=0)
    
    def _interpret_predictions(self, predictions):
        # Map predictions to object classes
        object_classes = ['car', 'truck', 'pedestrian', 'bicycle', 'motorcycle']
        result = {}
        
        for idx, prob in enumerate(predictions[0]):
            result[object_classes[idx]] = prob
        
        return result

# Example usage
def forward_collision_warning(detected_objects):
    """Generate warning based on object detection"""
    warning_threshold = {
        'car': 0.7,
        'truck': 0.6,
        'pedestrian': 0.8,
        'bicycle': 0.75,
        'motorcycle': 0.7
    }
    
    warnings = []
    for obj, prob in detected_objects.items():
        if prob > warning_threshold[obj]:
            warnings.append(f"High collision risk with {obj}")
    
    return warnings