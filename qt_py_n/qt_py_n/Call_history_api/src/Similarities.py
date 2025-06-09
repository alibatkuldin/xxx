from typing import List

def group_similar_values_across_sources(calls: List[dict]):
    """
    Groups call objects by each shared key-value pair (ignoring 'app', 'type', and 'source'),
    but only if that pair is present in objects coming from at least two different sources.
    
    Returns a list of dictionaries each with keys:
        - 'field': the field name
        - 'value': the common value
        - 'objects': the list of call objects (each with its source) sharing that key-value pair.
    """
    skip_keys = {"app", "type", "source"}
    groups = {}

    for call in calls:
        for key, value in call.items():
            if key in skip_keys:
                continue
            group_key = (key, value)
            groups.setdefault(group_key, []).append(call)

    result = []
    for (field, value), group_calls in groups.items():
        sources = {call["source"] for call in group_calls}
        if len(sources) > 1:
            result.append({
                "field": field,
                "value": value,
                "objects": group_calls
            })
    return result