from bs4 import BeautifulSoup
import re
import aiohttp

class Book:
    full_title= ""
    title= ""
    author= ""
    author_link= ""
    author_img= ""
    tags= []
    rating= ""
    favorites= ""
    followers= ""
    chapter_count= ""
    page_count= ""
    description= ""
    image_link = ""

class Tag:
    name=""
    link=""



async def getBook(book_url):
    url_to_scrape = book_url
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url_to_scrape) as response:

            """ try: 
                request_page = urlopen(url_to_scrape)
            except urllib.error.HTTPError as e:
                fut.set_result(None)
                return; """
            
            if(response.status != 200):
                return;
            
            page_html = await response.text()
            html_soup = BeautifulSoup(page_html, 'html.parser')
            book = Book()

            # get book title
            book.full_title = html_soup.find("title").get_text()
            title_node = html_soup.find("div", attrs={"class": "fic-title"})
            book.title = title_node.find("h1").get_text()
            
            fiction_info_node = html_soup.find("div", attrs={"class": "fiction-info"})
            # get book statistics / relies on index position
            try:
                statistics_node = html_soup.find("div", attrs={"class": "stats-content"}).find_all("li", attrs={"class": "font-red-sunglo"})
                book.followers = statistics_node[2].get_text() #
                book.favorites = statistics_node[3].get_text() #
                book.page_count = statistics_node[5].get_text() #
                book.chapter_count = fiction_info_node.find("span", string=re.compile("Chapter"), attrs={"class": "label"}).get_text().split()[0]
            except IndexError as e:
                book.followers = ""
                book.favorites = ""
                book.page_count = ""
            
            # get book author
            book.author = html_soup.find("meta", attrs={"property": "books:author"})["content"]
            book.author_link = "https://www.royalroad.com" + title_node.find("a")["href"]
            book.author_img = "https://www.royalroad.com" + html_soup.find("div", attrs={"class": "portlet-body"}).find("img")["src"]
            
            # get tag list
            book_tags_list = fiction_info_node.find("span", attrs={"class": "tags"})

            del book.tags[:]
            for contributor in book_tags_list.find_all('a'):
                tag = Tag()
                tag.name = contributor.get_text()
                tag.link = "https://www.royalroad.com" + contributor["href"]
                book.tags.append(tag)
            # do interaction here for many authors

            # get book image
            book.image_link = html_soup.find("meta", attrs={"property": "og:image"})["content"]
            # get book description
            book.description = html_soup.find("meta", attrs={"property": "og:description"})["content"]
            # get book rating
            book.rating = html_soup.find("meta", attrs={"property": "books:rating:value"})["content"]
            return book
