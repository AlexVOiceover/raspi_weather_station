# Real AI for Weather Station - Tiny Neural Network
import time

class TinyWeatherPerceptron:
    """Simple neural network that learns weather comfort patterns"""
    
    def __init__(self):
        # Neural network weights - start with small random values
        self.weights = [0.02, 0.01, -0.5]  # [temp_weight, humidity_weight, bias]
        self.learning_rate = 0.005
        self.prediction_count = 0
        
    def predict_comfort_level(self, temp, humidity):
        """
        Neural network forward pass
        Returns comfort probability between 0.0 and 1.0
        """
        # Linear combination of inputs
        weighted_sum = (temp * self.weights[0] + 
                       humidity * self.weights[1] + 
                       self.weights[2])
        
        # Sigmoid activation function (approximated for microcontroller)
        if weighted_sum > 5:
            return 0.99
        elif weighted_sum < -5:
            return 0.01
        else:
            # Simple sigmoid approximation
            return 0.5 + weighted_sum / 10
    
    def learn_from_feedback(self, temp, humidity, comfort_feedback):
        """
        REAL AI: Backpropagation learning algorithm
        comfort_feedback: 0.0 (uncomfortable) to 1.0 (very comfortable)
        """
        # Forward pass to get current prediction
        prediction = self.predict_comfort_level(temp, humidity)
        
        # Calculate error (how wrong we were)
        error = comfort_feedback - prediction
        
        # Backpropagation: Update weights using gradient descent
        self.weights[0] += self.learning_rate * error * temp
        self.weights[1] += self.learning_rate * error * humidity
        self.weights[2] += self.learning_rate * error
        
        # Prevent weights from growing too large
        for i in range(len(self.weights)):
            if self.weights[i] > 1.0:
                self.weights[i] = 1.0
            elif self.weights[i] < -1.0:
                self.weights[i] = -1.0
    
    def record_prediction(self, temp, humidity):
        """
        Record that we made a prediction (no fake learning)
        """
        self.prediction_count += 1
        
    def learn_from_user_feedback(self, temp, humidity, user_rating):
        """
        REAL LEARNING: Learn from actual user feedback
        user_rating: 0.0 (very uncomfortable) to 1.0 (very comfortable)
        """
        self.learn_from_feedback(temp, humidity, user_rating)
        print(f"Neural network learned: {temp}°C, {humidity}% -> {user_rating} comfort")
    
    def get_comfort_description(self, comfort_level):
        """Convert comfort probability to human-readable description"""
        if comfort_level >= 0.8:
            return "Very Comfortable"
        elif comfort_level >= 0.6:
            return "Comfortable"
        elif comfort_level >= 0.4:
            return "Moderate"
        elif comfort_level >= 0.2:
            return "Uncomfortable"
        else:
            return "Very Uncomfortable"
    
    def get_learning_stats(self):
        """Return statistics about the neural network's learning"""
        return {
            'predictions_made': self.prediction_count,
            'temp_weight': self.weights[0],
            'humidity_weight': self.weights[1],
            'bias': self.weights[2],
            'learning_rate': self.learning_rate
        }