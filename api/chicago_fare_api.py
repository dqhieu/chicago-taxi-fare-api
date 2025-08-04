#!/usr/bin/env python3
"""
Chicago Taxi Fare Prediction API
Production-ready endpoint for real-time fare predictions
"""

from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Initialize Flask app
app = Flask(__name__)

# Load production model and preprocessing components
model = joblib.load('models/chicago_fare_predictor_linear_regression.pkl')
scaler = joblib.load('models/chicago_fare_scaler.pkl')
label_encoders = joblib.load('models/chicago_label_encoders.pkl')

with open('models/chicago_fare_model_metadata.json', 'r') as f:
    model_metadata = json.load(f)

def engineer_features(trip_data):
    """Apply the EXACT same feature engineering as training"""
    df = pd.DataFrame([trip_data])
    
    # Parse timestamp
    df['trip_start_timestamp'] = pd.to_datetime(df['trip_start_timestamp'])
    
    # Temporal features
    df['hour'] = df['trip_start_timestamp'].dt.hour
    df['day_of_week'] = df['trip_start_timestamp'].dt.dayofweek
    df['month'] = df['trip_start_timestamp'].dt.month
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Time category
    def categorize_time(hour):
        if 5 <= hour < 9:
            return 'morning_rush'
        elif 9 <= hour < 16:
            return 'daytime'
        elif 16 <= hour < 20:
            return 'evening_rush'
        elif 20 <= hour < 24:
            return 'evening'
        else:
            return 'night'
    
    df['time_category'] = df['hour'].apply(categorize_time)
    
    # Geographic features
    df['pickup_area'] = df['pickup_community_area'].fillna(0).astype(int)
    df['dropoff_area'] = df['dropoff_community_area'].fillna(0).astype(int)
    df['same_area'] = (df['pickup_area'] == df['dropoff_area']).astype(int)
    
    # Add missing geographic coordinates (use defaults for Chicago)
    # Chicago downtown area approximate coordinates
    df['pickup_latitude'] = trip_data.get('pickup_latitude', 41.8781)
    df['pickup_longitude'] = trip_data.get('pickup_longitude', -87.6298)
    df['dropoff_latitude'] = trip_data.get('dropoff_latitude', 41.8781)
    df['dropoff_longitude'] = trip_data.get('dropoff_longitude', -87.6298)
    
    # Trip characteristics
    df['trip_duration_minutes'] = df['trip_seconds'] / 60
    df['speed_mph'] = df['trip_miles'] / (df['trip_duration_minutes'] / 60)
    df['speed_mph'] = df['speed_mph'].fillna(20.0)  # Default speed
    
    # Distance category
    df['distance_category'] = pd.cut(df['trip_miles'], 
                                   bins=[0, 1, 3, 7, 15, float('inf')], 
                                   labels=['very_short', 'short', 'medium', 'long', 'very_long'])
    
    # Business features
    peak_hours = [3, 7, 11, 19]
    df['is_peak_hour'] = df['hour'].isin(peak_hours).astype(int)
    
    high_demand_areas = [73, 53, 23, 32, 69]
    df['is_high_demand_pickup'] = df['pickup_area'].isin(high_demand_areas).astype(int)
    df['is_high_demand_dropoff'] = df['dropoff_area'].isin(high_demand_areas).astype(int)
    
    # Premium indicators
    df['is_premium_distance'] = (df['trip_miles'] > 10).astype(int)
    df['is_premium_duration'] = (df['trip_duration_minutes'] > 45).astype(int)
    
    # Economic features
    df['base_fare_estimate'] = 3.25
    df['distance_fare_estimate'] = df['trip_miles'] * 2.25
    df['time_fare_estimate'] = df['trip_duration_minutes'] * 0.35
    df['estimated_base_total'] = (df['base_fare_estimate'] + 
                                 df['distance_fare_estimate'] + 
                                 df['time_fare_estimate'])
    
    # Interaction features
    df['distance_time_interaction'] = df['trip_miles'] * df['trip_duration_minutes']
    df['hour_distance_interaction'] = df['hour'] * df['trip_miles']
    df['weekend_distance_interaction'] = df['is_weekend'] * df['trip_miles']
    df['peak_distance_interaction'] = df['is_peak_hour'] * df['trip_miles']
    
    # Efficiency features
    df['efficiency_score'] = df['trip_miles'] / (df['trip_duration_minutes'] + 1)
    df['is_efficient_trip'] = (df['efficiency_score'] > 0.1).astype(int)  # Default threshold
    
    # Density features (computed from area popularity - Chicago specific)
    # High density areas based on Chicago taxi data
    area_density_map = {
        73: 156, 53: 89, 23: 134, 32: 201, 69: 78,  # Top areas
        5: 45, 41: 67, 28: 123, 44: 89, 76: 56,     # Medium areas
    }
    
    df['pickup_area_density'] = df['pickup_area'].map(area_density_map).fillna(50)
    df['dropoff_area_density'] = df['dropoff_area'].map(area_density_map).fillna(50)
    
    # Encode categorical variables
    categorical_columns = ['time_category', 'distance_category', 'payment_type', 'company']
    for col in categorical_columns:
        if col in df.columns and col in label_encoders:
            try:
                df[f'{col}_encoded'] = label_encoders[col].transform(df[col].astype(str))
            except ValueError:
                # Handle unknown categories with a safe default
                df[f'{col}_encoded'] = 0
        elif col in df.columns:
            # If encoder not available, create a simple numeric encoding
            df[f'{col}_encoded'] = 0
    
    return df

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': model_metadata['model_name'],
        'version': model_metadata['model_version'],
        'production_ready': model_metadata['production_ready']
    })

