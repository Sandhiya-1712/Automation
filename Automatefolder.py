import os
import shutil
from pathlib import Path
import datetime

#-----------------------------
#1.set your downloads path
#------------------------------

Downloads = Path(r"C:\Users\ssand\Downloads")

#-------------------------------
#2.category rules
#-----------------------------
CATEGORIES ={
    "Images" :[".jpg", ".jpeg", ".png", ".gif",".webp",".jfif", ".heic"],
    "Documents":[".pdf",".docx",".txt",".pptx",".doc",".xlsx",".xls"],
    "CSV_files":[".csv"],
    "videos":[".mp4",".mkv",".avi"],
    "Archives":[".zip",".rar",".7z",".tar",".gz",".tar.gz"],
}

#Create folder for uncategorized files
CATEGORIES["Others"]=[]

#create extension -> category map for fast lookup
ext_to_cat = {}
for cat, exts in CATEGORIES.items():
    for e in exts:
        ext_to_cat[e] = cat

#List of suffixes that indicate partial downloads or temp files(skip or handle separately)
TEMP_SUFFIXES = {".crdownload", ".part", ".tmp", ".partial"}

#--------------------------------------------
#3.create category folders
#---------------------------------------

for folder in CATEGORIES.keys():
    (Downloads/folder).mkdir(exist_ok=True)

#------------------------------------------------
#4.logging helpers
#----------------------------------------------
def append_log(fname, message):
    with open(Downloads/fname,"a", encoding = "utf-8") as f:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] {message}\n")

def log_debug(message):
    append_log("automation_debug_log.txt",message)

def log_action(message):
    append_log("automation_log.txt",message)

#-----------------------------------------------------
#5. cleaner functions (robust)
#-----------------------------------------------------

def auto_clean_downloads():
    moved_count =0
    skipped_count =0
    others_count =0

    for path in Downloads.iterdir():
        #skip the folders we created and logged
        if path.is_dir():
            #skip the category directions themselves
            if path.name in CATEGORIES:
                continue
            else:
                log_debug(f"Skipping directory:{path.name}")
                continue
        
        if not path.is_file():
            log_debug(f"skipping non-file: {path}")
            skipped_count+=1
            continue

        name = path.name
        suffix = path.suffix.lower()
        suffixes = [s.lower() for s in path.suffixes]

        #if file is in temporary /in-progress download, skip(or move to temp)
        if suffix in TEMP_SUFFIXES or any(s in TEMP_SUFFIXES for s in suffixes):
            log_debug(f"Skipping temp/in-progress file: {name} (suffixes ={suffixes})")
            skipped_count+=1
            continue

        #try to exact match on last suffix first
        category = ext_to_cat.get(suffix)

        #if not found, try matching by checking earlier suffixes
        if category is None and len(suffixes)>1:
            #check from left to right for known extensions
            for s in suffixes:
                if s in ext_to_cat:
                    category = ext_to_cat[s]
                    log_debug(f"Matched by inner suffix: {name} -> {s} -> {category}")
                    break

        #Special handling:treat 'tar.gz' as archives if needed
        if category is None and "".join(suffixes[-2:]) == ".tar.gz":
            category = ext_to_cat.get(".tar.gz","Archives")

        # Move file
        if category:
            dest_folder = Downloads/category
            try:
                shutil.move(str(path), str(dest_folder/name))
                log_action(f"Moved:{name} -> {category}")
                moved_count+=1
            except Exception as e:
                log_debug(f"Failed to move{name}:{e}")
        else:
            #No category matched -> move to others
            try:
                shutil.move(str(path),str(Downloads/"Others"/name)) 
                log_action(f"Moved:{name} -> Others (suffix = {suffixes})")
                others_count+=1
            except Exception as e:
                log_debug(f"Failed to move to others{name}:{e}")

    print(f"Done.moved = {moved_count}, others = {others_count}, skipped = {skipped_count}")
    log_debug(f"Summary: moved = {moved_count}, others = {others_count}, skipped = {skipped_count}")               

#-----------------------------------------------
#6.Run the cleaner
#-----------------------------------------------

if __name__ == "__main__":
    log_debug("=== starting auto clean_downloads run ===")
    auto_clean_downloads()
    log_debug("=== Finished run ===")