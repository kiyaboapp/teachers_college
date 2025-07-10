import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from collections import defaultdict
import os
import argparse

class NectaResultsAnalyzer:
    """A class to analyze NECTA results and save analysis as CSV."""
    
    def __init__(self, centre_number=None, url=None):
        """
        Initialize with either a centre number or a full URL.
        
        Parameters:
        - centre_number: Centre number (e.g., '507') to construct URL
        - url: Full URL (e.g., 'https://matokeo.necta.go.tz/results/2025/dsee/results/507.htm')
        """
        if centre_number and url:
            raise ValueError("Provide either centre_number or url, not both.")
        if not centre_number and not url:
            raise ValueError("Provide either centre_number or url.")
        if centre_number:
            self.url = f"https://matokeo.necta.go.tz/results/2025/dsee/results/{centre_number}.htm"
            self.centre_number = centre_number
        else:
            self.url = url
            self.centre_number = None
        self.valid_grades = ['A', 'B', 'C', 'D', 'F', 'X', '*R']  # Valid subject grades
        self.star_codes = {
            '*S': 'Results suspended due to anomalies or irregularities',
            '*E': 'Results withheld, pending proof of payment',
            '*I': 'Incomplete results due to missing Continuous Assessment scores',
            '*W': 'Results withheld/nullified due to dishonesty or irregularities',
            '*T': 'Results transferred to previous year due to illness',
            'ABS': 'Candidate missed the exam',
            'FLD': 'Candidate failed the exam',
            'X': 'Candidate did not appear for the registered subject'
        }  # NECTA star codes
        self.df = None
        self.unique_subjects = None
        self.unique_grades = self.valid_grades
        self.grade_counts_by_sex = None
        self.total_grade_counts = None
        self.summary_df = None
        self.div_summary_df = None

    def fetch_data(self):
        """Fetch webpage and parse the last table into a DataFrame."""
        # For offline usage, uncomment the following and comment out the requests block:
        """
        try:
            with open(f"{self.centre_number}.htm", 'r', encoding='utf-8') as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            tables = soup.find_all('table')
            if not tables:
                print("No tables found.")
                return False
            target_table = tables[-1]
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return False
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching webpage: {e}")
            return False

        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        if not tables:
            print("No tables found on the page.")
            return False
        target_table = tables[-1]

        headers = []
        header_row = target_table.find_all('tr')[0]
        for th in header_row.find_all('td'):
            header_text = th.find('font').get_text(strip=True) if th.find('font') else ''
            if header_text:
                headers.append(header_text)

        data = []
        for row in target_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            row_data = [col.find('font').get_text(strip=True) if col.find('font') else '' for col in cols]
            row_data = [d for d in row_data if d]
            if row_data:
                data.append(row_data)

        self.df = pd.DataFrame(data, columns=headers)
        return True

    def parse_subjects(self, subject_string):
        """Parse DETAILED SUBJECTS into subject-grade pairs."""
        subjects = re.split(r'\s{2,}|\s*-\s*', subject_string.strip())
        subject_grade_pairs = []
        for i in range(0, len(subjects)-1, 2):
            subject = subjects[i].strip()
            grade = subjects[i+1].strip("'").strip()
            if grade:  # Ignore empty or null grades
                subject_grade_pairs.append({'subject': subject, 'grade': grade})
        return subject_grade_pairs

    def validate_grades(self):
        """Validate grades in DETAILED SUBJECTS and report invalid ones."""
        all_grades = set()
        self.df['Subject_Grade_Pairs'] = self.df['DETAILED SUBJECTS'].apply(self.parse_subjects)
        for pairs in self.df['Subject_Grade_Pairs']:
            for pair in pairs:
                all_grades.add(pair['grade'])

        invalid_grades = all_grades - set(self.valid_grades)
        if invalid_grades:
            print(f"Warning: Found invalid grades after cleaning: {invalid_grades}")
        else:
            print("All grades are valid: A, B, C, D, F, X, *R")
        return invalid_grades

    def summarize_star_codes(self):
        """Summarize NECTA star codes in AGGT and DIV columns."""
        star_code_summary = {}
        for column in ['AGGT', 'DIV']:
            if column in self.df.columns:
                star_values = self.df[column][self.df[column].str.contains(r'[*]', na=False, regex=True)].unique()
                if star_values.size > 0:
                    star_code_summary[column] = {
                        'values': list(star_values),
                        'counts': self.df[column].value_counts().to_dict()
                    }
        if star_code_summary:
            print("\nStar Codes Summary:")
            for column, info in star_code_summary.items():
                print(f"\nColumn: {column}")
                for value in info['values']:
                    description = self.star_codes.get(value, "Unknown code")
                    count = info['counts'].get(value, 0)
                    print(f"  {value}: {description} (Count: {count})")
        else:
            print("\nNo star codes found in AGGT or DIV columns.")
        return star_code_summary

    def analyze_results(self):
        """Analyze results and create subject-grade and DIV summary DataFrames."""
        # Subject-grade analysis
        all_subjects = set()
        for pairs in self.df['Subject_Grade_Pairs']:
            for pair in pairs:
                all_subjects.add(pair['subject'])
        self.unique_subjects = sorted(list(all_subjects))

        self.grade_counts_by_sex = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.total_grade_counts = defaultdict(lambda: defaultdict(int))
        for _, row in self.df.iterrows():
            sex = row['SEX']
            for pair in row['Subject_Grade_Pairs']:
                subject = pair['subject']
                grade = pair['grade']
                if grade in self.valid_grades:
                    self.grade_counts_by_sex[subject][sex][grade] += 1
                    self.total_grade_counts[subject][grade] += 1

        summary_data = []
        for subject in self.unique_subjects:
            row = {'Subject': subject}
            for grade in self.unique_grades:
                row[f'F_{grade}'] = self.grade_counts_by_sex[subject]['F'][grade]
                row[f'M_{grade}'] = self.grade_counts_by_sex[subject]['M'][grade]
                row[f'Total_{grade}'] = self.total_grade_counts[subject][grade]
            summary_data.append(row)

        columns = ['Subject']
        for grade in self.unique_grades:
            columns.extend([f'F_{grade}', f'M_{grade}', f'Total_{grade}'])
        self.summary_df = pd.DataFrame(summary_data, columns=columns)

        # DIV summary by sex
        div_counts = self.df.groupby(['DIV', 'SEX']).size().unstack(fill_value=0)
        div_counts['Total'] = div_counts.get('F', 0) + div_counts.get('M', 0)
        div_summary_data = []
        for div in sorted(div_counts.index, key=lambda x: (x not in ['I', 'II', 'III', 'IV', '0'], x)):
            row = {
                'DIV': div,
                'F': div_counts.at[div, 'F'] if 'F' in div_counts.columns else 0,
                'M': div_counts.at[div, 'M'] if 'M' in div_counts.columns else 0,
                'Total': div_counts.at[div, 'Total']
            }
            div_summary_data.append(row)
        self.div_summary_df = pd.DataFrame(div_summary_data, columns=['DIV', 'F', 'M', 'Total'])

    def print_analysis(self):
        """Print analysis results."""
        print("\nGrade Counts by Subject and Sex:")
        for subject in self.unique_subjects:
            print(f"\nSubject: {subject}")
            for sex in ['F', 'M']:
                if sex in self.grade_counts_by_sex[subject]:
                    print(f"  Sex: {sex}")
                    for grade in self.unique_grades:
                        count = self.grade_counts_by_sex[subject][sex][grade]
                        print(f"    Grade {grade}: {count}")

        print("\nTotal Grade Counts by Subject:")
        for subject in self.unique_subjects:
            print(f"\nSubject: {subject}")
            for grade in self.unique_grades:
                count = self.total_grade_counts[subject][grade]
                print(f"  Grade {grade}: {count}")

        print("\nAdditional Summary Statistics:")
        print(f"Total Students: {len(self.df)}")
        print(f"Total Female Students: {len(self.df[self.df['SEX'] == 'F'])}")
        print(f"Total Male Students: {len(self.df[self.df['SEX'] == 'M'])}")
        print(f"Unique Subjects Count: {len(self.unique_subjects)}")
        print(f"Valid Grades: {self.unique_grades}")
        print(f"Division Counts:\n{self.df['DIV'].value_counts().to_string()}")

        aggt_values = self.df['AGGT']
        numeric_aggt = pd.to_numeric(aggt_values, errors='coerce')
        if numeric_aggt.notna().any():
            mean_aggt = numeric_aggt.mean()
            print(f"Average AGGT (numeric values only): {mean_aggt:.2f}")
        else:
            print("Average AGGT: Not calculable (no numeric values)")
        non_numeric_aggt = aggt_values[aggt_values.str.contains(r'[^0-9.]', na=False, regex=True)].unique()
        if non_numeric_aggt.size > 0:
            print(f"Non-numeric AGGT values found: {list(non_numeric_aggt)}")

        self.summarize_star_codes()

        print("\nDIV Summary by Sex:")
        print(self.div_summary_df.to_string(index=False))

        print("\nSubject-Grade Summary DataFrame:")
        return self.summary_df

    def save_to_json(self, filename="necta_results.json"):
        """Save raw DataFrame to JSON."""
        try:
            json_data = self.df.to_dict(orient='records')
            with open(filename, 'w') as f:
                json.dump(json_data, f, indent=4)
            print(f"Raw data saved to {filename}")
        except Exception as e:
            print(f"Error saving JSON: {e}")

    def save_analysis_to_csv(self, directory=None, filename="necta_summary.csv"):
        """Save the subject-grade summary DataFrame to a CSV file."""
        if self.summary_df is None:
            print("No subject-grade summary DataFrame available. Run analyze_results first.")
            return
        try:
            target_dir = directory if directory else os.getcwd()
            if not os.path.exists(target_dir):
                raise FileNotFoundError(f"Directory does not exist: {target_dir}")
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, filename)
            self.summary_df.to_csv(file_path, index=False)
            print(f"Subject-Grade Summary DataFrame saved to {file_path}")
        except Exception as e:
            print(f"Error saving subject-grade CSV: {e}")

    def save_div_summary_to_csv(self, directory=None, filename="necta_div_summary.csv"):
        """Save the DIV summary DataFrame to a CSV file."""
        if self.div_summary_df is None:
            print("No DIV summary DataFrame available. Run analyze_results first.")
            return
        try:
            target_dir = directory if directory else os.getcwd()
            if not os.path.exists(target_dir):
                raise FileNotFoundError(f"Directory does not exist: {target_dir}")
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, filename)
            self.div_summary_df.to_csv(file_path, index=False)
            print(f"DIV Summary DataFrame saved to {file_path}")
        except Exception as e:
            print(f"Error saving DIV summary CSV: {e}")

    def run(self):
        """Run the full analysis pipeline."""
        if not self.fetch_data():
            return
        self.validate_grades()
        self.save_to_json()
        self.analyze_results()
        self.print_analysis()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NECTA Results Analyzer")
    parser.add_argument("--centre", help="Centre number (e.g., 507)")
    parser.add_argument("--url", help="Full NECTA results URL")
    parser.add_argument("--directory", help="Custom output directory")
    args = parser.parse_args()

    analyzer = NectaResultsAnalyzer(centre_number=args.centre, url=args.url)
    analyzer.run()
    if args.directory:
        analyzer.save_analysis_to_csv(directory=args.directory)
        analyzer.save_div_summary_to_csv(directory=args.directory)