from get_coordinates import get_coordinates
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def remove_duplicates_preserve_order(address):
    # Step 1: Split the address into words and preserve the original order
    address_parts = address.replace('.', ' ').replace(',', ' ').split("REFERENCIA")[0].split("CERCA ")[0].split()

    # Step 2: Remove duplicates while preserving order
    seen = set()
    unique_parts = []
    for part in address_parts:
        if part not in seen:
            seen.add(part)
            unique_parts.append(part)

    # Step 3: Join the parts back into a string and replace unwanted words
    cleaned_address = ' '.join(unique_parts)
    
    pattern=r'\b[A-Z]+\s+DEL\s+[A-Z]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    pattern=r'\b[A-Z]+\s+LA\s+[A-Z]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    pattern=r'\bLOS\s+[A-Z]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    pattern=r'\bEL\s+[A-Z]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    pattern=r'PJE\s+[0-9]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    pattern=r'PASAJE\s+[0-9]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    pattern=r'\bSAN\s+[A-Z]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    pattern=r'\bB\s+[0-9]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    pattern=r'\bCASA\s+[0-9]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    pattern=r'\bN\s+[0-9]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    pattern=r'\bSECTOR\s+[0-9]+\b'
    cleaned_address = re.sub(pattern, lambda m: m.group(0).replace(' ', '_'), cleaned_address)
    
    cleaned_address = (cleaned_address.replace('DE ', '')
                                      .replace('AV ', '')
                                      .replace('SN ', '')
                                      .replace('SN', '')
                                      .replace('  ', ' '))  # Ensure no double spaces

    return cleaned_address

def validate_address(address: str, pais: str = 'Chile') -> str:
    address_parts = remove_duplicates_preserve_order(address)

    address_parts = address_parts.split(" ")
    for i, ad in enumerate(address_parts):
        address_parts[i] = ad.replace("_", " ")
    iter = 3 if len(address_parts) > 3 else 2 

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(5, iter, -1):
            val_addrs = combinations(address_parts, i)
            # Submit the combinations asynchronously to the ThreadPoolExecutor
            for val_add in val_addrs:
                future = executor.submit(get_coordinates, f'{" ".join(val_add)}, {pais}')
                futures.append(future)

        # Process futures as they complete
        for future in as_completed(futures):
            try:
                coords = future.result()
                if not isinstance(coords, Exception):
                    print(address_parts, " ------ ", address, " ------- ", coords[0])
                    #print(coords[0], coords[1], coords[2])
                    # Cancel remaining tasks
                    for future in futures:
                        future.cancel()
                    return coords[0], coords[1], coords[2]
            except Exception as e:
                continue  # Handle the exception, but don't stop processing other futures

    print("sin coincidencias", address_parts, " ------ ", address)
    return None, None, None