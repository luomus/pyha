import json
import re
import string


def get_encoded_term_for_json_field_regex_search(term):
    """
        Get search term for case-insensitive regex search from json fields

        :param term: search term
        :return: search term where the special characters have been replaced with their encoded versions
    """
    new_term = term.lower()

    special_chars = set([char for char in new_term if char not in string.ascii_letters])

    for char in special_chars:
        encoded_terms = [json.dumps(char)[1:-1]]
        if char != char.upper():
            encoded_terms.append(json.dumps(char.upper())[1:-1])

        escaped_encoded_terms = [re.escape(term) for term in encoded_terms]

        new_term = new_term.replace(char, '({})'.format('|'.join(escaped_encoded_terms)))

    return new_term
