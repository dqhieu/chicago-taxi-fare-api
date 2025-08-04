#!/usr/bin/env python3
"""
Quick test to debug the Chicago data loader
"""

import pandas as pd
import numpy as np
import sys
import os

# Add current directory to path
sys.path.append('.')

# Import our data loader
from scripts.chicago_data_loader import ChicagoTaxiDataLoader

def test_mock_data():
    """Test the mock data generation"""
    print("🧪 TESTING MOCK DATA GENERATION")
    print("=" * 50)
    
    loader = ChicagoTaxiDataLoader()
    
    # Test mock dataset creation
    print("Creating mock dataset...")
    df = loader.create_mock_dataset(size=100)
    
    print(f"✅ Mock dataset created: {len(df)} rides")
    print(f"📊 Columns: {list(df.columns)}")
    print(f"💰 Sample fares: {df['fare'].head().tolist()}")
    
    # Test analysis
    print("\n🔍 Testing analysis...")
    analysis = loader.analyze_data_structure(df)
    
    # Test feature detection
    print("\n🎯 Testing feature detection...")
    features = loader.detect_key_features(df)
    
    print(f"✅ Features detected: {features}")
    
    return df, analysis, features

if __name__ == "__main__":
    data, analysis_results, features = test_mock_data()
    print("\n🏆 TEST COMPLETE!")