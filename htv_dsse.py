from secretsharing import PlaintextToHexSecretSharer as SecretSharer

class HTV_DSSE:
    def __init__(self, master_db_key):
        self.master_db_key = master_db_key
        # Lists to store our generated locked shares
        self.admin_user_shares = []
        self.engineering_user_shares = []
        
    def lock_tree(self):
        print("\n[SYSTEM] Initializing HTV-DSSE Top-Down Encryption...")
        
        # LEVEL 0: ROOT (Requires 2 out of 2 Departments to unlock)
        # We split the Master DB Key into 2 department shares.
        dept_shares = SecretSharer.split_secret(self.master_db_key, 2, 2)
        admin_dept_key = dept_shares[0]
        eng_dept_key = dept_shares[1]
        print("  [+] Master Key split into Admin and Engineering intermediate keys.")

        # LEVEL 1: DEPARTMENTS TO USERS
        
        # Admin Dept: Requires 1 out of 2 Admins (OR Gate)
        # SSS needs hex strings, so we strip the '1-' prefix the library adds for the sub-split
        raw_admin_key = admin_dept_key.split('-')[1] 
        self.admin_user_shares = SecretSharer.split_secret(raw_admin_key, 1, 2)
        
        # Engineering Dept: Requires 3 out of 5 Engineers
        raw_eng_key = eng_dept_key.split('-')[1]
        self.engineering_user_shares = SecretSharer.split_secret(raw_eng_key, 3, 5)

        print("  [+] User shares generated.")
        print("  [+] Tree is LOCKED.\n")

    def unlock_tree(self, submitted_admin_shares, submitted_eng_shares):
        print("--- SIMULATING AUTHORIZED SEARCH REQUEST ---")
        
        # STEP 1: RECONSTRUCT DEPARTMENTS
        try:
            # Reconstruct Admin (Needs 1)
            recovered_admin_raw = SecretSharer.recover_secret(submitted_admin_shares)
            # Re-attach the SSS index prefix we stripped earlier
            recovered_admin_dept = "1-" + recovered_admin_raw 
            print("  [+] Admin Department Key reconstructed.")

            # Reconstruct Engineering (Needs 3)
            recovered_eng_raw = SecretSharer.recover_secret(submitted_eng_shares)
            recovered_eng_dept = "2-" + recovered_eng_raw
            print("  [+] Engineering Department Key reconstructed.")

        except Exception:
            print("  [-] Threshold not met for a department. Reconstruction failed.")
            return False

        # STEP 2: RECONSTRUCT ROOT MASTER KEY
        try:
            final_shares = [recovered_admin_dept, recovered_eng_dept]
            recovered_master_key = SecretSharer.recover_secret(final_shares)
            print(f"  [+] ROOT MASTER KEY DECRYPTED: {recovered_master_key}")
            return True
        except Exception:
            print("  [-] Failed to reconstruct Root Key.")
            return False


# ---------------------------------------------------------
# EXECUTION DEMO
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Setup the system
    system = HTV_DSSE("REAL_AES256_DB_TRAPDOOR")
    system.lock_tree()

    # 2. SUCCESSFUL SCENARIO: 1 Admin and 3 Engineers submit valid shares
    print("\n>>> TEST 1: Valid Threshold <<<")
    valid_admins = system.admin_user_shares[0:1] # Get 1 admin
    valid_engs = system.engineering_user_shares[0:3] # Get 3 engineers
    system.unlock_tree(valid_admins, valid_engs)

    # 3. FAILURE SCENARIO: Not enough engineers (Only 2)
    print("\n>>> TEST 2: Invalid Threshold (Only 2 Engineers) <<<")
    invalid_engs = system.engineering_user_shares[0:2] # Get only 2 engineers
    system.unlock_tree(valid_admins, invalid_engs)
