def load_data(file_path: str) -> list[str | tuple[str]]:
    with open(file_path, 'r') as file:
        data = file.read().splitlines()
        data = [line for line in data if line != '']
        for i in range(len(data)):
            if "|" in data[i]:
                data[i] = tuple(data[i].split('|'))
    return data
