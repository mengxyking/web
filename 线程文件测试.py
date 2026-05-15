import random

data = {
    'CeiJJt73V': {'url': 'https://v.douyin.com/CeiJJt73V/', 'BIG_COUNT': '1555', 'TONGJI': '114441'},
    'Ceio71Xm': {'url': ' https://v.douyin.com/Ceio71Xm/', 'BIG_COUNT': '1555', 'TONGJI': '244400'},
    'CeioEpMe': {'url': 'https://v.douyin.com/CeioEpMe/', 'BIG_COUNT': '1555', 'TONGJI': '204446'},
    'CeioKu93': {'url': 'https://v.douyin.com/CeioKu93/', 'BIG_COUNT': '1555', 'TONGJI': '104440'},
    'iDPKSMAy': {'url': 'https://v.douyin.com/iDPKSMAy/', 'BIG_COUNT': '1555', 'TONGJI': '15444441'}
}


def get_random_valid_entry(data):
    # Convert string values of BIG_COUNT and TONGJI to integers for comparison
    def convert_to_int(entry):
        entry['BIG_COUNT'] = int(entry['BIG_COUNT'])
        entry['TONGJI'] = int(entry['TONGJI'])
        return entry

    # Make a copy of the data with integers for comparison
    converted_data = {key: convert_to_int(value) for key, value in data.items()}

    # Attempt to find a valid entry
    while converted_data:
        # Randomly select a key from the dictionary
        random_key = random.choice(list(converted_data.keys()))
        random_entry = converted_data[random_key]

        # Check if TONGJI is less than or equal to BIG_COUNT
        if random_entry['TONGJI'] <= random_entry['BIG_COUNT']:
            return {random_key:random_entry}

        # If not, remove this entry from the dictionary
        del converted_data[random_key]

    # If no valid entry is found, return False
    return False


# Test the function
result = get_random_valid_entry(data)
print(result)