import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

def check_install_dependency(module_name, package_name=None):
    """
    Check if a module is installed.
    If not, prompt the user (using a tkinter messagebox) to install the package.
    module_name: the name used in __import__
    package_name: the pip package name (if different, e.g. for bs4 use "beautifulsoup4")
    """
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
    except ImportError:
        temp_root = tk.Tk()
        temp_root.withdraw()
        answer = messagebox.askyesno("Missing Dependency",
                                     f"Module '{module_name}' is not installed. "
                                     f"Would you like to install '{package_name}' now?")
        temp_root.destroy()
        if answer:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            except subprocess.CalledProcessError:
                print(f"Failed to install {package_name}. Exiting.")
                sys.exit(1)
        else:
            print(f"Module '{module_name}' is required. Exiting.")
            sys.exit(1)

# Check and install required dependencies BEFORE importing them
check_install_dependency("requests")
check_install_dependency("bs4", "beautifulsoup4")

# Now it's safe to import the modules
import requests
from bs4 import BeautifulSoup
import os
import time
import csv
from urllib.parse import urlparse, parse_qs

# ---------------------------------------------------------------------
# Utility function to prompt user to save HTML output
# ---------------------------------------------------------------------
def prompt_save_html(html_data):
    """
    Ask the user if they would like to save the raw HTML output.
    If yes, open a file-save dialog and save the HTML data to that file.
    """
    answer = messagebox.askyesno("Save HTML Output", 
                                 "Would you like to save the raw HTML output for debugging?")
    if answer:
        filename = filedialog.asksaveasfilename(title="Save HTML Output",
                                                defaultextension=".html",
                                                filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")])
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_data)
            messagebox.showinfo("Saved", f"HTML output saved to {filename}")

# ---------------------------------------------------------------------
# Parse user ID from URL or direct input
# ---------------------------------------------------------------------
def parse_user_id(scholar_input: str) -> str:
    """
    Extract the user ID ('user' parameter) from a full Google Scholar URL.
    If the input doesn't start with "http", assume it's already the user ID.
    Example URL:
        https://scholar.google.com/citations?user=dnbO4DgAAAAJ&hl=en
    Returns the user ID (e.g. 'dnbO4DgAAAAJ'), or None if not found.
    """
    scholar_input = scholar_input.strip()
    if not scholar_input.startswith("http"):
        return scholar_input
    parsed_url = urlparse(scholar_input)
    query_params = parse_qs(parsed_url.query)
    user_ids = query_params.get("user", [])
    if user_ids:
        return user_ids[0]
    return None

# ---------------------------------------------------------------------
# Fetch publications from a user profile
# ---------------------------------------------------------------------
def fetch_all_publications(user_id, retries=5, delay=60):
    base_url = "https://scholar.google.com/citations"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    publications = []
    start = 0

    while True:
        params = {
            "user": user_id,
            "hl": "en",
            "cstart": start,
            "pagesize": 100
        }
        for attempt in range(retries):
            response = requests.get(base_url, headers=headers, params=params)
            print(f"HTTP Status Code (Publications): {response.status_code}")
            
            if response.status_code == 200:
                # Debug: print and optionally save the HTML output
                print(response.text)
                prompt_save_html(response.text)
                
                soup = BeautifulSoup(response.content, "html.parser")
                new_publications = soup.find_all("tr", {"class": "gsc_a_tr"})
                
                for pub in new_publications:
                    title = pub.find("a", {"class": "gsc_a_at"}).text
                    authors = pub.find("div", {"class": "gs_gray"}).text
                    gs_gray_divs = pub.find_all("div", {"class": "gs_gray"})
                    journal = gs_gray_divs[1].text if len(gs_gray_divs) > 1 else ""
                    citations = pub.find("a", {"class": "gsc_a_ac"}).text
                    year = pub.find("span", {"class": "gsc_a_h"}).text
                    publications.append({
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "citations": citations,
                        "year": year
                    })

                if len(new_publications) < 100:
                    return publications

                start += 100
                break
            elif response.status_code == 429:
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to fetch publications data.")
                return None

    print("Exceeded maximum retries while fetching publications.")
    return None

