import os
import re
from PIL import Image
import bs4


def load_file_as_soup(file_name):
    """ Loads html located at file_name as a soup obj """
    with open(file_name, 'r') as f:
        s = f.read()
        soup = bs4.BeautifulSoup(s)
    return soup

def to_coord(vals):
    """ convert listed values into coordinates (x0,y0,x1,y1) for bounding box """
    pix = 0.0786 * 0.651515 / 0.6352459016
    coord = (vals[0] * 0.61803921568 * pix, vals[1] * pix, vals[2] * 0.61803921568 * pix, vals[3] * pix)
    coord = [int(x) for x in coord]
    vals = (coord[0], coord[1], coord[0] + coord[2],  coord[1] + coord[3])
    return vals


def trans_coord(im, coord):
    out = im.transform((coord[2] - coord[0], coord[3] - coord[1]), Image.EXTENT, coord)
    return out


def get_image_list(files):
    """ given a list of files (inside ctdm), load a list of images (.jpg) files """
    im_list = []
    for f in files:
        if f[-4:] == ".jpg":
            im_list += [Image.open(f)]
    return im_list


def process_xml(g, im_list):
    """ Given an xml file name, process the required images and files """
    s = load_file_as_soup(g)
    for art in s.find_all('article'):
        import unicodedata
	""" Create a legal file name from the title. Possible to make this into a one-liner? """

        this_id = unicode(str(art.find('title').text.encode('utf-8', 'ignore'))[:64])
        print("Found item " + this_id)
        this_id = unicodedata.normalize('NFKD', this_id).encode('ascii', 'ignore')
        this_id = unicode(re.sub('[^\w\s-]', '', this_id).strip().lower())
        this_id = re.sub('[-\s]+', '_', this_id)
        if this_id=="":
        	this_id = "unknown"
        this_id = issuedate + "_" + this_id
        try:
            os.mkdir("output/" + issuedate + "/" + this_id)
        except OSError:
            pass
        i = 0
        for x in art.find_all('coord'):
            page = int(x._attr_value_as_string("inpage")) - 1
            y = [int(y) for y in x.text.split(":")]
            coord = to_coord(y)
            out = trans_coord(im_list[page], coord)
            out.save("output/" + issuedate + "/" + this_id + "/" + str(i) + ".jpg")
            i += 1


# We will eventually loop over all 20k "papers"; for now just using this test case 

paper = "ctdm634808100057560437ubv"
files = [paper + "/" + x for x in os.listdir(paper)]
""" Extract the date from index.desc  """
for g in files:
	if g[-10:] == "index.desc":
		d = load_file_as_soup(g)
   		for date in d.find_all('date'):
   			print("Now processing " + date.text)
   			issuedate=date.text

im_list = get_image_list(files)
for g in files:
    if g[-4:] == ".xml":
        process_xml(g, im_list)




