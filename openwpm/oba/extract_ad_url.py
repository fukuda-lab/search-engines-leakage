from pathlib import Path
import re
import json
import gzip
import argparse
from bs4 import BeautifulSoup
from adblockparser import AdblockRules

import sys


from urllib.parse import urlparse

# https://gist.github.com/gruber/8891611
# regex_s = r"(?i)\badurl=((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9\.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"

regex_s = r"(?i)\b(adurl|redirect)=((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9\.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"


def get_data_l_from_link(href_url):
    print("get_data_l_from_link: start")

    # href_url = link.get('href')

    # print("get_data_l_from_link: href_url: ", href_url)

    landing_page_url_l = re.findall(regex_s, href_url)

    # print("get_data_l_from_link: landing_page_url_l: %s" %
    #       (str(landing_page_url_l)))
    # print(iframe_d.keys())

    current_data_l = [(href_url, landing_page_url[0], landing_page_url[1])
                      for landing_page_url in landing_page_url_l]

    print("get_data_l_from_link: %d landing page data found" % (len(current_data_l)))

    print("get_data_l_from_link: end")

    return current_data_l


def check_source_string(ad_block_rules, iframe_key, data_d):
    print("check_source_string: start")

    # doc_url_s = data_d["doc_url"]
    source_s = data_d["source"]
    iframe_d = data_d["iframes"]

    print("check_source_string: iframe_key: ", iframe_key)
    # print("doc_url_s: ",doc_url_s)
    # print("source_s: ",source_s)

    # https://stackoverflow.com/questions/3075550/how-can-i-get-href-links-from-html-using-python
    soup = BeautifulSoup(source_s, "html.parser")

    link_data_l = soup.findAll('a', attrs={'href': re.compile("^http?s://")})
    link_l = [link_data.get('href') for link_data in link_data_l]
    print("check_source_string: %d link(s) found" % (len(link_l)))

    # print("check_source_string: link_l: %s" % (str(link_l)))

    ad_link_l = [
        link for link in link_l
        if ad_block_rules.should_block(link, {'script': False})
    ]
    print("check_source_string: %d ad link(s) found" % (len(ad_link_l)))

    current_data_l_l_tmp = [get_data_l_from_link(link) for link in ad_link_l]
    current_data_l_tmp = [
        item for sublist in current_data_l_l_tmp for item in sublist
    ]
    current_data_l = [(iframe_key, href_url, keyword, landing_page_url)
                      for (href_url, keyword,
                           landing_page_url) in current_data_l_tmp]

    data_l_l = [
        check_source_string(ad_block_rules, k, v)
        for (k, v) in iframe_d.items()
    ]
    data_l = [item for sublist in data_l_l for item in sublist]

    print("check_source_string: end")

    return current_data_l + data_l


def process(filter_file_path, input_json_gz_path, output_directory_path):
    print("process: start")

    print("process: reading blocking list")
    # f = open(easylist_file_path)
    # filter_l = f.read().splitlines()
    filter_l_l = [open(path).read().splitlines() for path in filter_file_path]
    filter_l = [item for sublist in filter_l_l for item in sublist]

    ad_block_rules = AdblockRules(filter_l)

    print("process: reading crawled iframe JSON gz")
    f = gzip.open(input_json_gz_path, 'rb')

    # file_content=f.read()

    # json_path = "datadir/sources/tete.json"
    # f = open(json_path)

    print("process: loading JSON")
    data_d = json.load(f)

    print("process: checking URL")
    data_l = check_source_string(ad_block_rules, "init", data_d)

    print(data_l)

    print("process: end")

def main():
    print("main: start")

    parser = argparse.ArgumentParser()
    # parser.add_argument('--filter-file-path',
    #                     nargs='+',
    #                     type=str,
    #                     required=True,
    #                     help='AdBlock filter file path list')
    parser.add_argument('-f',
                        '--filter-file-path',
                        action='append',
                        type=str,
                        required=True,
                        help='Add AdBlock filter file path to list')
    parser.add_argument("-i",
                        "--input-json-gz-path",
                        type=str,
                        required=True,
                        help="Input JSON gz path")
    parser.add_argument("-o",
                        "--output-directory-path",
                        type=str,
                        required=True,
                        help="Output directory path")
    # parser.add_argument("-n",
    #                     "--url-nb",
    #                     type=int,
    #                     default=80,
    #                     help="Nb of URL to crawl")
    # parser.add_argument("-e",
    #                     "--exponential-law-mean",
    #                     type=float,
    #                     default=180,
    #                     help="Exponential law mean")
    # parser.add_argument("-v", "--verbosity", action="count", default=0)
    args = parser.parse_args()

    filter_file_path = args.filter_file_path
    input_json_gz_path = args.input_json_gz_path
    output_directory_path = args.output_directory_path
    # url_nb = args.url_nb
    # exponential_law_mean = args.exponential_law_mean

    print("main: filter_file_path: %s" % (filter_file_path))
    print("main: input_json_gz_path: %s" % (input_json_gz_path))
    print("main: output_directory_path: %s" % (output_directory_path))
    # print("main: url_nb: %s" % (url_nb))
    # print("main: exponential_law_mean: %s" % (exponential_law_mean))

    process(
        filter_file_path,
        input_json_gz_path,
        output_directory_path,
    )

    print("main: end")


if __name__ == "__main__":
    main()
