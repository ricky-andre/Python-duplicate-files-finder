# Python 3.9.1
import os
import hashlib
from collections import defaultdict
import re
import json

src_folder = "E:\My Files"

def generate_md5(fname, chunk_size = 16384, first_chunk = False):
    # Function which takes a file name and returns md5 checksum of the file
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        # Read the 1st block of the file
        chunk = f.read(chunk_size)
        if first_chunk:
            hash.update(chunk)
        else:
            while chunk:
                hash.update(chunk)
                chunk = f.read(chunk_size)
    # Return the hex checksum
    return hash.hexdigest()

if __name__ == "__main__":
    full_file_dict = defaultdict(list)
    file_size_dict = defaultdict(list)
    file_to_hash_dict = defaultdict(list)

    # ext_filter = "(mp4|mp3|wav|avi|jpg|txt)"
    ext_filter = ".*"

    if os.path.exists('hash_data.json'):
        fp_to_hash = json.load(open('hash_data.json'))
        #print(fp_to_hash)
    else:
        fp_to_hash = {}

    # Walk through all files and folders within directory
    for path, dirs, files in os.walk(src_folder):
        print("Analyzing directory {}".format(path))
        for each_file in files:
            if re.search(ext_filter, each_file.split(".")[-1].lower()):
                # The path variable gets updated for each subfolder
                file_path = os.path.join(os.path.abspath(path), each_file)
                file_size_dict[os.path.getsize(file_path)].append(file_path)
    print("")
    
    for size in file_size_dict:
        if len(file_size_dict[size])>1:
            #print("Found "+(str)(len(file_size_dict[size]))+" files with length "+(str)(size))
            # we now have 2 or more files with EXACTLY the same length, we now read only the
            # first 16384 bytes and produce a hash. If the files are equal, 
            small_file_hash_dict = defaultdict(list)
            for path in file_size_dict[size]:
                hash = generate_md5(path, first_chunk=True)
                small_file_hash_dict[hash].append(path)
                #print("Partial hash "+hash+" for file \""+path+"\"")
            
            # now let's cycle through this dictionary of arrays, the key being the hash
            # in case the length of the array is bigger than 1, we need to check the full hash
            for hash in small_file_hash_dict:
                if len(small_file_hash_dict[hash])>1:
                    for file in small_file_hash_dict[hash]:
                        #print("Retrieving hash for file \"" + file + '\" ... ')
                        # If there are more files with same checksum append to list
                        if not file in fp_to_hash:
                            #print(' calculating hash for file')
                            hash = generate_md5(file)
                        else:
                            #print(' found in the database')
                            hash = fp_to_hash[file]
                        #print('hash value: ' + hash)
                        full_file_dict[hash].append(file)
                        file_to_hash_dict[file] = hash
                #else:
                #    print("Couldn't find two equal hashes on file's first 16Kbytes")

    with open('hash_data.json', 'w') as fp:
        json.dump(file_to_hash_dict, fp,  indent=4)

    # Identify keys (checksum) having more than one values (file names)
    duplicate_files = (val for key, val in full_file_dict.items() if len(val) > 1)
    
    for file_names in duplicate_files:
        print("Duplicated files:")
        for file in file_names:
            print(file)
        print("")

    print("Done")
