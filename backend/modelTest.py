import re
import spacy

# Load spaCy's small English model
nlp = spacy.load("en_core_web_sm")

# Define custom regex patterns for redaction
regex_patterns = {
    'EMAIL': r'\b[\w.-]+?@\w+?\.\w+?\b',
    'PHONE': r'\b(?:\+?\d{1,3})?[\s.-]?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b',
    'CREDIT_CARD': r'\b(?:\d[ -]*?){13,16}\b'
}

# Function to redact sensitive information
def redact_text(text):
    doc = nlp(text)

    # Redact named entities (e.g., PERSON, DATE)
    redacted_text = text
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'GPE', 'DATE', 'ORG']:
            redacted_text = redacted_text.replace(ent.text, f"[REDACTED_{ent.label_}]")

    # Redact custom regex patterns
    for label, pattern in regex_patterns.items():
        redacted_text = re.sub(pattern, f"[REDACTED_{label}]", redacted_text)

    return redacted_text

# Example input text
input_text = """
John Smith sent an email to jane.doe@example.com on January 5, 2024.
His phone number is (123) 456-7890 and his credit card is 4111 1111 1111 1111.
He lives in New York and works at Acme Corp.
"""

# Run redaction
output = redact_text(input_text)
print("Redacted Text:\n", output)
