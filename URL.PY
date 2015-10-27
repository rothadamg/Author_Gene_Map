import urllib2
import xml.etree.ElementTree as ET
import os

def get_xml(url):
    if url:
        file = urllib2.urlopen(url)
        xml = file.read()
        file.close()
        return xml

def make_search_url(base_URL, q1, q2, articles):
    max_papers = "&retmax=%d" % articles
    title_abstract_add = "[tiab]"
    search_url_add = "esearch.fcgi?db=pubmed&term=University%20of%20Pittsburgh%5BAffiliation%5D"
    url = base_URL + search_url_add + max_papers
    return url

def get_ID_list(xml):
    try:
        root = ET.fromstring(xml)
        ID_List_ofElements = root.findall("./IdList/Id")
        ids = []
        for element in ID_List_ofElements:
            singleID_string = ET.tostring(element, method='text')
            singleID_string_stripped = singleID_string.replace("\n", "")
            ids.append(singleID_string_stripped)
    except AttributeError:
        ids = []
        print("No Papers with both queries were found on PubMed")
    existing_papers = []  # Use this in the future to make database of existing IDs 
    papers_to_download = []
    for ind_id in ids:
        papers_to_download.append(ind_id)

    full_ID_List = {"existing_papers":existing_papers,
                                    "papers_to_download":papers_to_download}
    return full_ID_List

def make_fetch_url(base_URL, get_abstract_portion_URL, ids, articles):
    if ids["papers_to_download"]:
        max_papers = "&retmax=%d" % articles
        fetch_id_string = ",".join(ids["papers_to_download"])
        fetch_url_add = "efetch.fcgi?db=pubmed&id=%s" % fetch_id_string
        full_url = base_URL + fetch_url_add + get_abstract_portion_URL + max_papers
        return full_url
    else:
        max_papers = "&retmax=%d" % articles
        fetch_id_string = ",".join(ids["papers_to_download"])
        fetch_url_add = "efetch.fcgi?db=pubmed&id=%s" % fetch_id_string
        full_url = base_URL + fetch_url_add + get_abstract_portion_URL + max_papers
        return None


def get_info_from_docs_xml(xml, ids):
       
    root = ET.fromstring(xml)
    def findall(whattofind):  # closure function -- http://en.wikipedia.org/wiki/Closure_%28computer_programming%29
        listofelements = []
        for b in root.findall(whattofind):
            
            c = b.text
            if isinstance(c, unicode):
                c = c.encode('ascii', 'ignore')  # Note: ignores unicode, does not keep unicode letters
            listofelements.append(c)
        return listofelements
    
    id_list = findall(".//ArticleId[@IdType='pubmed']")
    title_list = findall(".//ArticleTitle")
    abstract_list = findall(".//AbstractText")
    authors_list = []

    return_dict = {"fetched_id_list" : id_list, "title_list":title_list, "abstract_list":abstract_list, "authors_list": authors_list}
    return return_dict

def get_info_from_PubMed(articles):  # Creates URL to search PubMed
    base_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    get_abstract_portion_URL = "&rettype=abstract"
    search_url = make_search_url(base_URL, query, articles)
    print search_url
    import sys
    sys.exit()
    if len(search_url) > 2000:
        return_dict = {}
        return return_dict
    
    id_xml_as_String = get_xml(search_url)
    full_ID_List = get_ID_list(id_xml_as_String)
    info_from_PubMed = {}
    if full_ID_List["papers_to_download"]:
        fetch_url = make_fetch_url(base_URL,
                                   get_abstract_portion_URL,
                                   full_ID_List,
                                   articles)
        docs_xml = get_xml(fetch_url)
        info_from_PubMed = get_info_from_docs_xml(docs_xml,
                                        full_ID_List)

    return info_from_PubMed
        

def make_paper_objects(dict_of_info):
    """takes in dict of info, returns dictionary paper objects like
        ["paper_id#"]: paper object """
    ID_paper_obj_dict = {}
    if "fetched_id_list" in dict_of_info:
        fetched_id_list = dict_of_info["fetched_id_list"]
        title_list = dict_of_info["title_list"]
        abstract_list = dict_of_info["abstract_list"]
           
 

def main():
    articles = 20
    docs_xml  = get_info_from_PubMed(articles)


if __name__=="__main__":
    main()








