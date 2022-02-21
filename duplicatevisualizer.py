import sys
import glob
from PIL import Image


rows=1


print('normalized_duplicates/' + sys.argv[1])
for duplicateset in glob.glob('normalized_duplicates/' + sys.argv[1] + '/*_01'):
	duplicatekey = duplicateset.split('/')[-1][:-3]
	print('Potential Duplicates for date ' +  duplicatekey)
	potentialduplicates = ['normalized_storage/' + sys.argv[1] + '/' + duplicatekey + '_00']

	for thispotentialduplcate in glob.glob('normalized_duplicates/' + sys.argv[1] + '/' + duplicatekey + '*'):
		potentialduplicates.append(thispotentialduplcate)

	potentialduplicates.sort()
	print(potentialduplicates)

	print('Now creating image thumbnails')

	images = [Image.open(imagename + '/1.jp2').resize((300, 300)) for imagename in potentialduplicates]
	print(images)
	cols=len(images)
	# output image for grid with thumbnails
	new_image = Image.new('RGB', (cols*300, rows*300))

	# paste thumbnails on output
	i = 0
	for y in range(rows):
	    if i >= len(images):
	        break
	    y *= 300
	    for x in range(cols):
	        x *= 300
	        img = images[i]
	        new_image.paste(img, (x, y, x+300, y+300))
	        print('paste:', x, y)
	        i += 1

	# save output
	new_image.save('duplicatevisualizer/' + duplicatekey + '.jpg')