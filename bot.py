import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileWriter, PdfFileReader
from requests_html import HTMLSession

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()
urls = set()

# This will make sure that a proper scheme (protocol, e.g http or https) and domain name exists in the URL.
def is_valid(url):
    """Checks whether `url` is a valid URL"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):

    session = HTMLSession()
    try:
        response = session.get(url)
    except:
        print("Check your url")
        return {}
        
    try:
        response.html.render()
    except:
        pass
#     soup = BeautifulSoup(requests.get(url).content, "html.parser")
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(response.html.html, "html.parser")  # this is assumed for javascript loaded pages 
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue

        
        href = urljoin(url, href)
#         print(href)
        parsed_href = urlparse(href)
        if parsed_href.query != "":
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path + "?" + parsed_href.query
        else:
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # its external link
            if href not in external_urls:
                external_urls.add(href)
            continue
        # else its internel links
        urls.add(href)
        internal_urls.add(href)
    return urls
        
        

def make_dir(dirName):
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ")
    else:
        print("Directory " , dirName ,  " already exists")



total_urls_visited = 0

# help to call give number of times inside the website
def crawl(url, max_urls=10):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 10.
    """
    global total_urls_visited
    total_urls_visited += 1
    links = get_all_website_links(url)
    links = list(links)
    if len(links) > 0:
        for link in links:
            if total_urls_visited > max_urls:
                break
            crawl(link, max_urls=max_urls)



if __name__ == "__main__":
    
    total_urls_visited = 0
    
    root_url = input("Enter the url:")
    max_url = int(input("Max number internel url to crawl:"))
    select_number_of_pdf = int(input("Number of pdf to dowload:"))
    
    links = get_all_website_links(root_url)
    print(len(links))
    list_links = list(links)
    if len(list_links) < max_url:
    	max_url = len(list_links)
    for i in range(max_url):
        get_all_website_links(list_links[i])



    print("[+] Total External links:", len(external_urls))
    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total:", len(external_urls) + len(internal_urls))
        

    #Create pdfs and txts 
    import os
    parsed = urlparse(root_url)
    netloc = parsed.netloc

    if not os.path.exists("pdfs"):
        os.mkdir("pdfs")

    if not os.path.exists("txts"):
        os.mkdir("txts")
        
    pdf_dirName = os.path.join("pdfs",netloc.split(".")[1])
    txt_dirName = os.path.join("txts",netloc.split(".")[1])


    make_dir(pdf_dirName)
    make_dir(txt_dirName)

    internal_urls = list(internal_urls)
    pdf_urls = [iu for iu in internal_urls if iu.endswith(".pdf")]

    total_pdfs = len(pdf_urls)
    print(f"Total pdfs {total_pdfs}!")


    def dowload_pdf_save_txt(url):
        pdf_name = url.split("/")[-1]

        print(pdf_name)
        try:
            response = requests.get(url)

            with open(f'{pdf_dirName}/{pdf_name}', 'wb') as f:
                f.write(response.content)
                f.close()
            output = PdfFileWriter()
            inputs = PdfFileReader(open(f'{pdf_dirName}/{pdf_name}', "rb"))
            print (f"{pdf_name} has {inputs.getNumPages()} pages.")
            total_pages = inputs.getNumPages()
            txt = url+"\n" + ""
            for i in range(total_pages):
                txt+=inputs.getPage(i).extractText()

            with open(f'{txt_dirName}/{pdf_name.split(".")[0]}.txt', 'w+') as f:
                f.write(txt)
                f.close()
        except:
            pass

        
    import time
    t1 = time.time()
    count = 0

    for pdf_url in pdf_urls[:select_number_of_pdf]:
        count+=1
        dowload_pdf_save_txt(pdf_url)
    print(f"Total {count} pdfs downloaded:")
    t2 = time.time()
    print(f'!{t2-t1} " seconds take!')
    print("Lets see pdfs and txts folder")
        
        


