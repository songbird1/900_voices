'''
file_magler.py 
Convert a single trint data file into format suitable for database consumption.
Can be called directly, or from another python file
'''

import sys
import re 

soundfile = ""

def store_sound_file_name(content):
    '''
    Find the sound filename and store it
    '''
    start = '<title>'
    end = '</title>'
    global soundfile
    soundfile = content[content.index(start)+len(start):content.index(end)]

def preprocess_substitutions(content):
    '''
    Source files contain some anomalies, this uses regexp to
    try to catch them and make substitutions
    '''
    # Substitute the test string because the timecode at the start isn't always zero
    test = r'class="timecode">\[\d+:\d+:\d+\] </span>'
    content = re.sub(test, 'class="timecode">[00:00:00] </span>',content)

    # Substitute 0 in a line without a duration, often duplicate start time
    test = r'<span class="word" data-m="\d+">'
    content = re.sub(test, '<span class="word" data-m="0" data-d="0">',content)

    # Substitute a blank for any number of spaces trailing a comma in the word
    test = r',\s+</span>'
    content = re.sub(test, ' </span>',content)

    return content  

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
    else:
        new_content = content  # Target string not found; no modification

    return new_content

def remove_speaker1(content):
    '''
    Speaker1 is the interviewer, their words shouldn't be in the final
    output.
    Find all elements from 
    <span class="speaker">Speaker 1 </span><span class="timecode">[00:00:18] </span> 
    to 
    <span class="speaker">Speaker 2 </span><span class="timecode">[00:01:02] </span>
    and remove them.
    Note: other logic strips out 'Speaker 1' etc etc. This fn just has to strip out
    the words between them.
    '''
    import io 
    new_content = ""
    buffer_file = io.StringIO(content) 
    keep_line = True

    # spin over all lines in the file, searching for 'Speaker 1', clear the keep_line 
    # flag until 'Speaker 2' appears. 
    # What happens if Speaker 1 is the last speaker, are there other items in the file 
    # that will be lost? Doesn't seem to matter, the text afterwards isn't required.
    
    # copy every line of 'content' and copy it into 'new_content' unless
    # it is Speaker 1
    for line in buffer_file:
        # search for any s & S version of speaker. Something do to with 
        # editor find and replace? Requested by Zoe.
        if "speaker,Speaker 1" in line or "speaker,speaker 1" in line:
            keep_line = False
        elif "speaker,Speaker" in line:
            keep_line = True 

        if keep_line:
            new_content += line 

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
        r'"> </span>': '">NULL</span>', # catch an empty span tag
        r'<span class="word" data-m="': ',',
        r'<span class="word highlight" data-m="': ',',
        r'" data-d="': ',',
        r'">' : ',',
        r', </span>': ',filename\n', # catch a word with trailing comma
        r'. </span>': ',filename\n', # catch a word with a full stop
        r'</span>' : ',filename\n',
        # Add as many pairs as needed
    }

    # Read the file content into memory
    with open(source, 'r', encoding='utf-8') as file:
        content = file.read()

    # store sound file name
    store_sound_file_name(content)

    # preprocess substitutions
    content = preprocess_substitutions(content)

    # remove header
    content = strip_out_header(content)

    # remove footer
    content = strip_out_footer(content)

    # add new header for csv parser
    content = add_new_header(content)

    # Perform all find-and-replace operations
    for old_text, new_text in replacements.items():
        content = content.replace(old_text, new_text)

    # remove all traces of zoe
    content = remove_speaker1(content)

    # # Step 8: strip out a couple of awkward lines that we don't need:
    # </p><p time="28030" data-tc="00:00:28,<span class="speaker,Speaker 1 ,20240112_1243.wav
    # <span class="timecode,[00:00:28] ,20240112_1243.wav
    #
    # Note: this leaves a blank lines in output. Does this matter?
    test = r'</p><p time="\d+" data-tc="\d+:\d+:\d+,<span class="speaker,Speaker \d+ ,filename'
    content = re.sub(test, '', content)
    test = r'<span class="timecode,\[\d+:\d+:\d+\] ,filename'
    content = re.sub(test, '',content) 

    # Step 9: Replace filename with soundfile, doesn't want to work in def?
    content = content.replace("filename",soundfile)

    # Step 10: Write the modified content back to the file
    with open(destination, 'w', encoding='utf-8') as file:
        file.write(content)



if __name__ == "__main__":
    
    if len(sys.argv) == 3:
        source = sys.argv[1]
        destination = sys.argv[2]

        process_file(source,destination)
