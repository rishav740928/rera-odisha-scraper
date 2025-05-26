import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://rera.odisha.gov.in"
PROJECT_LIST_URL = f"{BASE_URL}/projects/project-list"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_project_links():
    response = requests.get(PROJECT_LIST_URL, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.select("table tbody tr")[:6]  # Get only the first 6 projects
    links = [BASE_URL + row.select_one("a")["href"] for row in rows]
    return links

def get_project_details(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    def get_text(label):
        tag = soup.find("td", string=label)
        return tag.find_next_sibling("td").get_text(strip=True) if tag else "N/A"

    # Get data from main info tab
    regd_no = get_text("RERA Regd. No")
    project_name = get_text("Project Name")
    
    # Switch to Promoter Details tab
    promoter_tab_url = url.replace("project-detail", "promoter-details")
    promoter_response = requests.get(promoter_tab_url, headers=headers)
    promoter_soup = BeautifulSoup(promoter_response.content, "html.parser")

    company_name = promoter_soup.find("td", string="Company Name")
    company_name = company_name.find_next_sibling("td").get_text(strip=True) if company_name else "N/A"

    address = promoter_soup.find("td", string="Registered Office Address")
    address = address.find_next_sibling("td").get_text(strip=True) if address else "N/A"

    gst_no = promoter_soup.find("td", string="GST No.")
    gst_no = gst_no.find_next_sibling("td").get_text(strip=True) if gst_no else "N/A"

    return {
        "RERA Regd. No": regd_no,
        "Project Name": project_name,
        "Promoter Name": company_name,
        "Promoter Address": address,
        "GST No": gst_no
    }

def main():
    links = get_project_links()
    data = [get_project_details(link) for link in links]
    df = pd.DataFrame(data)
    print(df)
    df.to_csv("rera_odisha_projects.csv", index=False)

if __name__ == "__main__":
    main()
