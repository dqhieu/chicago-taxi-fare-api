#!/usr/bin/env python3
"""
Chicago Taxi Fare Prediction API - PRODUCTION VERSION
Optimized for deployment with proper configuration, logging, and error handling
"""

import os
import logging
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import json
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with production configuration
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Production configuration
class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    MODEL_PATH = os.environ.get('MODEL_PATH', 'models/')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

app.config.from_object(ProductionConfig)

# Global variables for model components
model = None
scaler = None
label_encoders = None
model_metadata = None

def load_model_components():
    """Load all model components with error handling"""
    global model, scaler, label_encoders, model_metadata
    
    try:
        model_path = app.config['MODEL_PATH']
        
        # Load model components
        model = joblib.load(os.path.join(model_path, 'chicago_fare_predictor_linear_regression.pkl'))
        scaler = joblib.load(os.path.join(model_path, 'chicago_fare_scaler.pkl'))
        label_encoders = joblib.load(os.path.join(model_path, 'chicago_label_encoders.pkl'))
        
        # Load metadata
        with open(os.path.join(model_path, 'chicago_fare_model_metadata.json'), 'r') as f:
            model_metadata = json.load(f)
        
        logger.info("✅ All model components loaded successfully")
        logger.info(f"📊 Model: {model_metadata['model_name']}")
        logger.info(f"🎯 Performance: {model_metadata['performance']['test_rmse_pct']:.1f}% RMSE")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load model components: {e}")
        return False

