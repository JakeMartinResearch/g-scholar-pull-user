# Google Scholar Profile Scraper

This tool provides a graphical interface to fetch data from Google Scholar profiles. It retrieves profile details, publication information, citation metrics, and saves the results in CSV format. Additionally, you have the option to save the raw HTML output for debugging purposes.

## Features

- **Flexible Input:**  
  Enter either a full Google Scholar profile URL (e.g.,  
  `https://scholar.google.com/citations?user=z7YruZ8AAAAJ&hl=en`) or a direct user ID (e.g., `z7YruZ8AAAAJ`). Multiple inputs can be separated by commas.

- **Data Retrieval:**  
  The script fetches:
  - The user’s name and affiliation.
  - Research interests.
  - Citation counts, h-index, and i10-index metrics.
  - A list of publications with title, authors, journal, citations, and publication year.

- **CSV Export:**  
  Results for each profile are saved as a CSV file in a dedicated folder (`google-scholar-search-results`).

- **HTML Debugging Option:**  
  When fetching publication data, you are prompted to save the raw HTML output. This can help with debugging if the page content is not as expected.

## Requirements

- **Python:**  
  Python 3.8 or later is recommended.  
  *Note: If using an older Python version, you may encounter issues with certain type hints (e.g., `Literal` in the typing module).*

- **Dependencies:**  
  The script requires the following packages:
  - `requests`
  - `beautifulsoup4`
  
  The script includes a prompt to help install any missing dependencies automatically.

## Installation

**Clone the Repository:**

   ```bash
   git clone https://github.com/JakeMartinResearch/g-scholar-pull-user.git
   cd g-scholar-pull-user
   ```
  
  ## Useage

  - **Run the Script:**
     Launch the application by running:

```bash
python google-scholar-pull-gui.py
```
- **Enter Profile Information:**
In the GUI, enter a full Google Scholar profile URL or user ID. If you have multiple profiles to fetch, separate them with commas.

- **Fetch Data:**
Click the "Fetch Profile(s)" button. The script will:
  - Retrieve profile data from Google Scholar.
  - Optionally prompt you to save the raw HTML output for debugging.
  - Display the fetched information in the GUI.
  - Save the results in CSV files under the (`google-scholar-search-results`) folder.

- **Review Results:**
The CSV files contain all the retrieved profile information and publication details.

## License

This project is licensed under the MIT License.

MIT License

Copyright (c) [2025] [Jake M Martin]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Disclaimer

This project is an independent, open-source initiative and is not created, endorsed, or maintained by Google. Google is a registered trademark of Google LLC in the United States and other countries. Any references to Google in this project are solely for informational purposes and do not imply any affiliation with or endorsement by Google.

