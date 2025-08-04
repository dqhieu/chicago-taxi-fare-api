#!/usr/bin/env python3
"""
Chicago Taxi Challenge: Data Acquisition Script
Chapter 1: The Chicago Connection

Mission: Efficiently load Chicago taxi data for analysis
Agent: Data acquisition specialist for market intelligence
"""

import pandas as pd
import numpy as np
import requests
import json
import os
from pathlib import Path
import time
from typing import Optional, Dict, Any

class ChicagoTaxiDataLoader:
    """
    Sophisticated data loader for Chicago taxi datasets
    Handles large datasets with smart sampling and efficient processing
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.samples_dir = self.data_dir / "samples"
        
        # Create directories
        for dir_path in [self.raw_dir, self.processed_dir, self.samples_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Data source URLs
        self.data_sources = {
            "2021": {
                "api_endpoint": "https://data.cityofchicago.org/resource/9kgb-ykyt.json",
                "csv_download": "https://data.cityofchicago.org/api/views/9kgb-ykyt/rows.csv?accessType=DOWNLOAD",
                "description": "Chicago Taxi Trips 2021 (~12M rides)"
            },
            "2024": {
                "api_endpoint": "https://data.cityofchicago.org/resource/ajtu-isnz.json", 
                "csv_download": "https://data.cityofchicago.org/api/views/ajtu-isnz/rows.csv?accessType=DOWNLOAD",
                "description": "Chicago Taxi Trips 2024 (~8M rides)"
            }
        }
    
    def get_data_sample(self, year: str = "2021", sample_size: int = 10000) -> pd.DataFrame:
        """
        Get a sample of the data for initial exploration
        Smart approach: Sample first, understand second
        """
        print(f"🎯 MISSION 1.2: Data Reconnaissance - {year} Sample")
        print("=" * 60)
        print(f"Agent's Log: Acquiring {sample_size:,} ride samples for intelligence gathering...")
        
        try:
            url = f"{self.data_sources[year]['api_endpoint']}?$limit={sample_size}"
            print(f"📡 Connecting to Chicago Open Data API...")
            print(f"   Source: {self.data_sources[year]['description']}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Data acquired successfully!")
            
            # Parse JSON response
            data = response.json()
            df = pd.DataFrame(data)
            
            print(f"📊 Sample acquired: {len(df):,} rides")
            print(f"   Columns: {len(df.columns)} features detected")
            print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            # Save sample for future use
            sample_file = self.samples_dir / f"chicago_taxi_{year}_sample_{sample_size}.csv"
            df.to_csv(sample_file, index=False)
            print(f"💾 Sample saved: {sample_file}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Data acquisition failed: {e}")
            print("🔧 Troubleshooting: Check internet connection or try smaller sample")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return pd.DataFrame()
    
    def analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform initial data structure analysis
        Mission critical: Understanding the battlefield
        """
        print(f"\n🔍 MISSION 1.3: Data Structure Analysis")
        print("=" * 60)
        print("Agent's Log: Analyzing data structure for tactical advantage...")
        
        analysis = {}
        
        # Basic structure
        analysis['shape'] = df.shape
        analysis['memory_mb'] = df.memory_usage(deep=True).sum() / 1024**2
        analysis['columns'] = df.columns.tolist()
        
        print(f"📊 Dataset Overview:")
        print(f"   Shape: {df.shape[0]:,} rides × {df.shape[1]} features")
        print(f"   Memory: {analysis['memory_mb']:.2f} MB")
        
        # Column analysis
        print(f"\n📋 Column Intelligence Report:")
        column_analysis = {}
        
        for col in df.columns:
            try:
                # Handle columns that might contain complex data types
                unique_count = df[col].nunique()
                sample_values = df[col].dropna().head(3).tolist() if not df[col].empty else []
            except (TypeError, ValueError):
                # Handle columns with unhashable types (like dicts)
                unique_count = "N/A"
                sample_values = ["<complex_data>"]
                print(f"   ⚠️  {col}: Contains complex data (dict/list) - will need special handling")
            
            col_info = {
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'unique_values': unique_count,
                'sample_values': sample_values
            }
            column_analysis[col] = col_info
            
            print(f"   {col:25} | {col_info['dtype']:10} | "
                  f"Nulls: {col_info['null_count']:4} ({col_info['null_percentage']:5.1f}%) | "
                  f"Unique: {str(col_info['unique_values']):>6}")
        
        analysis['columns_detail'] = column_analysis
        
        # Time range analysis (if timestamp columns exist)
        timestamp_cols = [col for col in df.columns if 'timestamp' in col.lower() or 'time' in col.lower()]
        if timestamp_cols:
            print(f"\n⏰ Time Range Analysis:")
            for col in timestamp_cols:
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_range = f"{df[col].min()} to {df[col].max()}"
                    print(f"   {col}: {date_range}")
                    analysis[f'{col}_range'] = date_range
                except:
                    print(f"   {col}: Unable to parse as datetime")
        
        return analysis
    
    def detect_key_features(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect key features for fare prediction modeling
        """
        print(f"\n🎯 Key Feature Detection:")
        
        feature_mapping = {}
        
        # Common patterns for key features
        patterns = {
            'fare': ['fare', 'cost', 'price', 'amount'],
            'tips': ['tip', 'gratuity'],
            'distance': ['mile', 'distance', 'km'],
            'duration': ['second', 'minute', 'duration', 'time'],
            'pickup_time': ['pickup', 'start'],
            'dropoff_time': ['dropoff', 'end'],
            'pickup_location': ['pickup', 'origin'],
            'dropoff_location': ['dropoff', 'destination']
        }
        
        for feature_type, keywords in patterns.items():
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in keywords):
                    feature_mapping[feature_type] = col
                    print(f"   {feature_type:15}: {col}")
                    break
        
        return feature_mapping
    
    def quick_insights(self, df: pd.DataFrame, feature_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate quick business insights for mission briefing
        """
        print(f"\n💡 QUICK BUSINESS INTELLIGENCE:")
        print("=" * 60)
        
        insights = {}
        
        # Fare analysis
        if 'fare' in feature_mapping:
            fare_col = feature_mapping['fare']
            try:
                df[fare_col] = pd.to_numeric(df[fare_col], errors='coerce')
                fare_stats = {
                    'mean': df[fare_col].mean(),
                    'median': df[fare_col].median(),
                    'std': df[fare_col].std(),
                    'min': df[fare_col].min(),
                    'max': df[fare_col].max()
                }
                insights['fare_stats'] = fare_stats
                
                print(f"💰 Fare Intelligence:")
                print(f"   Average fare: ${fare_stats['mean']:.2f}")
                print(f"   Median fare: ${fare_stats['median']:.2f}")
                print(f"   Fare range: ${fare_stats['min']:.2f} - ${fare_stats['max']:.2f}")
                
                # Business implications
                if fare_stats['mean'] > 15:
                    print(f"   📈 Premium market detected (>${fare_stats['mean']:.0f} avg)")
                elif fare_stats['mean'] < 8:
                    print(f"   📉 Budget market identified (<${fare_stats['mean']:.0f} avg)")
                else:
                    print(f"   ⚖️  Balanced market segment (${fare_stats['mean']:.0f} avg)")
                    
            except Exception as e:
                print(f"   ❌ Fare analysis failed: {e}")
        
        # Tips analysis
        if 'tips' in feature_mapping:
            tips_col = feature_mapping['tips']
            try:
                df[tips_col] = pd.to_numeric(df[tips_col], errors='coerce')
                df['tip_percentage'] = (df[tips_col] / df[fare_col]) * 100
                
                avg_tip_pct = df['tip_percentage'].mean()
                insights['tip_percentage'] = avg_tip_pct
                
                print(f"💡 Tipping Intelligence:")
                print(f"   Average tip percentage: {avg_tip_pct:.1f}%")
                
                if avg_tip_pct > 20:
                    print(f"   🌟 High-tipping market (excellent service culture)")
                elif avg_tip_pct < 10:
                    print(f"   🔍 Low-tipping market (investigate service standards)")
                else:
                    print(f"   ✅ Standard tipping behavior")
                    
            except Exception as e:
                print(f"   ❌ Tips analysis failed: {e}")
        
        # Distance analysis
        if 'distance' in feature_mapping:
            distance_col = feature_mapping['distance']
            try:
                df[distance_col] = pd.to_numeric(df[distance_col], errors='coerce')
                avg_distance = df[distance_col].mean()
                insights['avg_distance'] = avg_distance
                
                print(f"🛣️  Distance Intelligence:")
                print(f"   Average trip distance: {avg_distance:.2f} miles")
                
                if avg_distance > 8:
                    print(f"   🌆 Long-distance market (airport/suburban focus)")
                elif avg_distance < 3:
                    print(f"   🏢 Short-haul market (downtown/urban focus)")
                else:
                    print(f"   🎯 Mixed distance market")
                    
            except Exception as e:
                print(f"   ❌ Distance analysis failed: {e}")
        
        print(f"\n✅ Initial reconnaissance complete!")
        return insights
    
    def save_analysis_report(self, analysis: Dict[str, Any], insights: Dict[str, Any]) -> None:
        """
        Save analysis report for mission documentation
        """
        report_file = self.processed_dir / "chicago_data_analysis_report.json"
        
        full_report = {
            'mission': 'Chicago Taxi Market Intelligence',
            'timestamp': pd.Timestamp.now().isoformat(),
            'data_structure': analysis,
            'business_insights': insights,
            'agent_notes': [
                'Initial data reconnaissance completed successfully',
                'Key features identified for fare prediction modeling',
                'Business intelligence gathered for market entry strategy',
                'Ready to proceed to Chapter 2: Market Analysis'
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(full_report, f, indent=2, default=str)
        
        print(f"📋 Mission report saved: {report_file}")
    
    def create_mock_dataset(self, size: int = 1000) -> pd.DataFrame:
        """
        Create a mock Chicago taxi dataset for demonstration when API is unavailable
        """
        print(f"🛠️  FALLBACK MODE: Creating mock dataset with {size:,} samples")
        print("📝 Note: This is synthetic data for demonstration purposes")
        
        import random
        from datetime import datetime, timedelta
        
        # Set random seed for reproducibility
        random.seed(42)
        np.random.seed(42)
        
        # Create synthetic taxi data based on Chicago patterns
        data = []
        base_date = datetime(2021, 6, 1)
        
        for i in range(size):
            # Random timestamp in June 2021
            random_hours = random.randint(0, 24*30)
            trip_start = base_date + timedelta(hours=random_hours)
            
            # Trip duration between 5 minutes to 2 hours
            duration_minutes = np.random.exponential(20) + 5
            duration_minutes = min(duration_minutes, 120)  # Cap at 2 hours
            trip_end = trip_start + timedelta(minutes=duration_minutes)
            
            # Distance based on duration (roughly)
            trip_miles = max(0.5, np.random.normal(duration_minutes/10, 2))
            
            # Fare calculation (Chicago-like pricing)
            base_fare = 3.25
            distance_fare = trip_miles * 2.25
            time_fare = duration_minutes * 0.35
            fare = base_fare + distance_fare + time_fare
            fare = round(max(fare, 5.0), 2)  # Minimum $5
            
            # Tips (0-25% of fare, weighted toward 15-20%)
            tip_percentage = max(0, np.random.normal(0.18, 0.08))
            tips = round(fare * tip_percentage, 2)
            
            # Extras and tolls (occasional)
            extras = round(random.choice([0, 0, 0, 1, 2, 5]), 2)
            tolls = round(random.choice([0, 0, 0, 0, 0, 6.50]), 2)
            
            trip_total = fare + tips + tolls + extras
            
            # Community areas (Chicago has 77)
            pickup_area = random.randint(1, 77)
            dropoff_area = random.randint(1, 77)
            
            # Payment types
            payment_type = random.choice(['Credit Card', 'Cash', 'Mobile', 'Credit Card', 'Credit Card'])
            
            # Mock company
            company = random.choice([
                'Taxi Affiliation Services', 'City Service', 'Blue Ribbon Taxi',
                'Chicago Taxi', 'Yellow Cab', 'Flash Cab', 'Sun Taxi'
            ])
            
            # Create record
            record = {
                'trip_id': f'trip_{i+1:06d}',
                'taxi_id': f'taxi_{random.randint(1000, 9999)}',
                'trip_start_timestamp': trip_start.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'trip_end_timestamp': trip_end.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'trip_seconds': int(duration_minutes * 60),
                'trip_miles': round(trip_miles, 1),
                'pickup_community_area': pickup_area,
                'dropoff_community_area': dropoff_area,
                'fare': fare,
                'tips': tips,
                'tolls': tolls,
                'extras': extras,
                'trip_total': round(trip_total, 2),
                'payment_type': payment_type,
                'company': company,
                'pickup_centroid_latitude': 41.85 + random.uniform(-0.3, 0.3),
                'pickup_centroid_longitude': -87.65 + random.uniform(-0.4, 0.4),
                'dropoff_centroid_latitude': 41.85 + random.uniform(-0.3, 0.3),
                'dropoff_centroid_longitude': -87.65 + random.uniform(-0.4, 0.4)
            }
            data.append(record)
        
        df = pd.DataFrame(data)
        
        # Save mock dataset
        mock_file = self.samples_dir / f"chicago_taxi_mock_{size}.csv"
        df.to_csv(mock_file, index=False)
        print(f"💾 Mock dataset saved: {mock_file}")
        
        return df

def main():
    """
    Execute Chapter 1: Data Acquisition and Initial Reconnaissance
    """
    print("🚕 CHICAGO TAXI CHALLENGE: CHAPTER 1")
    print("🎯 MISSION: Data Acquisition & Initial Reconnaissance")
    print("🏢 OBJECTIVE: Gather intelligence for Chicago market entry")
    print("=" * 70)
    
    # Initialize data loader
    loader = ChicagoTaxiDataLoader()
    
    # Mission 1.2: Acquire data sample with fallback strategy
    print("\n🚀 Initiating data acquisition protocol...")
    
    # Try different sample sizes if the first fails
    sample_sizes = [10000, 5000, 1000, 500]
    df = None
    
    for size in sample_sizes:
        print(f"\n🎯 Attempting acquisition: {size:,} ride sample...")
        df = loader.get_data_sample(year="2021", sample_size=size)
        if not df.empty:
            print(f"✅ Success with {size:,} rides!")
            break
        else:
            print(f"❌ Failed with {size:,} rides, trying smaller sample...")
    
    if df is None or df.empty:
        print("\n🔧 FALLBACK: Creating mock dataset for demonstration...")
        df = loader.create_mock_dataset()
    
    # Mission 1.3: Analyze data structure
    analysis = loader.analyze_data_structure(df)
    
    # Detect key features
    feature_mapping = loader.detect_key_features(df)
    
    # Mission 1.4: Generate quick insights
    insights = loader.quick_insights(df, feature_mapping)
    
    # Mission 1.5: Document findings
    loader.save_analysis_report(analysis, insights)
    
    print(f"\n🏆 CHAPTER 1 MISSION STATUS: COMPLETE")
    print("=" * 70)
    print("📊 Intelligence Summary:")
    print(f"   ✅ Data acquired: {len(df):,} rides analyzed")
    print(f"   ✅ Features identified: {len(feature_mapping)} key features")
    print(f"   ✅ Business insights: Market intelligence gathered")
    print(f"   ✅ Documentation: Mission report generated")
    print(f"\n🎯 Next Mission: Chapter 2 - Market Intelligence & Business Analysis")
    print("   Ready to proceed with comprehensive market analysis!")
    
    return df, analysis, insights, feature_mapping

if __name__ == "__main__":
    # Execute Chapter 1 mission
    data, analysis_results, business_insights, features = main()