# ---------------------------------------------------------------------
# Fetch the complete Scholar profile for a user
# ---------------------------------------------------------------------
def fetch_scholar_profile(user_id, retries=5, delay=60):
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    for attempt in range(retries):
        response = requests.get(url, headers=headers)
        print(f"HTTP Status Code (Profile): {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            profile = {}

            name_div = soup.find("div", {"id": "gsc_prf_in"})
            if name_div:
                profile["name"] = name_div.text
            else:
                print("Failed to find name div")

            affiliation_div = soup.find("div", {"class": "gsc_prf_il"})
            if affiliation_div:
                profile["affiliation"] = affiliation_div.text
            else:
                print("Failed to find affiliation div")

            interests = soup.find_all("a", {"class": "gsc_prf_inta gs_ibl"})
            if interests:
                profile["interests"] = [interest.text for interest in interests]
            else:
                print("Failed to find interests")

            metrics = soup.find_all("td", {"class": "gsc_rsb_std"})
            if metrics:
                profile["citations"] = {
                    "all": metrics[0].text,
                    "recent": metrics[1].text
                }
                profile["h_index"] = {
                    "all": metrics[2].text,
                    "recent": metrics[3].text
                }
                profile["i10_index"] = {
                    "all": metrics[4].text,
                    "recent": metrics[5].text
                }
            else:
                print("Failed to find metrics")

            publications = fetch_all_publications(user_id)
            if publications is not None:
                profile["publications_count"] = len(publications)
                profile["publications"] = publications
            else:
                profile["publications_count"] = "Failed to count publications"
                profile["publications"] = []

            return profile
        elif response.status_code == 429:
            print(f"Rate limited. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            print("Failed to fetch profile data.")
            return None

    print("Exceeded maximum retries while fetching profile.")
    return None

# ---------------------------------------------------------------------
# Write profile data to CSV
# ---------------------------------------------------------------------
def write_to_csv(profile_data, filename="scholar_profile.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", profile_data.get("name", "")])
        writer.writerow(["Affiliation", profile_data.get("affiliation", "")])
        interests = profile_data.get("interests", [])
        writer.writerow(["Interests"] + interests)
        citations = profile_data.get("citations", {})
        writer.writerow(["Citations (All)", citations.get("all", "")])
        writer.writerow(["Citations (Recent)", citations.get("recent", "")])
        h_index = profile_data.get("h_index", {})
        writer.writerow(["h-index (All)", h_index.get("all", "")])
        writer.writerow(["h-index (Recent)", h_index.get("recent", "")])
        i10_index = profile_data.get("i10_index", {})
        writer.writerow(["i10-index (All)", i10_index.get("all", "")])
        writer.writerow(["i10-index (Recent)", i10_index.get("recent", "")])
        writer.writerow([])
        writer.writerow(["Title", "Authors", "Journal", "Citations", "Year"])
        for pub in profile_data.get("publications", []):
            writer.writerow([
                pub.get("title", ""), 
                pub.get("authors", ""), 
                pub.get("journal", ""), 
                pub.get("citations", ""), 
                pub.get("year", "")
            ])

# ---------------------------------------------------------------------
# Tkinter GUI Functions
# ---------------------------------------------------------------------
def ensure_output_folder():
    folder_name = "google-scholar-search-results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def on_submit():
    user_input = entry_scholar_urls.get().strip()
    if not user_input:
        messagebox.showwarning("Input Error", "Please enter at least one Google Scholar profile URL or user ID.")
        return

    output_text.delete("1.0", tk.END)
    results_folder = ensure_output_folder()
    url_list = [url.strip() for url in user_input.split(",") if url.strip()]
    
    for url in url_list:
        user_id = parse_user_id(url)
        if not user_id:
            output_text.insert(tk.END, f"Could not parse user ID from input: {url}\n\n")
            continue
        
        profile_data = fetch_scholar_profile(user_id)
        if profile_data:
            output_text.insert(tk.END, f"--- Results for User ID: {user_id} ---\n")
            output_text.insert(tk.END, f"Name: {profile_data.get('name', 'N/A')}\n")
            output_text.insert(tk.END, f"Affiliation: {profile_data.get('affiliation', 'N/A')}\n")
            output_text.insert(tk.END, f"Interests: {profile_data.get('interests', 'N/A')}\n")
            output_text.insert(tk.END, f"Citations (All): {profile_data.get('citations', {}).get('all', 'N/A')}\n")
            output_text.insert(tk.END, f"Citations (Recent): {profile_data.get('citations', {}).get('recent', 'N/A')}\n")
            output_text.insert(tk.END, f"h-index (All): {profile_data.get('h_index', {}).get('all', 'N/A')}\n")
            output_text.insert(tk.END, f"h-index (Recent): {profile_data.get('h_index', {}).get('recent', 'N/A')}\n")
            output_text.insert(tk.END, f"i10-index (All): {profile_data.get('i10_index', {}).get('all', 'N/A')}\n")
            output_text.insert(tk.END, f"i10-index (Recent): {profile_data.get('i10_index', {}).get('recent', 'N/A')}\n")
            output_text.insert(tk.END, f"Publications Count: {profile_data.get('publications_count', 'N/A')}\n\n")

            csv_filename = f"scholar_profile_{user_id}.csv"
            csv_path = os.path.join(results_folder, csv_filename)
            write_to_csv(profile_data, filename=csv_path)
            
            output_text.insert(tk.END, f"Saved data to {csv_path}\n\n")
        else:
            output_text.insert(tk.END, f"Failed to fetch profile data for user ID: {user_id}\n\n")

    messagebox.showinfo("Done", "All profile(s) processed.")

# ---------------------------------------------------------------------
# Build the GUI
# ---------------------------------------------------------------------
root = tk.Tk()
root.title("Google Scholar Profile Scraper")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

lbl_scholar_urls = tk.Label(frame, text="Enter a Google Scholar profile URL (or user ID; multiple separated by commas):")
lbl_scholar_urls.grid(row=0, column=0, sticky=tk.W)

entry_scholar_urls = tk.Entry(frame, width=80)
entry_scholar_urls.grid(row=1, column=0, padx=5, pady=5)

btn_submit = tk.Button(frame, text="Fetch Profile(s)", command=on_submit)
btn_submit.grid(row=2, column=0, pady=10)

output_text = tk.Text(frame, width=80, height=20)
output_text.grid(row=3, column=0, padx=5, pady=10)

root.mainloop()
