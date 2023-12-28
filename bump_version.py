import re

version_file_path = 'version.py'

with open(version_file_path, 'r') as file:
    version_content = file.read()

current_version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_content, re.M).group(1)

major, minor, patch = current_version.split('.')
patch = str(int(patch) + 1)  # Increment the patch version
new_version = f"{major}.{minor}.{patch}"

with open(version_file_path, 'w') as file:
    file.write(re.sub(r"(^__version__ = ['\"])([^'\"]*)(['\"])",
                      f"\\g<1>{new_version}\\3",
                      version_content, flags=re.M))

print(f"Version bumped to {new_version}")
