from flask import Flask

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from flask import Flask, jsonify
import os

import openai

app = Flask(__name__)

@app.route('/extract_ad_copies')
def extract_ad_copies():
    # Set the URL to navigate to with the pageId variable interpolated
    pageId = "53283489648"
    url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=DK&view_all_page_id={pageId}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all"

    # Set up the Chrome options to run headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Create a new instance of the Chrome browser driver with the headless option
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the URL
    driver.get(url)

    # Wait for the button to appear on the page
    allow_cookies_button = driver.find_element("xpath", '//button[normalize-space()="Allow essential and optional cookies"]')
    allow_cookies_button.click()

    print("COOKIE CHALLENGE PASSED!")

    # Find all the elements with the "xh8yej3" class name
    cards = driver.find_elements(By.CLASS_NAME, "_4ik4._4ik5")
    extracted_text = []

    # Get the innerHTML of each element and print it out
    # Iterate over the divs and extract the text from the spans
    for div in tqdm(cards, desc="Extracting spans"):
        spans = div.find_elements(By.TAG_NAME, "span")
        divs_inside = div.find_elements(By.TAG_NAME, "div")
        for span in spans:
            # Get the text inside the current span tag and check if it starts with any of the specified words
            span_text = span.text.strip()
            if span_text and not span_text.startswith(("Ad Library Report", "Ad Library", "Filters", "See ad details", "Watch More", "Active", "Started running on", "Platforms", "This ad has multiple versions", "ID:", "Sponsored", "Ad Library API", "About ads and data use", "Privacy", "Terms", "Cookies", "Meta", "2 ads use this creative and text", "Open Drop-down", "“")):
                span_text = span_text.replace("\n", "")
                extracted_text.append(span_text)

        for div_inside in divs_inside:
            div_text = div_inside.text.strip()
            if div_text and not div_text.startswith(("Ad Library Report", "Ad Library", "Filters", "See ad details", "Watch More", "Active", "Started running on", "Platforms", "This ad has multiple versions", "ID:", "Sponsored", "Ad Library API", "About ads and data use", "Privacy", "Terms", "Cookies", "Meta", "2 ads use this creative and text", "Open Drop-down", "“")):
                div_text = div_text.replace("\n", "")
                extracted_text.append(div_text)

    unique_text = []
    duplicates = 0
    for text in extracted_text:
        if text[:20] not in [t[:20] for t in unique_text]:
            unique_text.append(text)
        else:
            duplicates += 1

    print("EXTRACT DONE.")

    openai.api_key = "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"



    ad_copies = unique_text # your array of ad copies




    if ad_copies:

        for ad_copy in ad_copies[:5]:
            print(f"RATING THIS AD COPY:  {ad_copy}")
            print("\n")
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Please rate this ad copy from 1/10, and provide information about any messaging or branding issues with it {ad_copy}",
                temperature=0,
                max_tokens=300,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            
            )

            print(response.choices[0].text.strip())
            print("\n")

    else:
        print("NO ADS FOUND")


    print("AMOUNT OF DUPLICATES FOUND: " + str(duplicates))

    # Close the browser
    driver.quit()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
