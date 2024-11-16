from get_coordinates import get_coordinates
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def remove_duplicates_preserve_order(address):
    # Step 1: Clean and split the address
    address_parts = address.replace('.', ' ').replace(',', ' ').split("REFERENCIA")[0].split("CERCA ")[0].split("LLAMAR ")[0].split("FRENTE ")[0].split("AL LADO ")[0].split()

    # Step 2: Remove duplicates while preserving order
    seen = set()
    unique_parts = [part for part in address_parts if part not in seen and not seen.add(part)]

    # Step 3: Create a single regex to handle all patterns at once
    patterns = [
        (r'\b[A-Z]+\s+DEL\s+[A-Z]+\b', '_'),
        (r'\b[A-Z]+\s+DE LA\s+[A-Z]+\b', '_'),
        (r'\bLA\s+[A-Z]+\b', '_'),
        (r'\bLAS\s+[A-Z]+\b', '_'),
        (r'\bLOS\s+[A-Z]+\b', '_'),
        (r'\bEL\s+[A-Z]+\b', '_'),
        (r'PJE\s+[0-9]+\b', '_'),
        (r'PASAJE\s+[0-9]+\b', '_'),
        (r'PASAJE\s+[A-Z]+\b', '_'),
        (r'\bSAN\s+[A-Z]+\b', '_'),
        (r'\bPJE\s+[A-Z]+\b', '_'),
        (r'\bB\s+[0-9]+\b', '_'),
        (r'\bCASA\s+[0-9]+\b', '_'),
        (r'\bN\s+[0-9]+\b', '_'),
        (r'\bSECTOR\s+[0-9]+\b', '_')
    ]

    cleaned_address = ' '.join(unique_parts)
    for pattern, replacement in patterns:
        cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', replacement), cleaned_address)

    # Clean up common keywords
    cleaned_address = cleaned_address.replace('DE ', '').replace('AV ', '').replace('SN ', '').replace('SN', '').replace('  ', ' ')
    return cleaned_address

def validate_address(address: str, pais: str = 'Chile') -> str:
    address_parts = address.split(" ")
    address_parts = [ad.replace("_", " ") for ad in address_parts]
    iter = 2

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        for i in range(5, iter, -1):
            val_addrs = combinations(address_parts, i)
            
            # Filter combinations with at least two consecutive words
            valid_combinations = [
                val_add for val_add in val_addrs
                if has_consecutive_words(val_add, address_parts)
            ]

            # Submit the filtered combinations asynchronously to the ThreadPoolExecutor
            for val_add in valid_combinations:
                future = executor.submit(get_coordinates, f'{" ".join(val_add)}, {pais}')
                futures.append(future)

        # Process futures as they complete
        for future in as_completed(futures):
            try:
                coords = future.result()
                if not isinstance(coords, Exception):
                    print(address_parts, " ------ ", address, " ------- ", coords[0])
                    # Cancel remaining tasks
                    for future in futures:
                        future.cancel()
                    return coords[0], coords[1], coords[2]
            except Exception as e:
                continue  # Handle the exception, but don't stop processing other futures

    print("sin coincidencias", address_parts, " ------ ", address)
    return None, None, None


def has_consecutive_words(combination, original_parts):
    """
    Check if a combination contains at least two consecutive words from the original address parts.
    """
    indices = [original_parts.index(word) for word in combination if word in original_parts]
    return any(indices[i] + 1 == indices[i + 1] for i in range(len(indices) - 1))