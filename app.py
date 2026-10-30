from flask import Flask, jsonify, request

from scraper import search_and_summarize

REGISTRATION = "FA22-BAI-001"
NEWS_SOURCE = "ARY News Pakistan"

app = Flask(__name__)


@app.route("/")
def home():
    return f"""<html><head><title>News Scraper API</title></head>
<body style="font-family:sans-serif;margin:40px">
<h1>Registration Number: {REGISTRATION}</h1>
<p>News source: {NEWS_SOURCE}</p>
<p>API: <code>/get?keyword=&lt;keyword&gt;</code></p>
</body></html>"""


@app.route("/get")
def get():
    keyword = (request.args.get("keyword") or "").strip()
    if not keyword:
        return jsonify({"error": "keyword query parameter is required"}), 400
    try:
        result, err = search_and_summarize(keyword)
    except Exception as e:
        return jsonify({"error": f"scraping failed: {type(e).__name__}"}), 502
    if err:
        return jsonify({"error": err}), 404
    return jsonify({
        "registration": REGISTRATION,
        "newssource": NEWS_SOURCE,
        "keyword": keyword,
        "url": result["url"],
        "summary": result["summary"],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
