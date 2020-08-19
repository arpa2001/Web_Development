import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "7isLrOkjqHxyy3d2FMXtXQ", "isbns": "9781632168146"})
print(res.json())
