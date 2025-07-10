import os
from analysis import NectaResultsAnalyzer

def demonstrate_online_centre():
    """Demonstrate using NectaResultsAnalyzer with a centre number."""
    print("=== Demonstration 1: Using Centre Number ===")
    analyzer = NectaResultsAnalyzer(centre_number="507")
    # url = "https://matokeo.necta.go.tz/results/2025/dsee/results/507.htm"
    # analyzer = NectaResultsAnalyzer(url=url)
    # UNCOMMENT the above lines to use a specific URL instead of centre number
    analyzer.run()
    # Save CSVs to current directory
    analyzer.save_analysis_to_csv()
    analyzer.save_div_summary_to_csv()
    print("\nOutputs saved to current directory:")
    print("- necta_results.json")
    print("- necta_summary.csv")
    print("- necta_div_summary.csv")

if __name__ == "__main__":
    demonstrate_online_centre()