import time
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from summarizer import summarize

SEARCH_URL = "https://arynews.tv/search/?q={}"
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


def first_result_url(driver, keyword):
    driver.get(SEARCH_URL.format(quote_plus(keyword)))
    deadline = time.time() + 25
    while time.time() < deadline:
        for a in driver.find_elements(By.CSS_SELECTOR, "a[href]"):
            href = a.get_attribute("href") or ""
            if "technologyreview.com/20" in href and href.count("/") >= 6:
                return href.split("?")[0]
        time.sleep(1)
    return None


def article_text(driver, url):
    driver.get(url)
    WebDriverWait(driver, 20).until(lambda d: d.find_elements(By.TAG_NAME, "p"))
    paras = [p.text.strip() for p in driver.find_elements(By.CSS_SELECTOR, "article p, main p, p")]
    seen, out = set(), []
    for p in paras:
        if len(p.split()) >= 8 and p not in seen:
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
