import os
from random import randint as rand

def get_size(start_path = './Unity'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


arr = []
TOTAL = 0
subfolders = [ f.path for f in os.scandir('.') if f.is_dir() ]

for folder in subfolders:
	# res = rand(1, 1048576*1024*2)
	res = get_size(start_path = folder)
	TOTAL += res

	arr.append([res, folder[2:]])
	
	if(res/(1048576*1024) >= 1):
		print(round(res/(1048576*1024), 2), 'gigabytes', end = '; ')
	elif(res/1048576 >= 1):
		print(round(res/1048576, 2), 'megabytes', end = '; ')
	else:
		print(res, 'bytes', end = '; ')
	
	print(folder[2:])


print('\n\n-------sorting-------\n')

arr.sort(reverse=True)
use_file = True
try:
	f = open('dirsize_results.txt', 'w')
except:
	print('PermissionError: cant save results\n')
	use_file = False
if use_file: f.write(str(os.getcwd()) + '\n\n')

for x, y in arr:
	if(x/(1048576*1024) >= 1):
		print(round(x/(1048576*1024), 2), 'gigabytes', end = '')
		if use_file: f.write(str(round(x/(1048576*1024), 2)) + ' gigabytes: ')
	elif(x/1048576 >= 1):
		print(round(x/1048576, 2), 'megabytes', end = '')
		if use_file: f.write(str(round(x/1048576, 2)) + ' megabytes: ')
	else:
		print(x, 'bytes', end = '')
		if use_file: f.write(str(x) + ' bytes: ')

	print(':', y)
	if use_file: f.write(y + '\n')

print('\nTOTAL:', end = ' ')
if use_file: f.write('\nTOTAL: ')

if(TOTAL/(1048576*1024) >= 1):
	print(round(TOTAL/(1048576*1024), 2), 'gigabytes')
	if use_file: f.write(str(round(TOTAL/(1048576*1024), 2)) + ' gigabytes\n')
elif(TOTAL/1048576 >= 1):
	print(round(TOTAL/1048576, 2), 'megabytes')
	if use_file: f.write(str(round(TOTAL/1048576, 2)) + ' megabytes\n')
else:
	print(TOTAL, 'bytes')
	if use_file: f.write(str(TOTAL) + ' bytes\n')

if use_file: f.close()
