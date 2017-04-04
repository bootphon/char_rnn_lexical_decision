"""
Surrounds every word by a space. The ouput is a corpus with a similar 
information but with the space as a unique delimitor character.
Any further preprocessing of the corpus (special characters, blank lines...) 
should be done here.
The corpus is truncated here (for now).
"""
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='input_path', help='path to the input corpus')
parser.add_argument('-o', dest='output_path', help='path to the cleaned corpus')
parser.add_argument('-s', dest='size', type=int, default=0, help='truncates the corpus after the desired number of characters (after the next space) - 0 value will keep the entire corpus') 
args = parser.parse_args()

with open(args.input_path) as f:
    input_text = f.read()

#search for the next space to split the corpus
if args.size != 0:
    i = args.size
    while input_text[i] != ' ':
        i += 1
    output_text = input_text[:i]

output_text = output_text.lower() 
output_text = re.sub(r'(\w[\S\w]*\w)', r' \1 ', output_text) #surround every word by a space
output_text = re.sub(r'(\n)', r' \1 ', output_text) #surround every newline by a space
output_text = re.sub(r' +', ' ', output_text)

with open(args.output_path, 'w+') as f:
    f.write(output_text)
