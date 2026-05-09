import os
import random

# A large Mersenne prime for Shamir's Secret Sharing over a finite field
PRIME = 2**521 - 1

# ---------------------------------------------------------
# CORE SHAMIR'S SECRET SHARING MATH
# ---------------------------------------------------------

def _eval_at(poly, x, prime):
    accum = 0
    for coeff in reversed(poly):
        accum = (accum * x + coeff) % prime
    return accum

def _extended_gcd(a, b):
    x = 0; last_x = 1
    y = 1; last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def _divmod(num, den, p):
    inv, _ = _extended_gcd(den, p)
    return num * inv

def _lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"
    def PI(vals):
        accum = 1
        for v in vals: accum *= v
        return accum
    nums = []
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod(nums[i] * den * y_s[i] % p, dens[i], p) for i in range(k)])
    return (_divmod(num, den, p) + p) % p

def split_secret(secret_int, threshold, num_shares):
    if threshold > num_shares:
        raise ValueError("Threshold must be <= num_shares")
    # For threshold 1, polynomial is just the secret (degree 0)
    poly = [secret_int] + [random.randint(1, PRIME - 1) for _ in range(threshold - 1)]
    shares = []
    for i in range(1, num_shares + 1):
        shares.append((i, _eval_at(poly, i, PRIME)))
    return shares

def recover_secret(shares):
    if not shares:
        raise ValueError("Need at least one share")
    x_s, y_s = zip(*shares)
    return _lagrange_interpolate(0, x_s, y_s, PRIME)

# ---------------------------------------------------------
# HIERARCHICAL SECRET SHARING SYSTEM
# ---------------------------------------------------------

def str_to_int(s):
    return int.from_bytes(s.encode('utf-8'), 'big')

def int_to_str(i):
    return i.to_bytes((i.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')

def lock_hierarchical_tree(secret_string, hierarchy_config):
    """
    Splits a secret top-down through a hierarchical tree.
    """
    secret_int = str_to_int(secret_string)
    
    num_depts = len(hierarchy_config['departments'])
    root_threshold = hierarchy_config['root_threshold']
    
    # 1. Split the Root Master Key into Department Keys
    dept_shares = split_secret(secret_int, root_threshold, num_depts)
    
    all_user_shares = {}
    
    # 2. Split each Department Key into User Shares
    for i, dept in enumerate(hierarchy_config['departments']):
        dept_key_int = dept_shares[i][1]
        user_shares = split_secret(dept_key_int, dept['threshold'], dept['num_users'])
        all_user_shares[dept['name']] = user_shares
        
    return all_user_shares

def unlock_hierarchical_tree(submitted_shares, hierarchy_config):
    """
    Reconstructs the secret bottom-up through the hierarchical tree.
    """
    recovered_dept_shares = []
    
    # 1. Try to reconstruct each department's key
    for i, dept in enumerate(hierarchy_config['departments']):
        name = dept['name']
        if name in submitted_shares and len(submitted_shares[name]) >= dept['threshold']:
            dept_key_int = recover_secret(submitted_shares[name])
            recovered_dept_shares.append((i + 1, dept_key_int)) # i+1 because dept shares were 1-indexed
            print(f"[+] Successfully reconstructed {name} Department Key.")
        else:
            print(f"[-] Failed to reconstruct {name} Department Key (not enough valid shares).")
            
    # 2. Try to reconstruct the Root Master Key using the recovered Department Keys
    if len(recovered_dept_shares) >= hierarchy_config['root_threshold']:
        root_key_int = recover_secret(recovered_dept_shares)
        return int_to_str(root_key_int)
    else:
        raise ValueError("Not enough department thresholds met to unlock root key.")

# ---------------------------------------------------------
# EXECUTION DEMO
# ---------------------------------------------------------
if __name__ == '__main__':
    MASTER_SECRET = "REAL_AES256_DB_TRAPDOOR"
    
    config = {
        'root_threshold': 2, # Need 2 departments
        'departments': [
            {'name': 'Admin', 'threshold': 1, 'num_users': 2}, # Need 1 out of 2 admins
            {'name': 'Engineering', 'threshold': 3, 'num_users': 5} # Need 3 out of 5 engineers
        ]
    }
    
    print(f"Original Master Key: {MASTER_SECRET}")
    print("\n[SYSTEM] Locking tree...")
    shares = lock_hierarchical_tree(MASTER_SECRET, config)
    print("Tree LOCKED. User shares distributed.")
    
    print("\n--- TEST 1: Valid Threshold (1 Admin, 3 Engineers) ---")
    valid_submit = {
        'Admin': shares['Admin'][0:1], 
        'Engineering': shares['Engineering'][0:3]
    }
    recovered = unlock_hierarchical_tree(valid_submit, config)
    print(f"[SUCCESS] ROOT MASTER KEY DECRYPTED: {recovered}")
    
    print("\n--- TEST 2: Invalid Threshold (1 Admin, only 2 Engineers) ---")
    invalid_submit = {
        'Admin': shares['Admin'][0:1], 
        'Engineering': shares['Engineering'][0:2]
    }
    try:
        recovered = unlock_hierarchical_tree(invalid_submit, config)
        print(f"[SUCCESS] ROOT MASTER KEY DECRYPTED: {recovered}")
    except Exception as e:
        print(f"[FAILURE] Could not reconstruct tree: {e}")
