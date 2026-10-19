#!/usr/bin/env python3
"""addons.xml generator (Python 3).

Builds addons.xml from every add-on folder's addon.xml and writes addons.xml.md5.
Run from the root of the repository:  python3 addons_xml_generator.py
Only handles a single-depth folder structure (one folder per add-on).
"""

import hashlib
import os
import sys
import xml.dom.minidom


def collect_addons(root="."):
    """Return the addon.xml contents (without the XML declaration) for every add-on folder."""
    entries = []
    for name in sorted(os.listdir(root), key=str.lower):
        path = os.path.join(root, name)
        if not os.path.isdir(path) or name.startswith("."):
            continue
        addon_xml = os.path.join(path, "addon.xml")
        if not os.path.isfile(addon_xml):
            print(f"Skipping {name}: no addon.xml")
            continue
        try:
            with open(addon_xml, "r", encoding="utf-8") as f:
                text = f.read()
            xml.dom.minidom.parseString(text.encode("utf-8"))  # fail early on malformed XML
        except Exception as e:  # missing or poorly formatted addon.xml
            print(f"Excluding {addon_xml}: {e}")
            continue
        lines = [line.rstrip() for line in text.splitlines() if "<?xml" not in line]
        entries.append("\n".join(lines).strip())
    return entries


def main():
    entries = collect_addons()
    addons_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
        + "\n\n".join(entries)
        + "\n</addons>\n"
    )
    data = addons_xml.encode("utf-8")
    with open("addons.xml", "wb") as f:
        f.write(data)
    with open("addons.xml.md5", "w", encoding="ascii") as f:
        f.write(hashlib.md5(data).hexdigest())
    print(f"Finished updating addons.xml ({len(entries)} add-ons) and addons.xml.md5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
