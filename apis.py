import requests

def id_given_isbn(f):
    res=requests.get("https://www.goodreads.com/book/isbn_to_id", params={"key": "...", "isbn": f})
    if res.status_code != 200:
        raise Exception("Error")
    return "https://www.goodreads.com/book/show/"+str(res.json())

def reviews_given_isbn(f):
    res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "...", "isbns": f}).json()
    return res

def main():
    return reviews_given_isbn("0340893605")

if __name__ == "__main__":
    main()