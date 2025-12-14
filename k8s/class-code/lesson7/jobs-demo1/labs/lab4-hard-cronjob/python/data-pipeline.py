#!/usr/bin/env python3
"""
Lab 4: Hard CronJob - Multi-Step Data Pipeline
Implements a complex data pipeline with multiple stages
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Configuration from environment variables
DATA_SOURCES = int(os.getenv('DATA_SOURCES', '3'))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/tmp/reports')
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp/pipeline')
REPORT_FORMAT = os.getenv('REPORT_FORMAT', 'json')

class DataPipeline:
    def __init__(self, data_sources: int, output_dir: str, temp_dir: str):
        self.data_sources = data_sources
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.extracted_data = []
        self.transformed_data = []
        
    def setup_directories(self):
        """Create necessary directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directories created")
    
    def stage1_extract(self) -> bool:
        """Stage 1: Extract data from multiple sources"""
        print("\n" + "=" * 50)
        print("=== Stage 1: Data Extraction ===")
        print("=" * 50)
        
        self.extracted_data = []
        
        for i in range(1, self.data_sources + 1):
            print(f"Extracting from source {i}/{self.data_sources}...")
            time.sleep(0.5)  # Simulate extraction time
            
            # Simulate data extraction
            source_data = {
                'source_id': f'source_{i}',
                'records': [{'id': j, 'value': j * i} for j in range(1, 51)],
                'extracted_at': datetime.now().isoformat(),
                'record_count': 50
            }
            
            # Save to temporary file
            temp_file = self.temp_dir / f'source_{i}_raw.json'
            temp_file.write_text(json.dumps(source_data, indent=2))
            
            self.extracted_data.append(source_data)
            print(f"  ✓ Source {i}: {source_data['record_count']} records extracted")
        
        print(f"\n✓ Extraction completed: {len(self.extracted_data)} sources")
        return True
    
    def stage2_transform(self) -> bool:
        """Stage 2: Transform and validate data"""
        print("\n" + "=" * 50)
        print("=== Stage 2: Data Transformation ===")
        print("=" * 50)
        
        self.transformed_data = []
        
        for i, source_data in enumerate(self.extracted_data, 1):
            print(f"Transforming source {i}...")
            time.sleep(0.3)
            
            # Validate data
            if not source_data.get('records'):
                raise ValueError(f"Source {i} has no records")
            
            if len(source_data['records']) != source_data.get('record_count', 0):
                raise ValueError(f"Source {i} record count mismatch")
            
            # Transform data (add computed fields)
            transformed = {
                'source_id': source_data['source_id'],
                'records': source_data['records'],
                'transformed_at': datetime.now().isoformat(),
                'total_value': sum(r['value'] for r in source_data['records']),
                'avg_value': sum(r['value'] for r in source_data['records']) / len(source_data['records']),
                'record_count': len(source_data['records'])
            }
            
            # Save transformed data
            temp_file = self.temp_dir / f'source_{i}_transformed.json'
            temp_file.write_text(json.dumps(transformed, indent=2))
            
            self.transformed_data.append(transformed)
            print(f"  ✓ Source {i}: Validated and transformed (avg: {transformed['avg_value']:.2f})")
        
        print(f"\n✓ Transformation completed: {len(self.transformed_data)} sources validated")
        return True
    
    def stage3_aggregate(self) -> Dict:
        """Stage 3: Aggregate data from all sources"""
        print("\n" + "=" * 50)
        print("=== Stage 3: Data Aggregation ===")
        print("=" * 50)
        
        print("Aggregating data...")
        time.sleep(0.5)
        
        # Aggregate all records
        all_records = []
        total_value = 0
        total_records = 0
        
        for transformed in self.transformed_data:
            all_records.extend(transformed['records'])
            total_value += transformed['total_value']
            total_records += transformed['record_count']
        
        aggregated = {
            'aggregated_at': datetime.now().isoformat(),
            'total_sources': len(self.transformed_data),
            'total_records': total_records,
            'total_value': total_value,
            'avg_value': total_value / total_records if total_records > 0 else 0,
            'sources': [t['source_id'] for t in self.transformed_data]
        }
        
        # Save aggregated data
        agg_file = self.temp_dir / 'aggregated.json'
        agg_file.write_text(json.dumps(aggregated, indent=2))
        
        print(f"✓ Aggregation completed: {aggregated['total_records']} records")
        return aggregated
    
    def stage4_report(self, aggregated: Dict) -> bool:
        """Stage 4: Generate report"""
        print("\n" + "=" * 50)
        print("=== Stage 4: Report Generation ===")
        print("=" * 50)
        
        print("Generating report...")
        time.sleep(0.3)
        
        # Generate report
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        
        if REPORT_FORMAT.lower() == 'json':
            report_file = self.output_dir / f'report-{timestamp}.json'
            report_data = {
                'pipeline_run': {
                    'started_at': datetime.now().isoformat(),
                    'completed_at': datetime.now().isoformat(),
                    'stages_completed': 4,
                    'status': 'success'
                },
                'summary': aggregated,
                'sources': [
                    {
                        'source_id': t['source_id'],
                        'record_count': t['record_count'],
                        'total_value': t['total_value'],
                        'avg_value': t['avg_value']
                    }
                    for t in self.transformed_data
                ]
            }
            report_file.write_text(json.dumps(report_data, indent=2))
        else:
            report_file = self.output_dir / f'report-{timestamp}.txt'
            report_lines = [
                "=" * 50,
                "Data Pipeline Report",
                "=" * 50,
                f"Generated: {datetime.now().isoformat()}",
                "",
                "Summary:",
                f"  Total Sources: {aggregated['total_sources']}",
                f"  Total Records: {aggregated['total_records']}",
                f"  Total Value: {aggregated['total_value']}",
                f"  Average Value: {aggregated['avg_value']:.2f}",
                "",
                "Sources:",
            ]
            for t in self.transformed_data:
                report_lines.append(f"  - {t['source_id']}: {t['record_count']} records")
            report_file.write_text('\n'.join(report_lines))
        
        print(f"✓ Report generated: {report_file}")
        return True
    
    def stage5_cleanup(self) -> bool:
        """Stage 5: Cleanup temporary files"""
        print("\n" + "=" * 50)
        print("=== Stage 5: Cleanup ===")
        print("=" * 50)
        
        print("Cleaning temporary files...")
        
        deleted_count = 0
        for temp_file in self.temp_dir.glob('*.json'):
            try:
                temp_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  ⚠ Warning: Could not delete {temp_file.name}: {e}")
        
        print(f"✓ Cleanup completed: {deleted_count} files removed")
        return True
    
    def run(self) -> int:
        """Run the complete pipeline"""
        print("=" * 50)
        print("Data Pipeline")
        print(f"Started at: {datetime.now()}")
        print(f"Pod Name: {os.getenv('HOSTNAME', 'unknown')}")
        print("=" * 50)
        
        try:
            # Setup
            self.setup_directories()
            
            # Run stages
            if not self.stage1_extract():
                raise Exception("Stage 1 failed")
            
            if not self.stage2_transform():
                raise Exception("Stage 2 failed")
            
            aggregated = self.stage3_aggregate()
            
            if not self.stage4_report(aggregated):
                raise Exception("Stage 4 failed")
            
            if not self.stage5_cleanup():
                raise Exception("Stage 5 failed")
            
            print("\n" + "=" * 50)
            print("Pipeline completed successfully!")
            print(f"Completed at: {datetime.now()}")
            print("=" * 50)
            return 0
            
        except Exception as e:
            print("\n" + "=" * 50)
            print(f"Pipeline failed: {str(e)}")
            print(f"Failed at: {datetime.now()}")
            print("=" * 50)
            return 1

def main():
    pipeline = DataPipeline(DATA_SOURCES, OUTPUT_DIR, TEMP_DIR)
    return pipeline.run()

if __name__ == "__main__":
    sys.exit(main())