def engineer_features(trip_data):
    """Production feature engineering with comprehensive error handling"""
    try:
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
        
        # Add coordinates (use defaults if not provided)
        df['pickup_latitude'] = trip_data.get('pickup_latitude', 41.8781)
        df['pickup_longitude'] = trip_data.get('pickup_longitude', -87.6298)
        df['dropoff_latitude'] = trip_data.get('dropoff_latitude', 41.8781)
        df['dropoff_longitude'] = trip_data.get('dropoff_longitude', -87.6298)
        
        # Trip characteristics
        df['trip_duration_minutes'] = df['trip_seconds'] / 60
        df['speed_mph'] = df['trip_miles'] / (df['trip_duration_minutes'] / 60)
        df['speed_mph'] = df['speed_mph'].fillna(20.0)
        
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
        df['is_efficient_trip'] = (df['efficiency_score'] > 0.1).astype(int)
        
        # Density features
        area_density_map = {
            73: 156, 53: 89, 23: 134, 32: 201, 69: 78,
            5: 45, 41: 67, 28: 123, 44: 89, 76: 56,
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
                    df[f'{col}_encoded'] = 0
            elif col in df.columns:
                df[f'{col}_encoded'] = 0
        
        return df
        
    except Exception as e:
        logger.error(f"Feature engineering error: {e}")
        raise ValueError(f"Feature engineering failed: {e}")

# Initialize model components at startup
logger.info("🚀 Initializing Chicago Taxi Fare Prediction API...")
if not load_model_components():
    logger.error("❌ Failed to initialize model components")
    raise RuntimeError("Model initialization failed")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed status"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'model': model_metadata['model_name'] if model_metadata else 'Not loaded',
            'version': model_metadata['model_version'] if model_metadata else 'Unknown',
            'production_ready': model_metadata['production_ready'] if model_metadata else False,
            'performance': {
                'rmse_percentage': model_metadata['performance']['test_rmse_pct'] if model_metadata else None,
                'r2_score': model_metadata['performance']['test_r2'] if model_metadata else None
            }
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/predict', methods=['POST'])
def predict_fare():
    """Production fare prediction with comprehensive validation"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        trip_data = request.get_json()
        if not trip_data:
            return jsonify({'error': 'Empty request body'}), 400
        
        # Validate required fields
        required_fields = ['trip_miles', 'trip_seconds', 'pickup_community_area', 
                          'dropoff_community_area', 'trip_start_timestamp']
        
        missing_fields = [field for field in required_fields if field not in trip_data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}',
                'required_fields': required_fields
            }), 400
        
        # Validate data types and ranges
        try:
            trip_miles = float(trip_data['trip_miles'])
            trip_seconds = int(trip_data['trip_seconds'])
            pickup_area = int(trip_data['pickup_community_area'])
            dropoff_area = int(trip_data['dropoff_community_area'])
            
            # Basic validation
            if trip_miles <= 0 or trip_miles > 1000:
                return jsonify({'error': 'trip_miles must be between 0 and 1000'}), 400
            if trip_seconds <= 0 or trip_seconds > 86400:  # Max 24 hours
                return jsonify({'error': 'trip_seconds must be between 0 and 86400'}), 400
            if pickup_area < 0 or pickup_area > 77:
                return jsonify({'error': 'pickup_community_area must be between 0 and 77'}), 400
            if dropoff_area < 0 or dropoff_area > 77:
                return jsonify({'error': 'dropoff_community_area must be between 0 and 77'}), 400
                
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid data types: {e}'}), 400
        
        # Add default values for optional fields
        trip_data.setdefault('payment_type', 'Credit Card')
        trip_data.setdefault('company', 'Chicago Taxi')
        
        # Engineer features
        df_features = engineer_features(trip_data)
        
        # Create exact feature set
        feature_columns = model_metadata['feature_columns']
        feature_df = pd.DataFrame()
        
        for col in feature_columns:
            if col in df_features.columns:
                feature_df[col] = df_features[col]
            else:
                # Provide defaults for missing features
                if 'latitude' in col:
                    feature_df[col] = 41.8781
                elif 'longitude' in col:
                    feature_df[col] = -87.6298
                elif 'density' in col:
                    feature_df[col] = 50
                else:
                    feature_df[col] = 0
        
        # Convert to numpy array for prediction
        X_values = feature_df.values
        
        # Scale features if needed
        if model_metadata['performance']['use_scaled']:
            X_processed = scaler.transform(X_values)
        else:
            X_processed = X_values
        
        # Make prediction
        predicted_fare = float(model.predict(X_processed)[0])
        
        # Calculate confidence interval
        model_rmse = model_metadata['performance']['test_rmse']
        lower_bound = max(5.0, predicted_fare - model_rmse)
        upper_bound = predicted_fare + model_rmse
        
        # Business category
        def get_business_category(fare):
            if fare < 10:
                return 'Budget'
            elif fare < 20:
                return 'Standard'
            elif fare < 40:
                return 'Premium'
            else:
                return 'Luxury'
        
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
        
        logger.info(f"✅ Prediction successful: ${predicted_fare:.2f}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Batch prediction endpoint"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        trips_data = data.get('trips', [])
        
        if not trips_data:
            return jsonify({'error': 'No trips provided'}), 400
        
        if len(trips_data) > 100:  # Limit batch size
            return jsonify({'error': 'Maximum 100 trips per batch'}), 400
        
        predictions = []
        for i, trip in enumerate(trips_data):
            try:
                # Use single prediction logic
                trip.setdefault('payment_type', 'Credit Card')
                trip.setdefault('company', 'Chicago Taxi')
                
                df_features = engineer_features(trip)
                feature_columns = model_metadata['feature_columns']
                feature_df = pd.DataFrame()
                
                for col in feature_columns:
                    if col in df_features.columns:
                        feature_df[col] = df_features[col]
                    else:
                        feature_df[col] = 0
                
                X_values = feature_df.values
                
                if model_metadata['performance']['use_scaled']:
                    X_processed = scaler.transform(X_values)
                else:
                    X_processed = X_values
                
                predicted_fare = float(model.predict(X_processed)[0])
                
                model_rmse = model_metadata['performance']['test_rmse']
                lower_bound = max(5.0, predicted_fare - model_rmse)
                upper_bound = predicted_fare + model_rmse
                
                def get_business_category(fare):
                    if fare < 10:
                        return 'Budget'
                    elif fare < 20:
                        return 'Standard'
                    elif fare < 40:
                        return 'Premium'
                    else:
                        return 'Luxury'
                
                predictions.append({
                    'trip_index': i,
                    'predicted_fare': round(predicted_fare, 2),
                    'confidence_interval': {
                        'lower': round(lower_bound, 2),
                        'upper': round(upper_bound, 2)
                    },
                    'business_category': get_business_category(predicted_fare)
                })
                
            except Exception as e:
                predictions.append({
                    'trip_index': i,
                    'error': str(e)
                })
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'successful': len([p for p in predictions if 'error' not in p]),
            'failed': len([p for p in predictions if 'error' in p]),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/predict', '/batch_predict'],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # This should not be used in production
    logger.warning("⚠️  Running with development server - NOT for production!")
    app.run(debug=False, host='0.0.0.0', port=5001)