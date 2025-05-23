# nlp_utils.py
def get_redact_entities(text, nlp_model):
    doc = nlp_model(text)
    redact_entities = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "DATE", "ORG", "GPE", "EMAIL", "PHONE"]:
            redact_entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char
            })
    return redact_entities
