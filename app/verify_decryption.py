import os
from scs_search import perform_search, decrypt_and_save

keyword = "test"
matches = perform_search(keyword)

if matches:
    print(f"Found {len(matches)} matches.")
    selected = matches[0]
    print(f"Decrypting {selected['original']}...")
    result_path = decrypt_and_save(selected)
    if result_path:
        print(f"Success! Restored to: {result_path}")
        with open(result_path, 'r') as f:
            print(f"Content: {f.read()}")
    else:
        print("Decryption failed.")
else:
    print("No matches found.")
