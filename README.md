# NECTA Results Analyzer 📊

A sleek Python tool to scrape and analyze NECTA (National Examinations Council of Tanzania) results, generating CSV summaries for subject grades and divisions by sex. Perfect for educators and administrators to dive into student performance data with ease. 🚀

## Features ✨

- **Scrape NECTA Data**: Pulls results using a centre number (e.g., `507`) or a full URL.
- **Subject-Grade Summary**: Outputs `necta_summary.csv` with grade counts (`A`, `B`, `C`, `D`, `F`, `X`, `*R`) by subject and sex (`F`, `M`, `Total`).
- **Division Summary**: Creates `necta_div_summary.csv` with division counts (e.g., `I`, `II`, `*E`) by sex.
- **Star Code Support**: Handles NECTA star codes (e.g., `*E`: withheld for payment, `*I`: incomplete results) with clear descriptions.
- **Flexible Outputs**: Saves raw data to `necta_results.json` and CSVs to the current directory or a custom path.
- **Robust Analysis**: Validates grades, sorts subjects alphabetically, and includes all grades for all subjects.

## Prerequisites 🛠️

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/).
- **Git** (optional for cloning): [Install Git](https://git-scm.com/downloads).
- Internet connection for fetching NECTA results (or use offline HTML files).

## Getting Started: Download and Setup 📥

### Option 1: Download as ZIP
1. Visit [https://github.com/kiyaboapp/teachers_college](https://github.com/kiyaboapp/teachers_college).
2. Click the green **Code** button, then select **Download ZIP**.
3. Extract the ZIP file to a folder (e.g., `teachers_college`).
4. Open a terminal and navigate to the folder:
   ```bash
   cd path/to/teachers_college
   ```

### Option 2: Clone with Git
Clone the repository using Git:
```bash
git clone https://github.com/kiyaboapp/teachers_college.git
cd teachers_college
```

### Setup Virtual Environment
Create and activate a virtual environment to keep dependencies isolated:

1. **Create**:
   ```bash
   python -m venv venv
   ```

2. **Activate**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   You’ll see `(venv)` in your terminal prompt.

3. **Install Dependencies**:
   ```bash
   pip install requests beautifulsoup4 pandas
   ```

### Run the Script
Analyze NECTA results with a centre number (e.g., `507`):
```bash
python analysis.py --centre 507
```

Or with a full URL:
```bash
python analysis.py --url https://matokeo.necta.go.tz/results/2025/dsee/results/507.htm
```

To save CSVs to a custom directory (e.g., `C:\Users\droge\OneDrive\Documents`):
```bash
python analysis.py --centre 507 --directory "C:\Users\droge\OneDrive\Documents"
```

### Offline Usage
To analyze a local HTML file (e.g., `507.htm`):
1. Place `507.htm` in the `teachers_college` directory.
2. Modify `fetch_data` in `analysis.py` (see comments in the code).
3. Run with:
   ```bash
   python analysis.py --centre 507
   ```

## Outputs 📈

- **JSON File**: `necta_results.json` (raw scraped data).
- **CSV Files**:
  - `necta_summary.csv`: Subject-grade counts (e.g., `F_A`, `M_A`, `Total_A`).
  - `necta_div_summary.csv`: Division counts by sex (e.g., `DIV`, `F`, `M`, `Total`).
- **Console Output**:
  - Grade validation (e.g., valid grades: `A, B, C, D, F, X, *R`).
  - Subject-grade counts by sex and total.
  - Summary stats (total students, female/male counts, unique subjects).
  - Average `AGGT` (numeric values only) and non-numeric values (e.g., `*E`).
  - Star codes summary (e.g., `*E: Results withheld, pending proof of payment`).
  - Division summary table.

### Example `necta_div_summary.csv`
```csv
DIV,F,M,Total
I,5,3,8
II,2,4,6
0,1,1,2
*E,1,2,3
*I,0,1,1
```

## Project Structure 📁

```
teachers_college/
├── analysis.py           # Main script with NectaResultsAnalyzer
├── venv/                # Virtual environment (after setup)
├── necta_results.json   # Raw data output
├── necta_summary.csv    # Subject-grade summary output
├── necta_div_summary.csv # Division summary output
└── README.md            # This file
```

## Command-Line Arguments 🎛️

Use these flags with `analysis.py`:
- `--centre`: Centre number (e.g., `507`).
- `--url`: Full NECTA URL (e.g., `https://matokeo.necta.go.tz/results/2025/dsee/results/507.htm`).
- `--directory`: Custom output directory (e.g., `C:\Users\droge\OneDrive\Documents`).

Example:
```bash
python analysis.py --centre 507 --directory "C:\Users\droge\OneDrive\Documents"
```

Other Way: Makesure you write the Args in it (test.py)
```
python test.py
```
## Contributing 🤝

Want to improve this tool? Here’s how:
1. Fork the repo.
2. Create a branch: `git checkout -b feature/YourFeature`.
3. Commit changes: `git commit -m "Add YourFeature"`.
4. Push: `git push origin feature/YourFeature`.
5. Open a pull request.

Follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

## License 📜

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments 🙌

- Built by [kiyaboapp](https://github.com/kiyaboapp) with ❤️.
- Powered by [requests](https://requests.readthedocs.io/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [pandas](https://pandas.pydata.org/).
- Inspired by educators’ need for streamlined NECTA results analysis.

---

🌟 **Star this repo** if it helps you! Report issues or suggest features at [GitHub Issues](https://github.com/kiyaboapp/teachers_college/issues). Happy analyzing! 🎉