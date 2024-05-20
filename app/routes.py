from app import app
from flask import render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
from . import utils
import json
import os

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method=='POST':
        product_id = request.form.get('product_id')
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes['ok']:
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions_count = utils.extract(page_dom, "a.product-review_link > span")
            if opinions_count:
                all_opinions = []
                while(url):
                    response = requests.get(url)
                    page_dom = BeautifulSoup(response.text, "html.parser")
                    opinions = page_dom.select("div.js_product-review")
                    for opinion in opinions:
                        single_opinion = {
                            key: utils.extract(opinion, *value)
                                for key, value in utils.selector.items()
                        }
                        all_opinions.append(single_opinion)
                    try:
                        url = "https://www.ceneo.pl/"+page_dom.select_one("a.pagination__next")["href"].strip()
                    except TypeError: 
                        url = None
                    if not os.path.exists("opinions"):
                        os.makedirs("opinions")
                    with open(f"app/opinions/{product_id}.json", "w", encoding="UTF-8") as jf:
                        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
                return redirect(url_for('product', product_id=product_id))
            return render_template("extract.html", error="Product does not have any opinions.") 
        return render_template("extract.html", error="Product does not exist")
    return render_template("extract.html")

@app.route('/products')
def products():
    return render_template("products.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/product/<product_id>')
def product(product_id):
    return render_template("product.html", product_id=product_id)
