import re
from markupsafe import escape


PROHIBITED_WORDS = ['nigger', 'kike', 'jew', 'faggot', 'pussy', 'cunt', 'chink', 'reallybadword']


def clean_message(message):
    # Escaping HTML to prevent XSS attacks
    #message = escape(message)

    # Lowercasing the message for case-insensitive comparison
    lowercased_message = message.lower()

    # Replacing prohibited words
    for word in PROHIBITED_WORDS:
        # Create a pattern that matches the word
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        # Find all matches of the prohibited word in the message
        matches = pattern.findall(lowercased_message)
        for match in matches:
            # Generate a string of asterisks with the same length as the match
            replacement = "*" * len(match)
            # Replace the word in the original message (preserving the original case)
            message = re.sub(re.escape(match), replacement, message, flags=re.IGNORECASE)

    # Trimming whitespace
    message = message.strip()

    # Add further sanitizations as needed...

    return message