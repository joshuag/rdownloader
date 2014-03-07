import sys, os, mimetypes, time

import requests

from pyquery import PyQuery as pq

from IPython import embed

def grab_user_links(username, found_links=None):

    if not found_links:

        found_links = []


    url = "http://www.reddit.com/user/%s/submitted" % username

    r = requests.get(url)

    page = pq(r.text)

    links = page("a.title")

    for link in links:

        found_links.append(link.attrib["href"])

    next_links = page("a[rel='next']")

    if len(next_links) == 1:

        found_links.append(grab_user_links(next_links[0].attrib["href"], found_links))

    return found_links


def get_and_filter_pages(link_list, user_path):

    image_types = ['jpeg', 'gif', 'png', 'bmp', 'jpg', 'jfif', 'tiff']

    for link in link_list:

        if "imgur" not in link:
            continue

        time.sleep(1)

        file_type = mimetypes.guess_type(link)[0]

        if file_type:

            file_type = file_type[file_type.rfind("/")+1:]

            if file_type in image_types:

                download_image(link, user_path, file_type)

        else:

            parse_page_for_images(link, user_path)


def parse_page_for_images(link, user_path):

    time.sleep(1)

    r = requests.get(link)

    page = pq(r.text)

    #check for a single imgur image

    header = page("#image-title")

    if header:

        image = page("div#image div a")[0]

        download_image(image.attrib["href"], user_path)

    else:

        images = page("a.zoom")

        for image in images:

            download_image(image.attrib["href"], user_path)


def download_image(url, path, file_type=None):

    if url[0:2] == "//":
        url = "http:" + url

    r = requests.get(url, stream=True)

    file_name = url[url.rfind("/")+1:]

    file_path = path + os.sep + file_name

    if file_type:

        file_path + file_type

    if r.status_code == 200:    

        with open(file_path, 'wb') as f:

            for chunk in r.iter_content(1024):

                f.write(chunk)


def prep_ground(username):

    root_path = os.getcwd()

    user_path = root_path + os.sep + username

    if not os.path.exists(user_path):

        os.makedirs(user_path)

    get_and_filter_pages(grab_user_links(username), user_path)


if __name__ == "__main__":

    print prep_ground(sys.argv[1])