import os
from datetime import datetime
import shutil

convert_days = {
    "Monday": "Poniedziałek",
    "Tuesday": "Wtorek",
    "Wednesday": "Środa",
    "Thursday": "Czwartek",
    "Friday": "Piątek",
    "Saturday": "Sobota",
    "Sunday": "Niedziela"
}

working_directory = os.getcwd()

def file_modification_date(path):
	return os.path.getmtime(path)

def path(file):
	return working_directory + "/" + file

def check_if_file_allowed(file):
	allowed_extensions = ["jpg", "JPG", "png", "PNG"]
	for ext in allowed_extensions:
		if(filename.endswith("." + ext)): return True
	return False

for file in os.listdir(working_directory):
	filename = os.fsdecode(file)
	ext = os.path.splitext(file)[-1]
	if(not check_if_file_allowed(filename)): continue

	t = file_modification_date(path(filename))
	t = datetime.fromtimestamp(t)
	day = convert_days[t.strftime("%A")]
	folder_date = t.strftime(f"%Y-%m-%d ({day})")
	t = t.strftime(f"%Y-%m-%d %H-%M-%S ({day})")

	if not os.path.exists(path(folder_date)):
		os.makedirs(path(folder_date))
	shutil.move(path(filename), path(folder_date + "/" + t + ext))


