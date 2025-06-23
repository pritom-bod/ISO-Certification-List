import requests
from bs4 import BeautifulSoup
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify

ISO_LINKS = {
    "ISO 21500": "https://www.iso.org/standard/50003.html",
    "ISO 9001": "https://www.iso.org/standard/62085.html",
    "ISO 14001": "https://www.iso.org/standard/60857.html",
    "ISO 27001": "https://www.iso.org/standard/54534.html",
    "ISO 45001": "https://www.iso.org/standard/63787.html",
    "ISO 22000": "https://www.iso.org/standard/65464.html",
    "ISO 50001": "https://www.iso.org/standard/69426.html",
    "ISO 13485": "https://www.iso.org/standard/59752.html",
    "ISO 31000": "https://www.iso.org/standard/65694.html",
    "ISO 22301": "https://www.iso.org/standard/50038.html",
    "ISO 26000": "https://www.iso.org/standard/42546.html",
    "ISO 37001": "https://www.iso.org/standard/65034.html",
    "ISO 20000": "https://www.iso.org/standard/54431.html",
}

def scrape_iso(code, url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.select_one("h1").text.strip() if soup.select_one("h1") else code

        # Description
        desc = ""
        p = soup.select_one("#main-content p") or soup.select_one("p")
        if p:
            desc = p.text.strip()

        # Key Requirements
        key = []
        for h2 in soup.select("h2"):
            if "requirement" in h2.text.lower():
                ul = h2.find_next_sibling("ul")
                if ul:
                    key = [li.text.strip() for li in ul.select("li")]
                break

        # Applicable Industries
        applicable = []
        for h2 in soup.select("h2"):
            if "industry" in h2.text.lower():
                ul = h2.find_next_sibling("ul")
                if ul:
                    applicable = [li.text.strip() for li in ul.select("li")]
                else:
                    p_ind = h2.find_next_sibling("p")
                    if p_ind:
                        applicable = [p_ind.text.strip()]
                break

        if not applicable:
            applicable = ["N/A"]

        return {
            "ISO_Code": code,
            "Title": title,
            "Description": desc,
            "Applicable_Industries": ", ".join(applicable),
            "Key_Requirements": ", ".join(key),
            "Issuing_Body": "International Organization for Standardization (ISO)",
            "Certification_Process": "Third-party certification available",
            "Renewal_Period": "Typically every 3 years",
            "Official_Source_URL": url
        }
    except Exception as e:
        return {
            "ISO_Code": code,
            "Title": "Error fetching",
            "Description": f"Error: {str(e)}",
            "Applicable_Industries": "N/A",
            "Key_Requirements": "N/A",
            "Issuing_Body": "N/A",
            "Certification_Process": "N/A",
            "Renewal_Period": "N/A",
            "Official_Source_URL": url
        }

def iso_list_html(request):
    certs = []
    for code, url in ISO_LINKS.items():
        data = scrape_iso(code, url)
        certs.append({
            "ISO_Code": code,
            "Title": data["Title"],
            "Slug": slugify(code)
        })
    return render(request, "Scrape_list/list.html", {"certs": certs})

def iso_detail_json(request, slug):
    for code, url in ISO_LINKS.items():
        if slugify(code) == slug:
            data = scrape_iso(code, url)
            return JsonResponse(data, json_dumps_params={'indent': 2, 'ensure_ascii': False})
    return JsonResponse({"error": "ISO code not found"}, status=404)

def iso_download_excel(request):
    data_list = []
    for code, url in ISO_LINKS.items():
        data = scrape_iso(code, url)
        data_list.append(data)

    df = pd.DataFrame(data_list)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=iso_certifications.xlsx'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='ISO Standards', index=False)

    return response
