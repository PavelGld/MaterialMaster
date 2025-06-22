#!/usr/bin/env python3
"""
Simple script to compile .po files to .mo files without requiring msgfmt
"""

import os
import struct
from typing import Dict, Tuple


def parse_po_file(po_path: str) -> Dict[str, str]:
    """Parse a .po file and return a dictionary of msgid -> msgstr mappings."""
    messages = {}
    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False
    
    with open(po_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('msgid '):
                if current_msgid is not None and current_msgstr is not None:
                    messages[current_msgid] = current_msgstr
                current_msgid = line[6:].strip('"')
                current_msgstr = None
                in_msgid = True
                in_msgstr = False
                
            elif line.startswith('msgstr '):
                current_msgstr = line[7:].strip('"')
                in_msgid = False
                in_msgstr = True
                
            elif line.startswith('"') and line.endswith('"'):
                content = line[1:-1]
                if in_msgid and current_msgid is not None:
                    current_msgid += content
                elif in_msgstr and current_msgstr is not None:
                    current_msgstr += content
    
    # Add the last entry
    if current_msgid is not None and current_msgstr is not None:
        messages[current_msgid] = current_msgstr
    
    return messages


def create_mo_file(messages: Dict[str, str], mo_path: str) -> None:
    """Create a .mo file from message dictionary."""
    # Filter out empty msgids and msgstrs
    filtered_messages = {k: v for k, v in messages.items() if k and v}
    
    # Prepare data
    keys = []
    values = []
    
    for msgid, msgstr in filtered_messages.items():
        # Ensure proper UTF-8 encoding
        key_bytes = msgid.encode('utf-8')
        value_bytes = msgstr.encode('utf-8')
        keys.append(key_bytes)
        values.append(value_bytes)
    
    # Calculate offsets
    key_offsets = []
    value_offsets = []
    key_start = 7 * 4 + 16 * len(keys)
    value_start = key_start + sum(len(k) + 1 for k in keys)
    
    current_offset = key_start
    for key in keys:
        key_offsets.append((len(key), current_offset))
        current_offset += len(key) + 1
    
    current_offset = value_start
    for value in values:
        value_offsets.append((len(value), current_offset))
        current_offset += len(value) + 1
    
    # Write MO file
    with open(mo_path, 'wb') as f:
        # Magic number
        f.write(struct.pack('<I', 0x950412de))
        # Version
        f.write(struct.pack('<I', 0))
        # Number of entries
        f.write(struct.pack('<I', len(keys)))
        # Offset of key table
        f.write(struct.pack('<I', 7 * 4))
        # Offset of value table
        f.write(struct.pack('<I', 7 * 4 + 8 * len(keys)))
        # Hash table size (0 = no hash table)
        f.write(struct.pack('<I', 0))
        # Hash table offset
        f.write(struct.pack('<I', 0))
        
        # Write key table
        for length, offset in key_offsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write value table
        for length, offset in value_offsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write keys
        for key in keys:
            f.write(key)
            f.write(b'\x00')
        
        # Write values
        for value in values:
            f.write(value)
            f.write(b'\x00')


def compile_po_to_mo(po_path: str, mo_path: str) -> None:
    """Compile a .po file to .mo file."""
    print(f"Compiling {po_path} -> {mo_path}")
    messages = parse_po_file(po_path)
    create_mo_file(messages, mo_path)
    print(f"Created {mo_path} with {len(messages)} messages")


if __name__ == "__main__":
    # Compile English translations
    compile_po_to_mo(
        "translations/en/LC_MESSAGES/messages.po",
        "translations/en/LC_MESSAGES/messages.mo"
    )
    
    # Compile Russian translations
    compile_po_to_mo(
        "translations/ru/LC_MESSAGES/messages.po", 
        "translations/ru/LC_MESSAGES/messages.mo"
    )
    
    print("Translation compilation complete!")