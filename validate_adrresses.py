from get_coordinates import get_coordinates
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from tqdm import tqdm

def remove_duplicates_preserve_order(address, comuna):
    # Step 1: Clean and split the address
    address_parts = address.replace('.', ' ').replace(',', ' ').split("REFERENCIA")[0].split("CERCA ")[0].split("LLAMAR ")[0].split("FRENTE ")[0].split("AL LADO ")[0].split()

    unique_parts = [part for part in address_parts if part not in comuna]

    # Step 3: Create a single regex to handle all patterns at once
    patterns = [
        (r'\b[A-Z]+\s+[0-9]+', '_'),
        (r'\b[A-Z]+\s+DEL\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+DE LA\s+[A-Z]+', '_'),
        (r'\bLA\s+[A-Z]+', '_'),
        (r'\bLAS\s+[A-Z]+', '_'),
        (r'\bLOS\s+[A-Z]+', '_'),
        (r'\bEL\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+EL\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+CON\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+LOS\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+LA\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+LAS\s+[A-Z]+', '_'),
        (r'\b[A-Z]+\s+CASA\s+[A-Z]+', '_'),
        (r'PASAJE\s+[A-Z]+', '_'),
        (r'\bSAN\s+[A-Z]+', '_'),
        (r'\bPJE\s+[A-Z]+', '_')
    ]

    cleaned_address = ' '.join(unique_parts)

    for pattern, replacement in patterns:
        cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', replacement), cleaned_address)

    """# Clean up common keywords
    cleaned_address = cleaned_address.replace('DE ', '').replace('AV ', '').replace('SN ', '').replace('SN', '').replace('  ', ' ')"""
    return cleaned_address

OPT = {
    1: "P",
    2: "2",
    3: "3",
    4: "4",
    'N': "N",
}

def validate_address(address: str, comuna:str, pais: str = 'Chile') -> str:

    address_parts = address.split(" ")
    address_parts = [ad.replace("_", " ") for ad in address_parts]
    
    iter = len(address_parts) - 1
    dir = f'{" ".join(address_parts).lower()} {comuna.lower().replace("_", " ")}, {pais}'
    coords = get_coordinates(dir)

    if not isinstance(coords, Exception):
                return coords[0], coords[1], coords[2], OPT[1]


    for i in range(len(address_parts) - 1, iter, -1):
        val_addrs = combinations(address_parts, i)
        # Filter combinations with at least two consecutive words
        valid_combinations = [address_parts]

        for val_add in val_addrs:
            indices = [address_parts.index(word) for word in val_add if word in address_parts]

            if any(indices[i] + 1 == indices[i + 1] for i in range(len(indices) - 1)):
                valid_combinations.append(val_add)

        for val_add in valid_combinations:
            dir = f'{" ".join(val_add).lower()} {comuna.lower()}, {pais}'
            coords = get_coordinates(dir)

            if not isinstance(coords, Exception):
                return coords[0], coords[1], coords[2], OPT[len(address_parts) - i]

    print("sin coincidencias", address_parts, " ------ ", address, comuna.replace("_", " "))
    return None, None, None, OPT["N"]

    """with ThreadPoolExecutor(max_workers=1) as executor:
        futures = []

        for i in range(6, iter, -1):
            val_addrs = combinations(address_parts, i)
            # Filter combinations with at least two consecutive words
            valid_combinations = [address_parts]

            for val_add in val_addrs:
                indices = [address_parts.index(word) for word in val_add if word in address_parts]

                if any(indices[i] + 1 == indices[i + 1] for i in range(len(indices) - 1)):
                    valid_combinations.append(val_add)

            for val_add in valid_combinations:
                dir = f'{" ".join(val_add).lower()} {comuna.lower()}, {pais}'
                future = executor.submit(get_coordinates, dir)
                futures.append(future)

        # Process futures as they complete
        for future in as_completed(futures):
            try:
                coords = future.result()
                if not isinstance(coords, Exception):
                    print(address_parts, " ------ ", address, " ------- ", coords[0], "-----------", coords[3])
                    # Cancel remaining tasks
                    for future in futures:
                        future.cancel()
                    return coords[0], coords[1], coords[2], coords[3]
            except Exception as e:
                continue  # Handle the exception, but don't stop processing other futures"""

    print("sin coincidencias", address_parts, " ------ ", address, comuna)
    return None, None, None


print(validate_address("MARIA VELIZ ALCAYAGA VALLENAR ATACAMA CHILE VILLA", "Vallenar", "Chile"))