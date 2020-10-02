import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os


def main(get_functions):
    ean = input("EAN: ")
    if not is_ean_valid(ean):
        print("Invalid EAN")
        return
    print("Checking prices in stores...")
    data = list()
    for i in range(len(get_functions)):
        print("Checking ({}/{})".format(i + 1, len(get_functions)))
        store = get_functions[i](ean)
        if store is not None:
            data.append(store)
    if len(data) == 0:
        print("Not found in any store")
    else:
        print("Found {} result{}!".format(len(data), "s" if len(data) > 1 else ""))
        show_results(data)
        save_txt(ean, data)
        save_csv(ean, data)


# Validates EAN
def is_ean_valid(ean):
    if not ean.isnumeric():
        return False
    if 12 <= len(ean) <= 13:
        return True
    return False


# Show results in console, if asked
def show_results(data):
    show = input("Show results in console? [y/n] ")
    if show.lower() == 'y':
        for store in data:
            print('{}\nName: {}\nPrice: {}\nStock: {}\nLink: {}\n'.format(*store))


# Save results in a TXT file, if asked
def save_txt(ean, data):
    save = input("Save results in TXT file? [y/n] ")
    if save.lower() == 'y':
        date = datetime.today().strftime('%Y-%m-%d')
        filename = "output/{}_{}.txt".format(ean, date)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            for store in data:
                file.write('{}\nName: {}\nPrice: {}\nStock: {}\nLink: {}\n\n'.format(*store))


# Save results in a CSV file, if asked
def save_csv(ean, data):
    save = input("Save results in CSV file? [y/n] ")
    if save.lower() == 'y':
        date = datetime.today().strftime('%Y-%m-%d')
        filename = "output/{}_{}.csv".format(ean, date)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write('store,name,price,stock,link\n')
            for store in data:
                file.write('{},{},{},{},{}\n'.format(*store))


# List of functions to get data from stores
get_functions = list()


# Get product info from GlobalData
# www.globaldata.pt
def get_globaldata(ean):
    try:
        url = "https://www.globaldata.pt/catalogsearch/result/?q=" + ean
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        result = soup.find_all(class_="product-item-info")
        if len(result) == 0:
            return None
        link = result[0].find("a")['href']
        prodpage = requests.get(link)
        soup = BeautifulSoup(prodpage.content, 'html.parser')
        prodean = soup.find(class_="ean").find(class_="value")
        if prodean is None:
            return None
        if int(prodean.text.strip()) != int(ean):
            return None
        result = soup.find(class_="product-info-main")
        name = result.find(class_="page-title").find(class_="base").text
        price = result.find(class_="price-final_price").find_all(class_="price")[-1].text.replace("\xa0", "")
        stock = result.find(class_="stock-shops").find("span").text
        return "Globaldata", name, price, stock, link
    except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException, AttributeError):
        return None
get_functions.append(get_globaldata)


# Get product info from SwitchTechnology
# www.switchtechnology.pt
def get_switchtech(ean):
    try:
        url = "https://www.switchtechnology.pt/index.php?route=product/search&search=" + ean
        headers = {'User-Agent': '...'}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        result = soup.find(class_="main-products product-grid").find_all(class_="product-thumb")
        if len(result) == 0:
            return None
        link = result[0].find(class_="name").find("a")['href']
        prodpage = requests.get(link, headers=headers)
        soup = BeautifulSoup(prodpage.content, 'html.parser')
        prodean = soup.find(class_="product-ean").find("span")
        if prodean is None:
            return None
        if int(prodean.text.strip()) != int(ean):
            return None
        result = soup.find(class_="product-details")
        name = result.find(class_="title").text
        price = result.find(class_="price-group").find("div").text
        stock = result.find(class_="product-stock").find("span").text
        return "Switch Technology", name, price, stock, link
    except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException, AttributeError):
        return None
get_functions.append(get_switchtech)


if __name__ == '__main__':
    main(get_functions)
