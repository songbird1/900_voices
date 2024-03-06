'''
file_magler.py 
Convert a single trint data file into format suitable for database consumption.
Can be called directly, or from another python file
'''

import sys

soundfile = ""

def store_sound_file_name(content):
    '''
    Find the sound filename and store it
    '''
    start = '<title>'
    end = '</title>'
    global soundfile
    soundfile = content[content.index(start)+len(start):content.index(end)]

def strip_out_header(content):
    '''
    Source files contain a large area of redundant data.
    Remove this from the output file.
    '''

    target_string = r'class="timecode">[00:00:00] </span>'

    # Find the target string and remove content before it
    position = content.find(target_string) + len(target_string)
    if position != -1:  # The target string was found
        new_content = content[position:]
        print("found it")
    else:
        new_content = content  # Target string not found; no modification

    return new_content

def add_new_header(content):
    '''
    Database requires new header, add it here
    '''

    new_header = 'id,data_m,data_d,data_w,data_fn\n'
    new_content = new_header + content 
    return new_content

def strip_out_footer(content):
    '''
    Source files contain a large area of redundant data.
    Remove this from the output file.
    '''

    target_string = r'</p></section></article>'

    # Find the target string and remove after it
    position = content.find(target_string) + len(target_string)
    if position != -1:  # The target string was found
        new_content = content[:content.index(target_string)]
        print("found it")
    else:
        new_content = content  # Target string not found; no modification

    return new_content


def process_file(source, destination):
    '''
    Take source file, carry out all processing required for database
    consumption, load result into destination
    '''

    # open source file
    print(f"{source}, {destination}")

    # Define find-and-replace pairs
    replacements = {
        r'<span class="word" data-m="': ',',
        r'" data-d="': ',',
        r'">' : ',',
        r', </span>': ',filename\n', # catch a word with trailing comma
        r'. </span>': ',filename\n', # catch a word with a full stop
        r'</span>' : ',filename\n',
        # Add as many pairs as needed
    }

    # Step 1: Read the file content into memory
    with open(source, 'r', encoding='utf-8') as file:
        content = file.read()

    # Step 2: store sound file name
    store_sound_file_name(content)

    # Step 3: remove header
    content = strip_out_header(content)

    # Step 4: remove footer
    content = strip_out_footer(content)

    # Step 5: add new header for csv parser
    content = add_new_header(content)

    # Step 6: Perform all find-and-replace operations
    for old_text, new_text in replacements.items():
        content = content.replace(old_text, new_text)

    # Step 7: Replace filename with soundfile, doesn't want to work in def?
    content = content.replace("filename",soundfile)

    # Step 8: Write the modified content back to the file
    with open(destination, 'w', encoding='utf-8') as file:
        file.write(content)



if __name__ == "__main__":
    
    if len(sys.argv) == 3:
        source = sys.argv[1]
        destination = sys.argv[2]

        process_file(source,destination)
