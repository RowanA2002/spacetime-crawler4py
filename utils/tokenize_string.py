from typing import List
from io import StringIO
import re


def tokenize(s: str) -> List[str]:
        """
        Reads in a string and returns a list of the tokens in that string
        """
        tokens= []
        with StringIO(s) as stream:  # replaces characters that fail decoding with a valid char
            current_token = ''
            #  O(n) for n chars in the string
            while True:
                char = ''
                try:  # catch any decoding errors
                    char = stream.read(1)
                except:
                    continue
                
                if re.match("[a-zA-Z0-9]", char):
                    current_token += char.lower()
                else:  # encountered a delimeter character
                    if len(current_token) > 0:
                        tokens.append(current_token)
                        current_token = ''
                    if len(char) == 0:
                        break
        return tokens