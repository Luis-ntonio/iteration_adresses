from get_coordinates import get_coordinates
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def validate_address(address: str, pais: str = 'Chile') -> str:
    address_parts = ' '.join(set(address.split('.')))
    address_parts = ' '.join(set(address_parts.split(',')))
    address_parts = ' '.join(set(address_parts.split()))
    address_parts = address_parts.replace('DE ', '').replace('AV ', '').replace('LA ', '').replace('  ', ' ').replace('LOS ', '')

    address_parts = address_parts.split(" ")
    iter = 3

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(4, iter, -1):
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
                    print(coords[0], coords[1], coords[2])
                    # Cancel remaining tasks
                    for future in futures:
                        future.cancel()
                    return coords[0], coords[1], coords[2]
            except Exception as e:
                continue  # Handle the exception, but don't stop processing other futures

    print("sin coincidencias")
    return None, None, None