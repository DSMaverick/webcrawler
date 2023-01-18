from flask import Flask, render_template, send_file
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Connecting to SQLite
conn = sqlite3.connect('books.db', check_same_thread=False)

# Delete table if exists
conn.execute('''DROP TABLE IF EXISTS books;''')
# Create table
conn.execute('''CREATE TABLE books(title TEXT, url TEXT);''')

# Web Scraping
url = 'https://books.toscrape.com/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extracting title and url
for article in soup.find_all('article'):
    title = article.h3.a.attrs['title']
    url = article.h3.a.attrs['href']
    # Inserting into SQLite
    conn.execute("INSERT INTO books (title, url) VALUES (?, ?)", (title, url))
    conn.commit()

books_df = pd.read_sql_query("SELECT * FROM books", conn)
books_df.to_csv("books.csv", index=False)
books_df.to_xml("books.xml", index=False)

# Route to display data


@app.route('/')
def index():
    cursor = conn.execute("SELECT title, url from books")
    books = cursor.fetchall()
    return render_template('index.html', books=books)


@app.route('/download/<string:file_name>')
def download(file_name):
    return send_file(file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
