#!/usr/bin/env python3
"""addons.xml generator (Python 3).

Builds addons.xml + addons.xml.md5 for the repository root and for every
Kodi-version folder listed in VERSION_DIRS (each one is a separate <dir> in
repository.nic/addon.xml). Run from the root of the repository:

    python3 addons_xml_generator.py

Each folder holds one sub-folder per add-on containing its addon.xml.
"""

import hashlib
import os
import sys
import xml.dom.minidom

# Kodi-version folders; keep in sync with the <dir> entries in repository.nic/addon.xml
VERSION_DIRS = ["piers"]  # Kodi 22


def collect_addons(root, skip=()):
    """Return the addon.xml contents (without the XML declaration) for every add-on folder in root."""
    entries = []
    for name in sorted(os.listdir(root), key=str.lower):
        path = os.path.join(root, name)
        if not os.path.isdir(path) or name.startswith(".") or name in skip:
            continue
        addon_xml = os.path.join(path, "addon.xml")
        if not os.path.isfile(addon_xml):
            print(f"Skipping {path}: no addon.xml")
            continue
        try:
            with open(addon_xml, "r", encoding="utf-8-sig") as f:
                text = f.read()
            xml.dom.minidom.parseString(text.encode("utf-8"))  # fail early on malformed XML
        except Exception as e:  # missing or poorly formatted addon.xml
            print(f"Excluding {addon_xml}: {e}")
            continue
        lines = [line.rstrip() for line in text.splitlines() if "<?xml" not in line]
        entries.append("\n".join(lines).strip())
    return entries


def write_index(root, skip=()):
    entries = collect_addons(root, skip)
    addons_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
        + "\n\n".join(entries)
        + "\n</addons>\n"
    )
    data = addons_xml.encode("utf-8")
    with open(os.path.join(root, "addons.xml"), "wb") as f:
        f.write(data)
    with open(os.path.join(root, "addons.xml.md5"), "w", encoding="ascii") as f:
        f.write(hashlib.md5(data).hexdigest())
    print(f"{root}/addons.xml: {len(entries)} add-ons")


def main():
    write_index(".", skip=VERSION_DIRS)
    for d in VERSION_DIRS:
        write_index(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
