from get_coordinates import get_coordinates
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

def validate_address(address: str, pais: str = 'Chile') -> str:
    address_parts = address.split(" ")

    def get_validated_coordinates(val_add):
        try:
            coords = get_coordinates(f'{" ".join(val_add)} {pais}')
            time.sleep(1.5)
            if coords:
                return " ".join(val_add), *coords
            else:
                return None, None, None
        except Exception as e:
            print(f"Error retrieving coordinates for {' '.join(val_add)}: {e}")
            return None, None, None

    with ThreadPoolExecutor() as executor:
        futures = []
        # Submit tasks to the thread pool for combinations
        for i in range(len(address_parts) - 3):
            val_addrs = combinations(address_parts, len(address_parts) - i)
            for val_add in val_addrs:
                futures.append(executor.submit(get_validated_coordinates, val_add))
        
        # Iterate over futures as they complete
        for future in tqdm(as_completed(futures), total=len(futures)):
            result = future.result()
            if result[1] is not None:  # if valid coordinates are found
                return result

    return None, None, None

