#!/usr/bin/env python3
"""
Simple model classes for Render compatibility (no numpy dependencies)
"""

class SimpleLinearModel:
    def __init__(self):
        # Simple fare calculation: base + distance * rate + time * rate
        self.base_fare = 3.25
        self.distance_rate = 2.25  
        self.time_rate = 0.35
        self.coefficients = {
            'trip_miles': 2.25,
            'trip_seconds': 0.0058,  # Convert to minutes * rate
            'is_peak_hour': 1.50,
            'is_weekend': -0.75,
            'pickup_community_area': 0.01,
            'dropoff_community_area': 0.01,
            'hour': 0.05,
            'day_of_week': -0.1,
            'month': 0.02
        }
    
    def predict(self, X):
        """Simple prediction without numpy dependencies"""
        if hasattr(X, 'values'):  # DataFrame
            X = X.values
        
        predictions = []
        for row in X:
            fare = self.base_fare
            # Simple feature mapping (first 9 features)
            features = ['trip_miles', 'trip_seconds', 'is_peak_hour', 'is_weekend', 
                       'pickup_community_area', 'dropoff_community_area', 
                       'hour', 'day_of_week', 'month']
            
            for i, feature in enumerate(features):
                if i < len(row) and feature in self.coefficients:
                    fare += row[i] * self.coefficients[feature]
            
            predictions.append(max(fare, 2.50))  # Minimum fare
        
        return predictions

class SimpleScaler:
    def __init__(self):
        self.mean_ = [5.2, 1800, 0.3, 0.3, 35, 35, 12, 3, 6]  # Approximate means
        self.scale_ = [3.0, 600, 0.5, 0.5, 20, 20, 6, 2, 3]   # Approximate scales
    
    def transform(self, X):
        """Simple scaling without numpy"""
        if hasattr(X, 'values'):
            X = X.values
        
        scaled = []
        for row in X:
            scaled_row = []
            for i, val in enumerate(row):
                if i < len(self.mean_):
                    scaled_val = (val - self.mean_[i]) / self.scale_[i]
                    scaled_row.append(scaled_val)
                else:
                    scaled_row.append(val)
            scaled.append(scaled_row)
        return scaled

class SimpleLabelEncoder:
    def __init__(self, categories=None):
        self.categories = categories or ['Credit Card', 'Cash', 'Unknown']
        self.mapping = {cat: i for i, cat in enumerate(self.categories)}
    
    def transform(self, values):
        return [self.mapping.get(str(val), 0) for val in values]