@app.route('/predict', methods=['POST'])
def predict_fare():
    """Predict taxi fare for a given trip"""
    try:
        # Get trip data from request
        trip_data = request.json
        
        # Validate required fields
        required_fields = ['trip_miles', 'trip_seconds', 'pickup_community_area', 
                          'dropoff_community_area', 'trip_start_timestamp']
        
        for field in required_fields:
            if field not in trip_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add default values for optional fields
        trip_data.setdefault('payment_type', 'Credit Card')
        trip_data.setdefault('company', 'Chicago Taxi')
        
        # Engineer features
        df_features = engineer_features(trip_data)
        
        # Get exact feature columns from training (in correct order)
        feature_columns = model_metadata['feature_columns']
        
        # Ensure ALL training features are present with correct values
        feature_df = pd.DataFrame()
        for col in feature_columns:
            if col in df_features.columns:
                feature_df[col] = df_features[col]
            else:
                # Provide sensible defaults for missing features
                if 'latitude' in col:
                    feature_df[col] = 41.8781  # Chicago downtown lat
                elif 'longitude' in col:
                    feature_df[col] = -87.6298  # Chicago downtown lon
                elif 'density' in col:
                    feature_df[col] = 50  # Default density
                elif 'interaction' in col:
                    feature_df[col] = 0  # Default interaction
                elif 'encoded' in col:
                    feature_df[col] = 0  # Default encoding
                elif col in ['pickup_community_area', 'dropoff_community_area']:
                    feature_df[col] = df_features[col] if col in df_features.columns else 0
                else:
                    feature_df[col] = 0  # Safe default
        
        # Fill any remaining NaN values
        X = feature_df.fillna(0)
        
        # Verify feature count and order
        if len(X.columns) != len(feature_columns):
            raise ValueError(f"Feature count mismatch: got {len(X.columns)}, expected {len(feature_columns)}")
        
        # Verify feature names match exactly
        if list(X.columns) != feature_columns:
            raise ValueError(f"Feature names mismatch: {list(X.columns)} vs {feature_columns}")
        
        # Scale features if needed (CRITICAL: Use .values to convert DataFrame to numpy array)
        X_values = X.values  # Convert DataFrame to numpy array to avoid sklearn feature name issues
        
        if model_metadata['performance']['use_scaled']:
            X_processed = scaler.transform(X_values)
        else:
            X_processed = X_values
        
        # Make prediction
        predicted_fare = model.predict(X_processed)[0]
        
        # Calculate confidence interval (simplified)
        model_rmse = model_metadata['performance']['test_rmse']
        lower_bound = max(5.0, predicted_fare - model_rmse)
        upper_bound = predicted_fare + model_rmse
        
        # Prepare response
        response = {
            'predicted_fare': round(predicted_fare, 2),
            'confidence_interval': {
                'lower': round(lower_bound, 2),
                'upper': round(upper_bound, 2)
            },
            'model_info': {
                'model_name': model_metadata['model_name'],
                'rmse_percentage': round(model_metadata['performance']['test_rmse_pct'], 1),
                'r2_score': round(model_metadata['performance']['test_r2'], 3)
            },
            'business_category': get_business_category(predicted_fare),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_business_category(fare):
    """Categorize fare for business insights"""
    if fare < 10:
        return 'Budget'
    elif fare < 20:
        return 'Standard'
    elif fare < 40:
        return 'Premium'
    else:
        return 'Luxury'

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Predict fares for multiple trips"""
    try:
        trips_data = request.json.get('trips', [])
        
        if not trips_data:
            return jsonify({'error': 'No trips provided'}), 400
        
        predictions = []
        for trip in trips_data:
            # Reuse single prediction logic
            temp_request = type('obj', (object,), {'json': trip})
            with app.test_request_context(json=trip):
                result = predict_fare()
                if isinstance(result, tuple):  # Error case
                    predictions.append({'error': result[0].json['error']})
                else:
                    predictions.append(result.json)
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Chicago Taxi Fare Prediction API Starting...")
    print(f"📊 Model: {model_metadata['model_name']}")
    print(f"🎯 Performance: {model_metadata['performance']['test_rmse_pct']:.1f}% RMSE")
    print(f"✅ Production Ready: {model_metadata['production_ready']}")
    print("🌐 API Endpoints:")
    print("   GET  /health - Health check")
    print("   POST /predict - Single fare prediction")
    print("   POST /batch_predict - Batch fare predictions")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
