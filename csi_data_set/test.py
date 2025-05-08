import os

folder_path = r'C:\Users\ROG\Desktop\data_set_new1'

for filename in os.listdir(folder_path):
    old_path = os.path.join(folder_path, filename)
    if not os.path.isfile(old_path):
        continue
    if filename.startswith("6-"):
        new_name = "5-" + filename[2:]
    else:
        continue

    new_path = os.path.join(folder_path, new_name)
    os.rename(old_path, new_path)
    print(f"Renamed: {filename} -> {new_name}")