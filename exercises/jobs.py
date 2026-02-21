import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# from scraper import fetch_website_contents
from IPython.display import Markdown, display
from openai import OpenAI
from playwright.async_api import async_playwright, Playwright
from playwright.sync_api import sync_playwright

MODEL_GPT = "gpt-4o-mini"
MODEL_LLAMA = "llama3.2"

# set up environment
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

# Check the key

if not api_key:
    print(
        "No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!"
    )
elif not api_key.startswith("sk-proj-"):
    print(
        "An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook"
    )
elif api_key.strip() != api_key:
    print(
        "An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook"
    )
else:
    print("API key found and looks good so far!")

system_prompt = """
You are recruiter with 25 years of experience that analyzes job descriptions. 
When you are given a job posting, you will analyze the job posting and determine what would make a candidate a good fit.
Please respond with all the requirements, skills, and experience that would help a candidate pass
the applicant tracking system (ATS) of the company. 
Note, it's important to ensure that the candidate is not rejected by the ATS.
Please provide a sample resume that would pass ATS
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""
user_prompt_prefix = """
Here is the content of the job posting,
Provide a list of requirements, skills, and experience that would help a candidate pass 
the applicant tracking system (ATS) of the company: 


"""


# Step 1: configure playwright to scrape website
# Step 2: Scrape website with playwright
def scrape_website(url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        content = page.content()
        return content


def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website},
    ]


def summarize_content(html_content):
    # Get only the text parts of the webpage
    soup = BeautifulSoup(html_content, "html.parser")
    summary_text = soup.get_text(separator=" ", strip=True)
    return summary_text


def save_markdown(summary, filename="jobs.md", job=None):
    # Open the file summary.md
    with open(filename, "w", encoding="utf-8") as f:
        if job:
            f.write(f"# Summary of [{job}]({job})\n\n")
        else:
            f.write("# Summary\n\n")
        f.write(summary.strip())


def main():
    html = scrape_website(
        "http://fmgsuite.applytojob.com/apply/oTdBt0ICez/Software-Engineer-Remote"
    )

    summary = summarize_content(html)

    ollama = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    response = ollama.chat.completions.create(
        model=MODEL_LLAMA,
        messages=messages_for(summary)
    )

    result = response.choices[0].message.content

    save_markdown(result)
    print("execution was complete!")


# Step 2: Get gpt-4o-mini to do something which I don't know just yet
main()
