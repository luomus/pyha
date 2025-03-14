import json
import string


def get_escaped_terms_for_case_insensitive_json_field_search(term):
    """
        Get escaped search terms for case-insensitive search from json fields

        :param term: search term
        :return: list of search terms where special characters are escaped (the terms contain both lowercase and uppercase versions)
    """
    term = term.lower()
    special_chars = []

    for char in term:
        if char not in string.ascii_letters:
            if char not in special_chars:
                special_chars.append(char)

    return _get_escaped_terms_for_chars([term], special_chars)


def _get_escaped_terms_for_chars(terms, special_chars):
    """
        Escapes the given special characters in the search terms

        :param terms: list of search terms, should be in lower case
        :param special_chars: list of special characters that should be escaped
        :return: list of search terms where the character is escaped
    """
    if len(special_chars) == 0:
        return terms

    char = special_chars.pop(0)
    result = []

    for term in terms:
        result += _get_escaped_terms_for_char(term, char)

    return _get_escaped_terms_for_chars(result, special_chars)


def _get_escaped_terms_for_char(term, char_to_escape):
    """
        Escapes the given character in the search term

        :param term: search term, should be in lower case
        :param char_to_escape: character, should be in lower case
        :return: list of search terms where the character is escaped
    """
    if len(term) == 0:
        return ['']

    char = term[0]

    encoded_terms_for_char = []
    if char == char_to_escape:
        encoded_terms_for_char.append(json.dumps(char)[1:-1])
        if char != char.upper():
            encoded_terms_for_char.append(json.dumps(char.upper())[1:-1])
    else:
        encoded_terms_for_char.append(char)

    result_from_next_char = _get_escaped_terms_for_char(term[1:], char_to_escape)

    result = []

    for encoded_term in encoded_terms_for_char:
        for res in result_from_next_char:
            result.append(encoded_term + res)

    return result
