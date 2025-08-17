#!/usr/bin/env python3
"""
Report generation script for the dice gambling game Robot Framework test suite.
"""

import os
import sys
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def parse_robot_output(output_xml_path: Path) -> Dict[str, Any]:
    """Parse Robot Framework output.xml file."""
    if not output_xml_path.exists():
        raise FileNotFoundError(f"Output XML not found: {output_xml_path}")
    
    tree = ET.parse(output_xml_path)
    root = tree.getroot()
    
    # Extract basic statistics
    stats = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "suites": [],
        "start_time": None,
        "end_time": None,
        "elapsed_time": None
    }
    
    # Get suite information
    suite = root.find("suite")
    if suite is not None:
        stats["start_time"] = suite.get("starttime")
        stats["end_time"] = suite.get("endtime")
        stats["elapsed_time"] = suite.get("elapsedtime")
        
        # Process test cases
        for test in suite.iter("test"):
            stats["total_tests"] += 1
            status = test.find("status")
            if status is not None and status.get("status") == "PASS":
                stats["passed_tests"] += 1
            else:
                stats["failed_tests"] += 1
        
        # Process suites
        for sub_suite in suite.iter("suite"):
            if sub_suite != suite:  # Skip root suite
                suite_info = {
                    "name": sub_suite.get("name"),
                    "source": sub_suite.get("source"),
                    "tests": len(list(sub_suite.iter("test")))
                }
                stats["suites"].append(suite_info)
    
    return stats


def generate_summary_report(stats: Dict[str, Any]) -> str:
    """Generate a text summary report."""
    report = []
    report.append("=" * 60)
    report.append("DICE GAMBLING GAME TEST EXECUTION SUMMARY")
    report.append("=" * 60)
    report.append("")
    
    # Basic statistics
    report.append(f"Total Tests:    {stats['total_tests']}")
    report.append(f"Passed Tests:   {stats['passed_tests']}")
    report.append(f"Failed Tests:   {stats['failed_tests']}")
    
    if stats['total_tests'] > 0:
        pass_rate = (stats['passed_tests'] / stats['total_tests']) * 100
        report.append(f"Pass Rate:      {pass_rate:.1f}%")
    
    report.append("")
    
    # Timing information
    if stats['start_time'] and stats['end_time']:
        report.append(f"Start Time:     {stats['start_time']}")
        report.append(f"End Time:       {stats['end_time']}")
    
    if stats['elapsed_time']:
        elapsed_ms = int(stats['elapsed_time'])
        elapsed_sec = elapsed_ms / 1000
        report.append(f"Elapsed Time:   {elapsed_sec:.2f} seconds")
    
    report.append("")
    
    # Suite information
    if stats['suites']:
        report.append("Test Suites:")
        for suite in stats['suites']:
            report.append(f"  - {suite['name']}: {suite['tests']} tests")
    
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)


def generate_json_report(stats: Dict[str, Any], output_path: Path):
    """Generate a JSON report."""
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "test_framework": "Robot Framework",
        "project": "Dice Gambling Game Test Suite",
        "statistics": stats,
        "summary": {
            "total_tests": stats["total_tests"],
            "passed_tests": stats["passed_tests"],
            "failed_tests": stats["failed_tests"],
            "pass_rate": (stats["passed_tests"] / stats["total_tests"] * 100) if stats["total_tests"] > 0 else 0
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)


def generate_html_summary(stats: Dict[str, Any], output_path: Path):
    """Generate a simple HTML summary report."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dice Gambling Game Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .passed {{ background-color: #d4edda; }}
            .failed {{ background-color: #f8d7da; }}
            .total {{ background-color: #e2e3e5; }}
            .suite-list {{ margin: 20px 0; }}
            .suite-item {{ padding: 10px; border-left: 3px solid #007bff; margin: 5px 0; background-color: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Dice Gambling Game Test Execution Report</h1>
            <p>Generated on: {generated_time}</p>
        </div>
        
        <div class="stats">
            <div class="stat-box total">
                <h3>Total Tests</h3>
                <h2>{total_tests}</h2>
            </div>
            <div class="stat-box passed">
                <h3>Passed</h3>
                <h2>{passed_tests}</h2>
            </div>
            <div class="stat-box failed">
                <h3>Failed</h3>
                <h2>{failed_tests}</h2>
            </div>
            <div class="stat-box">
                <h3>Pass Rate</h3>
                <h2>{pass_rate:.1f}%</h2>
            </div>
        </div>
        
        {timing_section}
        
        <div class="suite-list">
            <h3>Test Suites</h3>
            {suite_items}
        </div>
    </body>
    </html>
    """
    
    # Calculate pass rate
    pass_rate = (stats["passed_tests"] / stats["total_tests"] * 100) if stats["total_tests"] > 0 else 0
    
    # Generate timing section
    timing_section = ""
    if stats.get("elapsed_time"):
        elapsed_ms = int(stats["elapsed_time"])
        elapsed_sec = elapsed_ms / 1000
        timing_section = f"""
        <div class="timing">
            <h3>Execution Time</h3>
            <p>Duration: {elapsed_sec:.2f} seconds</p>
            <p>Start: {stats.get('start_time', 'N/A')}</p>
            <p>End: {stats.get('end_time', 'N/A')}</p>
        </div>
        """
    
    # Generate suite items
    suite_items = ""
    for suite in stats.get("suites", []):
        suite_items += f'<div class="suite-item">{suite["name"]}: {suite["tests"]} tests</div>'
    
    if not suite_items:
        suite_items = '<div class="suite-item">No suite information available</div>'
    
    # Fill template
    html_content = html_template.format(
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_tests=stats["total_tests"],
        passed_tests=stats["passed_tests"],
        failed_tests=stats["failed_tests"],
        pass_rate=pass_rate,
        timing_section=timing_section,
        suite_items=suite_items
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate reports for dice gambling game test results"
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Path to Robot Framework output.xml file"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for generated reports"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "html", "all"],
        default="all",
        help="Report format to generate (default: all)"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    project_root = get_project_root()
    
    if args.input:
        output_xml_path = Path(args.input)
    else:
        output_xml_path = project_root / "results" / "output.xml"
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "results" / "reports"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Parse Robot Framework output
        print(f"Parsing Robot Framework output: {output_xml_path}")
        stats = parse_robot_output(output_xml_path)
        
        # Generate reports based on format
        if args.format in ["text", "all"]:
            print("Generating text summary report...")
            summary = generate_summary_report(stats)
            print(summary)
            
            # Save to file
            text_report_path = output_dir / "summary.txt"
            with open(text_report_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Text report saved to: {text_report_path}")
        
        if args.format in ["json", "all"]:
            print("Generating JSON report...")
            json_report_path = output_dir / "report.json"
            generate_json_report(stats, json_report_path)
            print(f"JSON report saved to: {json_report_path}")
        
        if args.format in ["html", "all"]:
            print("Generating HTML summary...")
            html_report_path = output_dir / "summary.html"
            generate_html_summary(stats, html_report_path)
            print(f"HTML summary saved to: {html_report_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())