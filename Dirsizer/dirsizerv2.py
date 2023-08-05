# TODO
# Bug: sometimes subfolder sizes are incorrectly added
# Feature: to optimize make result in html

import os

PRINT_TO_FILE = True
PRINT_TO_TERMINAL = False
MARKDOWN_ARROW_SIZE = 3
MAX_DEPTH = 5


def dirsizer(path = '.', depth = 0, foldername = ''):	# returns dirsize and details string
	tab = []		# (size, details, name)

	try:
		for f in os.listdir(path):
			fp = os.path.join(path, f)
			if os.path.islink(fp): continue 	# skip if it is symbolic link
			
			if not os.path.isdir(fp):
				size = os.path.getsize(fp)
				details = ' &nbsp;'*4*depth + ' ' + f + ' | **' + convert_size(size) + '**  '
				tab.append((size, details, f))
			else:
				if depth <= MAX_DEPTH:
					size, details = dirsizer(fp, depth+1, f)
					tab.append((size, details, f))
				else:
					size = get_size(fp)
					details = ' &nbsp;'*4*depth + ' ' + f + ' | **' + convert_size(size) + '**  '
					tab.append((size, details, f))
	except:
		tab.append((get_size(path), "PERMISSION ERROR", foldername))

	tab.sort(reverse=True)

	total_size = 0
	total_details = ''
	for subsize, subdetail, name in tab:
		total_size += subsize
		total_details += '\n' + subdetail

	return (total_size, markdownize(total_size, total_details, 
			(path if foldername == '' else foldername), depth,
			(True if depth == 0 else False)))


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def convert_size(size):
	if(size/(1048576*1024) >= 1):
		res = str(round(size/(1048576*1024), 2)) + ' gigabytes'
	elif(size/1048576 >= 1):
		res = str(round(size/1048576, 2)) + ' megabytes'
	else:
		res = str(size) + ' bytes'
	return res

def markdownize(size, details, name, depth = 0, open = False):
	return ('<details' + (' open' if open else '') + '>\n<summary>' + 
		   (' &nbsp;'*(4*depth-MARKDOWN_ARROW_SIZE)) + ' ' + name +
		    ' | <b> ' + convert_size(size) + 
		    ' </b> </summary>\n' + details + '\n</details>\n')


size, stuff = dirsizer(os.getcwd())

try:
	f = open('dirsize_results.md', 'w', encoding="utf-8")
except:
	print('PermissionError: cant save results\n')
	PRINT_TO_FILE = False
if PRINT_TO_FILE:
	f.write(stuff)
	f.close()
if PRINT_TO_TERMINAL:
	print(stuff)
