import requests
import urllib2

from lxml import html
################################################################################
# Downloads and processes the ELM database
# 1. Reqeusts list of motifs
# 2. For each motif it extracts its name, pattern, and probability
# 3. Extracts each motif's GO terms from its HTML site
# 4. Requests list of GO terms 'go-basic.obo'
# 5. For each motif finds its parents and all of its descendants
#    (1 up, all down)
# 6. Writes motifs to a file in format 'name pattern probability go_terms', e.g.
#    'elm1 [SK].P 0.0000000002 1000 1001 1002'
#
# Usage: ./scrape_elm.py output_name"
#
################################################################################


def get_motif_go_terms(elm_id):
    page = requests.get("http://elm.eu.org/elms/elmPages/{}.html".format(
        elm_id))
    tree = html.fromstring(page.text)
    go_terms = []
    for i in tree.get_element_by_id('ElmDetailGoterms').iterlinks():
        if i[2].startswith("http://www.ebi.ac.uk/QuickGO/GTerm?id=GO:"):
            go_terms += [i[2].split(':')[2]]
    return go_terms


def find_children(goid, result, go_file):
    search = False
    for lineI in go_file[::-1]:
        if lineI.startswith("is_a: GO:{}".format(goid)):
            search = True
        elif search and lineI.startswith("id: GO:"):
            new_id = lineI.split()[1].split(':')[1]
            if new_id not in result:
                find_children(new_id, result, go_file)
                result.add(new_id)
            search = False


def find_parents(goid, go_file):
    search = False
    result = set()
    for i, lineI in enumerate(go_file):
        if lineI.startswith("id: GO:{}".format(goid)):
            search = True
        elif search and lineI.startswith("id: GO:"):
            search = False
            break
        elif search and lineI.startswith("is_a: "):
            new_id = lineI.split()[1].split(':')[1]
            result.add(new_id)
        elif search and lineI.startswith("relationship: "):
            new_id = lineI.split()[2].split(':')[1]
            result.add(new_id)
        elif search and lineI.startswith("alt_id: "):
            new_id = lineI.split()[1].split(':')[1]
            result.add(new_id)
    return result


def extend_go_terms(go_file, motif_go_terms, go_families):
    newgos_set = set()
    for i in motif_go_terms:
        newgos_set.add(i)
        if i not in go_families.keys():
            go_families[i] = find_parents(i, go_file)
            go_children = set()
            find_children(i, go_children, go_file)
            go_families[i] = go_families[i].union(go_children)
        newgos_set.update(go_families[i])
    return list(newgos_set)


def get_data_from_url(url):
    req = urllib2.Request(url)
    return urllib2.urlopen(req).read().splitlines()
