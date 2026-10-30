import time
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from summarizer import summarize

SEARCH_URL = "https://arynews.tv/search/{}"
BASE = "https://arynews.tv/"
SKIP = ("search", "category", "tag", "author", "writers", "about-us", "contact-us", "feedback",
        "privacy-policy", "mobile-apps", "live", "videos")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")


def make_driver():
    opts = Options()
    opts.binary_location = "/usr/bin/google-chrome"
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
              "--window-size=1366,900", f"--user-agent={UA}",
              "--disable-blink-features=AutomationControlled"):
        opts.add_argument(a)
    opts.page_load_strategy = "eager"
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=opts)
    driver.set_page_load_timeout(40)
    return driver


HREFS_JS = ("return Array.from(document.querySelectorAll('h2 a[href], h3 a[href], h4 a[href]'))"
            ".map(a => a.href);")


def first_result_url(driver, keyword):
    driver.get(SEARCH_URL.format(quote_plus(keyword)))
    deadline = time.time() + 25
    while time.time() < deadline:
        for href in driver.execute_script(HREFS_JS):
            href = (href or "").split("?")[0].split("#")[0]
            if not href.startswith(BASE):
                continue
            slug = href[len(BASE):].strip("/")
            if slug and "/" not in slug and slug not in SKIP and slug.count("-") >= 2:
                return href
        time.sleep(1)
    return None


PARAS_JS = "return Array.from(document.querySelectorAll('p')).map(p => p.innerText || '');"


def article_text(driver, url):
    driver.get(url)
    WebDriverWait(driver, 20).until(lambda d: d.find_elements(By.TAG_NAME, "p"))
    paras = [t.strip() for t in driver.execute_script(PARAS_JS)]
    seen, out = set(), []
    for p in paras:
        if len(p.split()) >= 8 and p not in seen and "ARY NEWS brings you" not in p:
            seen.add(p)
            out.append(p)
    return " ".join(out)


def search_and_summarize(keyword):
    driver = make_driver()
    try:
        url = first_result_url(driver, keyword)
        if not url:
            return None, "No results found"
        text = article_text(driver, url)
        return {"url": url, "summary": summarize(text)}, None
    finally:
        driver.quit()
