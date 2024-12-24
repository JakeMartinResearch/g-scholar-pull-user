import os
import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urlparse, parse_qs

# ---------------------------------------------------------------------
# Scraping functions
# ---------------------------------------------------------------------
def parse_user_id(scholar_url: str) -> str:
    """
    Extract the user ID ('user' parameter) from a full Google Scholar URL.
    Example:
        https://scholar.google.com/citations?user=dnbO4DgAAAAJ&hl=en
    Returns the user ID (e.g. 'dnbO4DgAAAAJ'), or None if not found.
    """
    parsed_url = urlparse(scholar_url.strip())
    query_params = parse_qs(parsed_url.query)
    user_ids = query_params.get("user", [])
    if user_ids:
        return user_ids[0]  # Return the first 'user' value
    return None

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
                soup = BeautifulSoup(response.content, "html.parser")
                new_publications = soup.find_all("tr", {"class": "gsc_a_tr"})
                
                for pub in new_publications:
                    title = pub.find("a", {"class": "gsc_a_at"}).text
                    authors = pub.find("div", {"class": "gs_gray"}).text
                    journal = pub.find_all("div", {"class": "gs_gray"})[1].text
                    citations = pub.find("a", {"class": "gsc_a_ac"}).text
                    year = pub.find("span", {"class": "gsc_a_h"}).text
                    publications.append({
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "citations": citations,
                        "year": year
                    })

                # If fewer than 100 publications were found, we've reached the end
                if len(new_publications) < 100:
                    return publications

                start += 100
                break
            elif response.status_code == 429:
                # Rate limited; wait and retry
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to fetch publications data.")
                return None

    print("Exceeded maximum retries while fetching publications.")
    return None

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

            # Extract name
            name_div = soup.find("div", {"id": "gsc_prf_in"})
            if name_div:
                profile["name"] = name_div.text
            else:
                print("Failed to find name div")

            # Extract affiliation
            affiliation_div = soup.find("div", {"class": "gsc_prf_il"})
            if affiliation_div:
                profile["affiliation"] = affiliation_div.text
            else:
                print("Failed to find affiliation div")

            # Extract research interests
            interests = soup.find_all("a", {"class": "gsc_prf_inta gs_ibl"})
            if interests:
                profile["interests"] = [interest.text for interest in interests]
            else:
                print("Failed to find interests")

            # Extract citation metrics
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

            # Extract publication details
            publications = fetch_all_publications(user_id)
            if publications is not None:
                profile["publications_count"] = len(publications)
                profile["publications"] = publications
            else:
                profile["publications_count"] = "Failed to count publications"
                profile["publications"] = []

            return profile
        elif response.status_code == 429:
            # Rate limited; wait and retry
            print(f"Rate limited. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            print("Failed to fetch profile data.")
            return None

    print("Exceeded maximum retries while fetching profile.")
    return None

def write_to_csv(profile_data, filename="scholar_profile.csv"):
    """Write profile data to a CSV file at the specified filename."""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", profile_data.get("name", "")])
        writer.writerow(["Affiliation", profile_data.get("affiliation", "")])

        # Interests
        interests = profile_data.get("interests", [])
        writer.writerow(["Interests"] + interests)

        # Citations
        citations = profile_data.get("citations", {})
        writer.writerow(["Citations (All)", citations.get("all", "")])
        writer.writerow(["Citations (Recent)", citations.get("recent", "")])

        # h-index
        h_index = profile_data.get("h_index", {})
        writer.writerow(["h-index (All)", h_index.get("all", "")])
        writer.writerow(["h-index (Recent)", h_index.get("recent", "")])

        # i10-index
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
# Tkinter GUI
# ---------------------------------------------------------------------
def ensure_output_folder():
    """
    Ensure that the google-scholar-search-results folder exists.
    """
    folder_name = "google-scholar-search-results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def on_submit():
    """
    1. Retrieve text from 'entry_scholar_urls'.
    2. Split by comma to handle multiple Google Scholar URLs.
    3. For each URL, parse the user ID, fetch the profile, save CSV in google-scholar-search-results.
    4. Display info in the text widget.
    """
    user_input = entry_scholar_urls.get().strip()
    if not user_input:
        messagebox.showwarning("Input Error", "Please enter at least one Google Scholar profile URL.")
        return

    # Clear previous text in the output box
    output_text.delete("1.0", tk.END)

    # Create the folder if it doesn't exist
    results_folder = ensure_output_folder()

    # Split multiple URLs separated by commas
    url_list = [url.strip() for url in user_input.split(",") if url.strip()]
    
    # Process each URL
    for url in url_list:
        user_id = parse_user_id(url)
        if not user_id:
            output_text.insert(tk.END, f"Could not parse user ID from URL: {url}\n\n")
            continue
        
        profile_data = fetch_scholar_profile(user_id)
        if profile_data:
            # Display some data in the text widget
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

            # Write CSV for this user in the google-scholar-search-results folder
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

lbl_scholar_urls = tk.Label(frame, text="Enter a Google Scholar profile page address (or multiple, separated by commas):")
lbl_scholar_urls.grid(row=0, column=0, sticky=tk.W)

entry_scholar_urls = tk.Entry(frame, width=80)
entry_scholar_urls.grid(row=1, column=0, padx=5, pady=5)

# Button to fetch profiles
btn_submit = tk.Button(frame, text="Fetch Profile(s)", command=on_submit)
btn_submit.grid(row=2, column=0, pady=10)

# Text box to display results
output_text = tk.Text(frame, width=80, height=20)
output_text.grid(row=3, column=0, padx=5, pady=10)

root.mainloop()
