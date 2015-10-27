import urllib2
import get_genes
import os
import math
import time
from random import randrange
from xml.dom.minidom import parseString
from cookielib import domain_match
try:
    import xml.etree.cElementTree as ET
except ImportEror:
    import xml.etree.ElementTree as ET

def get_xml_minidom(url):
    xml = urllib2.urlopen(url)
    dom = parseString(xml.read())
    return dom

def get_xml(url):
    if url:
        print 'url', url
        file = urllib2.urlopen(url)
        xml = file.read()
        file.close()
        return xml

def make_search_url(base_URL, articles, university, type_field):
    max_papers = "&retmax=%d" % articles
#    title_abstract_add = "[tiab]"
    search_url_add = "esearch.fcgi?db=pubmed&term="      #University%20of%20Pittsburgh%5BAffiliation%5D"
    url = base_URL + search_url_add + type_field + university + max_papers
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

    max_papers = "&retmax=%d" % articles
    fetch_id_string = ",".join(ids)
    fetch_url_add = "efetch.fcgi?db=pubmed&id=%s" % fetch_id_string
    full_url = base_URL + fetch_url_add + get_abstract_portion_URL + max_papers
    return full_url
#     else:
#         max_papers = "&retmax=%d" % articles
#         fetch_id_string = ",".join(ids["papers_to_download"])
#         fetch_url_add = "efetch.fcgi?db=pubmed&id=%s" % fetch_id_string
#         full_url = base_URL + fetch_url_add + get_abstract_portion_URL + max_papers
#         return None


def get_info_from_docs_xml(xml_list, ids):
    
    return_dict = {}
    for xml in xml_list:
#        root = ET.fromstring(xml)
        tree = ET.ElementTree(ET.fromstring(xml))
        root = tree.getroot()
        
        PMIDS = []
        for elem in tree.iter(tag = 'MedlineCitation'):
            for child in elem:
                if child.tag == 'PMID':
                    PMID = child.text
                    PMIDS.append(PMID)
        
        partial_return_dict_values = []
        for elem in tree.iter(tag='Article'):
            individual_paper_info = []
            for child in elem:
                if child.tag == 'Abstract':
                    for grandchild in child:
  #                      abstract_text = grandchild.text
                        abstract_text = 'PLACE HOLDER'
                        individual_paper_info.append(abstract_text)
                if child.tag == 'ArticleTitle':
                    ArticleTitle = child.text
                if child.tag =='AuthorList':
                    Authors = []
                    for grandchild in child:
                        if grandchild.tag == 'Author':
                            Last_Name = ''
                            First_Name = ''
                            Affiliation = ''
                            for sub_branch in grandchild:
                                if sub_branch.tag == 'LastName':
                                    Last_Name = sub_branch.text
                                if sub_branch.tag == 'ForeName':
                                    First_Name = sub_branch.text
                                if sub_branch.tag == 'Affiliation':
                                    Affiliation = sub_branch.text
                            single_author = (First_Name, Last_Name, Affiliation)
                            Authors.append(single_author)
                    individual_paper_info.append(Authors)
            partial_return_dict_values.append(individual_paper_info)
        
        if len(PMIDS) != len(partial_return_dict_values):
            print 'Different number of PMIDS and results!!!!'
            
        for num, ID in enumerate(PMIDS):
            if ID in return_dict:
                pass
            else:
                return_dict[ID] = partial_return_dict_values[num]
#            partial_return_dict[ID] = partial_return_dict_values[num]
        
    return return_dict
        

def get_info_from_PubMed(articles, university, type_field):  # Creates URL to search PubMed
    base_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    get_abstract_portion_URL = "&rettype=abstract"
    
    search_url = make_search_url(base_URL, articles, university, type_field)
    
    if len(search_url) > 2000:
        return_dict = {}
        raise error('Length of search URL is greater than 2000')
        return return_dict
    
    id_xml_as_String = get_xml(search_url)
    full_ID_List = get_ID_list(id_xml_as_String)
    id_list = full_ID_List['papers_to_download']
    info_from_PubMed = {}
    if full_ID_List["papers_to_download"]:
        size = 200
        id_lists = [id_list[i:i+size] for i  in range(0, len(id_list), size)]
        docs_xml_list = []
        for sub_list in id_lists:
            fetch_url = make_fetch_url(base_URL, get_abstract_portion_URL, sub_list, articles)
            docs_xml = get_xml(fetch_url)
            docs_xml_list.append(docs_xml)
            time.sleep(randrange(3,6))
        info_from_PubMed = get_info_from_docs_xml(docs_xml_list, full_ID_List)
    else:
        print 'Search returned no results'
        info_from_PubMed = {}
        
    return info_from_PubMed
        
        
def make_paper_objects(dict_of_info):
    """takes in dict of info, returns dictionary paper objects like
        ["paper_id#"]: paper object """
    ID_paper_obj_dict = {}
    if "fetched_id_list" in dict_of_info:
        fetched_id_list = dict_of_info["fetched_id_list"]
        title_list = dict_of_info["title_list"]
        abstract_list = dict_of_info["abstract_list"]
        author_list = dict_of_info["authors_list"]
    print author_list

def get_university(university):
    university = university.replace(' ', '%20')
    affiliation = '%5BAffiliation%5D'
    univ_search = university+affiliation
    return univ_search

def main():
# either search by university + author or gene + university
#  search type: 
#   select (1) for university+author, OR 
#   select (2) for university+gene   ####PROBABLY NOT GOING TO USE
    search_type = '1'
    articles = 1000
    university = 'University of Pittsburgh'
    gene = 'trpml1'
    Author_first = 'Kirill'
    Author_last = 'Kiselyov'
    
    
    Author_string = Author_last + '%2C%20' +Author_first + '%5BAuthor%5D'
    university = get_university(university)
    if int(search_type) == 1:
        docs_dict  = get_info_from_PubMed(articles, university, Author_string)
        # docs dict = {PMID:[ 'ABSTRACT_TEXT' , [('FIRST','LAST','Affiliation'),(('FIRST','LAST','Affiliation')]]}
    elif int(search_type) == 2:
        gene_field = '{0}%20AND%20' .format(gene)
        docs_xml  = get_info_from_PubMed(articles, university, gene_field , Author_first, Author_last)
        
    get_genes.main(docs_dict)

    
if __name__=="__main__":
    main()




