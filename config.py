"""
OVERTHRONE :: config.py
Grid map configurations and constants.
"""

STARTING_HP = 5000
STARTING_AP = 1200
EPOCH_DURATION_SECS = 300  # 5 minutes
ATTACK_COST_AP = 500
TASK_FAIL_CHANCE = 0.15

# Color Palettes
TEAM_PALETTE = [
    {"color": "#0099FF", "bg": "#001933", "icon": "🔵"},
    {"color": "#FF2244", "bg": "#330011", "icon": "🔴"},
    {"color": "#00CC88", "bg": "#003322", "icon": "🟢"},
    {"color": "#FFB800", "bg": "#332500", "icon": "🟡"},
    {"color": "#CC44FF", "bg": "#220033", "icon": "🟣"},
    {"color": "#FF8800", "bg": "#331100", "icon": "🟠"},
]

CELL_COLORS = {
    "ALPHA": "#0a2040", "CRIMSON": "#2a0a0a", "VERDANT": "#0a2a12", "AURUM": "#2a1a00", 
    "NONE": "#0a1a0e" # default free
}
CELL_GLOW = {
    "ALPHA": "#0099FF", "CRIMSON": "#FF2244", "VERDANT": "#00CC88", "AURUM": "#FFB800",
    "NONE": "transparent"
}

# PUBG-style terrain special cells
TERRAIN_SPECIAL = {15: "🪂", 44: "💊", 55: "🔫", 33: "🏥", 66: "💣"}

TASKS = {
    "monarch": [
        # ─ EASY (10) ─
        {"id":"h1","title":"Historian's Message","diff":"EASY","pts":500,"desc":"A historian left behind a message, but spacing and punctuation were erased by time: Qlk_vhgl_vw_ylvlel. Can you restore its meaning?"},
        {"id":"h2","title":"Ancient Broadcast","diff":"EASY","pts":500,"desc":"This broadcast was captured decades ago. The voice is distorted, the message unclear—but patterns remain. Download the audio file to decode it.","link":"https://drive.google.com/file/d/1OUG1uTlha1qPLVE3uS4v9Z2fz9mMck0i/view?usp=sharing"},
        {"id":"h3","title":"Hex Color Code","diff":"EASY","pts":500,"desc":"Hex codes are divided into three pairs: RR (Red), GG (Green), BB (Blue). Values range from 00 to FF. Which color is #0502FA?"},
        {"id":"h4","title":"Secret Cipher","diff":"EASY","pts":500,"desc":"A simple encryption shifts every letter forward by 1 in the alphabet (A→B, B→C, ..., Z→A). Example: HAL→IBM. Encrypt: CAT"},
        {"id":"h5","title":"Broken Transmission","diff":"EASY","pts":500,"desc":"An old agent encoded a secret phrase before going dark with a shift of 3 steps forward. Decrypt: Eudnh_wkh_frgh_iluvw. Recover the original message."},
        {"id":"h6","title":"Binary Message","diff":"EASY","pts":500,"desc":"A rookie analyst intercepted machine noise—it's just binary. Each group of 8 bits is one ASCII character. Convert: 01101100 01101111 01100111 01101001 01101110 01011111 01101110 01101111 01110111. What does it say?"},
        {"id":"h7","title":"XOR Mystery","diff":"EASY","pts":500,"desc":"Find the XOR of all numbers from 1 to 10. (XOR: 1 XOR 2 XOR 3 ... XOR 10 = ?)"},
        {"id":"h8","title":"String Collapse","diff":"EASY","pts":500,"desc":"Given string: ttiiiiieeeeiieett. Repeatedly remove any group of ≥3 consecutive characters. After removal, collapse and continue. Stop when impossible. Final result?"},
        {"id":"h9","title":"Bit Flip Score","diff":"EASY","pts":500,"desc":"Binary string: 11010011101101001110. Flip exactly one contiguous subarray (0→1, 1→0). Maximum 1s possible?"},
        {"id":"h10","title":"Subsequence Illusion","diff":"EASY","pts":500,"desc":"String: istetiet. Count distinct subsequences equal to 'tiet'. (Subsequence: delete chars without changing order)"},
        # ─ MEDIUM (10) ─
        {"id":"h11","title":"Audio Archive","diff":"MEDIUM","pts":750,"desc":"A dusty archive yields a peculiar audio file. At first, chaotic static—white noise with no pattern. But something feels intentional: 'You're hearing only half the story. Some messages aren't meant to be heard.' Download and analyze.","link":"https://drive.google.com/file/d/1WEEu48om3dtKn0rHF9kWaDxkVeCtwauk/view?usp=drive_link"},
        {"id":"h12","title":"Hex Decode","diff":"MEDIUM","pts":750,"desc":"A spy intercepted a mysterious message in hex encoding: 73 65 63 72 65 74 5f 62 61 73 65. Decode to plaintext. The data appears to be encoded and not directly readable."},
        {"id":"h13","title":"Git History","diff":"MEDIUM","pts":750,"desc":"A developer accidentally committed a secret to a repository, quickly removed it and pushed a new version, believing the secret was gone. Explore the repository's past commits—deleting a file doesn't erase its history.","link":"https://drive.google.com/file/d/1yYNGltWlgc7v3b7ggvhwELHuJVQKl0n9/view?usp=drive_link"},
        {"id":"h14","title":"Corrupted Image","diff":"MEDIUM","pts":750,"desc":"A mysterious file has been recovered, but it refuses to open. Seemingly corrupted, yet something feels intentional. 'The file is broken. The password is lost. The flag is buried. You have three layers of security to peel back.'","link":"https://drive.google.com/file/d/1x65T0p9l0TNbtpcck1CAWSRceIOhrOaH/view?usp=drive_link"},
        {"id":"h15","title":"Obfuscated JavaScript","diff":"MEDIUM","pts":750,"desc":"A suspicious HTML file recovered during investigation. Embedded JavaScript is heavily obfuscated with meaningless operations and confusing control flow. 'Not everything that runs matters... and not everything that matters runs in order.' Focus on arrays and bitwise operations—simple transformation hides behind complexity.","link":"https://drive.google.com/file/d/1jeqcox0Zmf3xsBO26fCiT_ZTz4hXUr9b/view?usp=drive_link"},
        {"id":"h16","title":"PDF Secrets","diff":"MEDIUM","pts":750,"desc":"A company policy document circulated internally—on the surface, completely normal. But something doesn't add up. 'Not everything in a document is meant to be seen. Some secrets exist where no page can reach.' Analyze the PDF for hidden data.","link":"https://drive.google.com/file/d/1FblfNeNq6hUvhjc2o0-Oo9yjdZox2MCa/view?usp=drive_link"},
        {"id":"h17","title":"ZIP Comments","diff":"MEDIUM","pts":750,"desc":"A password-protected ZIP archive recovered during investigation. Inside appears a harmless text file—but something feels like a distraction. 'Not all secrets are locked away. Some are hidden where no one thinks to look.' Recover the hidden flag.","link":"https://drive.google.com/file/d/1ii_d1yvkzkJyEYRBjMOxCR-Bg51XQLav/view?usp=drive_link"},
        {"id":"h18","title":"Grid Pathfinding","diff":"MEDIUM","pts":750,"desc":"Grid: [[1,3,1],[1,5,1],[4,2,1]]. Move only right or down. Find the minimum path sum from top-left to bottom-right."},
        {"id":"h19","title":"Elevator Puzzle","diff":"MEDIUM","pts":750,"desc":"Secret facility: 20 floors (1-20). Elevator wraps around: floor 20+UP→1, floor 1-DOWN→20. Start at floor 10. Commands: [8,5,15,7,12]. EVEN→UP by n/2, PRIME→DOWN by n, ODD(not prime)→no move, next valid reversed. Final floor?"},
        {"id":"h20","title":"Heartbeat Signal","diff":"MEDIUM","pts":750,"desc":"Network trace shows long ICMP (ping) requests—regular heartbeat traffic between machines. Analysts suspect it carries more than connectivity checks. 'Every heartbeat carries a signal... if you listen closely enough.' Analyze packet capture to reconstruct hidden flag.","link":"https://drive.google.com/file/d/1X3h8Da3pBE78r6FRAxrz6HRiNk77S9RD/view?usp=drive_link"},
        # ─ HARD (7) ─
        {"id":"h21","title":"Triple Encryption","diff":"HARD","pts":1000,"desc":"Message secured with three transformations: (1) ROT13, (2) Reverse entire string, (3) Encode to hex (char→2-digit hex). Final output: 656c62 6d75645f 6c6c6977 5f756f79. Work backwards: hex decode→reverse→ROT13. Recover plaintext."},
        {"id":"h22","title":"Baby RSA","diff":"HARD","pts":1000,"desc":"Mole used simple RSA with exposed public parameters. Only one character encrypted. n=3233, e=17, c=2790. Factor n into primes, compute φ(n), find modular inverse d. Decrypt using RSA and convert result to ASCII character."},
        {"id":"h23","title":"Sudoku Solver","diff":"HARD","pts":1000,"desc":"9×9 Sudoku grid (0=empty). Each row, column, 3×3 subgrid contains 1-9 exactly once. Grid provided. After solving, sum the digits on main diagonal (top-left to bottom-right)."},
        {"id":"h24","title":"Protocol Tunnel","diff":"HARD","pts":1000,"desc":"Firewall intercepted ICMP packets from unknown source. Traffic appears normal at first—standard requests, no suspicious payloads. 'The packets look ordinary... but one header field is behaving strangely. It almost feels like the data is trying to communicate.' Analyze packet capture.","link":"https://drive.google.com/file/d/1NMNPh4PchneqFKFCVWUiwmnEYvzY9KLw/view?usp=drive_link"},
        {"id":"h25","title":"Chromatic Vault","diff":"HARD","pts":1000,"desc":"Seemingly harmless image file recovered from compromised system. Opens normally, nothing unusual to naked eye. But analysts believe it's more than just an image. 'Not every color is meant to be seen. Some are hiding something deeper.' Analyze file for hidden flag.","link":"https://drive.google.com/file/d/1OISMonvwopLFBF1lRpHx7yEcivwhJgwW/view?usp=drive_link"},
        {"id":"h26","title":"Packet Sniffer","diff":"HARD","pts":1000,"desc":"Network capture from compromised machine shows routine traffic including file transfer. At first glance, normal—everything seems fine. 'The file transfer completed successfully... or did it? Sometimes, what's sent isn't what's received.' Analyze capture for hidden flag.","link":"https://drive.google.com/file/d/16tY-j-q0ywwb8ipJA8cu42q9_hoUdgrX/view?usp=drive_link"},
        {"id":"h27","title":"Ghost in Crontab","diff":"HARD","pts":1000,"desc":"Backup script recovered from compromised Linux server. Appears to be routine utility for scheduled backups. But something feels off. 'The job runs on time... but what if the schedule itself is hiding something?' Analyze script for hidden flag.","link":"https://drive.google.com/file/d/1eN5Kc7vrBgYURrd7SiA3n1ShWVVoKZyK/view?usp=drive_link"},
    ],
}

MONARCH_TASK_PORTAL = {
    # EASY (10)
    "h1": {"answer": "old_things_still_work"},
    "h2": {"answer": "fr3qu3ncy_m4tt3rs"},
    "h3": {"answer": "Bright Electric Blue"},
    "h4": {"answer": "DBU"},
    "h5": {"answer": "Break_the_code_first"},
    "h6": {"answer": "login_now"},
    "h7": {"answer": "11"},
    "h8": {"answer": "tiet"},
    "h9": {"answer": "14"},
    "h10": {"answer": "2"},
    # MEDIUM (10)
    "h11": {"answer": "v1su4l_v1brati0ns"},
    "h12": {"answer": "secret_base"},
    "h13": {"answer": "git_n3v3r_forg3ts"},
    "h14": {"answer": "n3st3d_m4tr3ry0shka_d0ll"},
    "h15": {"answer": "js_0bfusc4t10n_1s_4rt_2026"},
    "h16": {"answer": "p1df_0bj3ct_h1d3_2026"},
    "h17": {"answer": "z1p_c0mm3nt_n0t_s0_s3cr3t_2026"},
    "h18": {"answer": "7"},
    "h19": {"answer": "2"},
    "h20": {"answer": "p1ng_p0ng_d4t4_42"},
    # HARD (7)
    "h21": {"answer": "you_will_never"},
    "h22": {"answer": "A"},
    "h23": {"answer": "47"},
    "h24": {"answer": "p1ng_p0ng_pr0t0c0l"},
    "h25": {"answer": "p4l3tt3_p01s0n1ng_4281"},
    "h26": {"answer": "p4ck3t_h4ck3r_n01_2026"},
    "h27": {"answer": "cr0n_j0b_h3r0_2026"},
}

BOT_TASKS = {
    # ─ NEURAL ARCHITECT (Pattern Processing) ─
    "NA_06": {
        "id":"NA_06", "category":"Neural Architect", "title":"Convolution Engine",
        "description":"Apply 3x3 convolution to a 10x10 grid with padding=1",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"convolution_3x3",
        "template":"""def convolution_3x3(grid, kernel):
    \"\"\"Perform 3x3 convolution on 10x10 grid. Edges padded with 0.\"\"\"
    result = [[0]*10 for _ in range(10)]
    # TODO: Extract 3x3 neighborhoods and apply kernel
    return result""",
        "test_harness":"""grid = [[1.0]*10 for _ in range(10)]
kernel = [[1/9]*3 for _ in range(3)]
result = convolution_3x3(grid, kernel)
verify_val = round(result[5][5], 1)""",
        "expected_output": 1.0,
        "verify_token":"CONV_RESULT"
    },
    "NA_07": {
        "id":"NA_07", "category":"Neural Architect", "title":"Matrix Rotation",
        "description":"Rotate a 5x5 matrix 90 degrees clockwise",
        "difficulty":"EASY", "ap_reward":500, "function_name":"rotate_matrix_90",
        "template":"""def rotate_matrix_90(matrix):
    \"\"\"Rotate 5x5 matrix 90° clockwise. matrix[i][j] -> matrix[j][4-i]\"\"\"
    n = 5
    result = [[0]*5 for _ in range(5)]
    # TODO: Rotate the matrix
    return result""",
        "test_harness":"""matrix = [[i*5+j for j in range(5)] for i in range(5)]
result = rotate_matrix_90(matrix)
verify_val = result[0][4]""",
        "expected_output": 0,
        "verify_token":"ROT_COMPLETE"
    },
    "NA_08": {
        "id":"NA_08", "category":"Neural Architect", "title":"Blob Analysis",
        "description":"Find longest contiguous chain of 1s (horizontal/vertical/diagonal)",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"longest_blob",
        "template":"""def longest_blob(grid):
    \"\"\"Find longest contiguous sequence of 1s in grid (4-connected).\"\"\"
    visited = set()
    max_len = 0
    
    def dfs(i, j):
        if (i,j) in visited or i<0 or i>=len(grid) or j<0 or j>=len(grid[0]) or grid[i][j]!=1:
            return 0
        visited.add((i,j))
        length = 1
        # TODO: Recursively count neighbors
        return length
    
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j]==1 and (i,j) not in visited:
                max_len = max(max_len, dfs(i,j))
    return max_len""",
        "test_harness":"""grid = [[1,1,0,1,1],[1,1,0,0,0],[0,0,0,1,1],[0,0,1,1,1],[0,0,1,1,1]]
result = longest_blob(grid)
verify_val = result""",
        "expected_output": 6,
        "verify_token":"BLOB_MAX_LEN"
    },
    "NA_09": {
        "id":"NA_09", "category":"Neural Architect", "title":"Gaussian Blur",
        "description":"Apply Gaussian blur approximation (3x3 averaging kernel) to 10x10 grid",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"gaussian_blur",
        "template":"""def gaussian_blur(grid):
    \"\"\"Apply 3x3 averaging filter (simplest blur).\"\"\"
    result = [[grid[i][j] for j in range(10)] for i in range(10)]
    # TODO: For interior cells, replace with average of 3x3 neighborhood
    return result""",
        "test_harness":"""grid = [[2]*10 for _ in range(10)]
grid[5][5] = 10
result = gaussian_blur(grid)
verify_val = round(result[5][5], 1)""",
        "expected_output": 2.0,
        "verify_token":"BLUR_STABLE"
    },
    "NA_10": {
        "id":"NA_10", "category":"Neural Architect", "title":"Gaussian Thresholding",
        "description":"Apply adaptive Gaussian thresholding: if pixel > (local_mean + 2*std), set to 255, else 0",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"gaussian_threshold",
        "template":"""def gaussian_threshold(grid):
    \"\"\"Adaptive threshold: pixel > (mean + 2*std) -> 255, else 0\"\"\"
    import statistics
    result = [[0]*10 for _ in range(10)]
    
    for i in range(10):
        for j in range(10):
            # TODO: Extract 5x5 neighborhood, compute mean and std
            # If grid[i][j] > mean + 2*std, set result[i][j]=255, else 0
            pass
    return result""",
        "test_harness":"""grid = [[5]*10 for _ in range(10)]
grid[5][5] = 20
result = gaussian_threshold(grid)
verify_val = result[5][5]""",
        "expected_output": 255,
        "verify_token":"THRESH_APPLIED"
    },
    
    # ─ CIPHER BREAKER (Cryptography) ─
    "CB_06": {
        "id":"CB_06", "category":"Cipher Breaker", "title":"Vigenère Decryption",
        "description":"Decrypt Vigenère cipher with unknown key. Plaintext is English (check common words).",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"decrypt_vigenere",
        "template":"""def decrypt_vigenere(ciphertext, key):
    \"\"\"Decrypt Vigenère cipher given key.\"\"\"
    plaintext = ""
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            shift = ord(key[i % len(key)].upper()) - ord('A')
            if char.isupper():
                plaintext += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                plaintext += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
        else:
            plaintext += char
    return plaintext""",
        "test_harness":"""ciphertext = "LXFOPVEFRNHR"
key = "KEY"
result = decrypt_vigenere(ciphertext, key)
verify_val = result.upper()""",
        "expected_output": "ATTACKATDAWN",
        "verify_token":"VIG_DECRYPTED"
    },
    "CB_07": {
        "id":"CB_07", "category":"Cipher Breaker", "title":"Modular Exponentiation",
        "description":"Compute (base^exp) mod mod efficiently using binary exponentiation",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"mod_exp",
        "template":"""def mod_exp(base, exp, mod):
    \"\"\"Compute (base^exp) % mod efficiently. Use binary exponentiation.\"\"\"
    result = 1
    base = base % mod
    # TODO: Binary exponentiation loop
    return result""",
        "test_harness":"""result = mod_exp(2, 10, 1000)
verify_val = result""",
        "expected_output": 24,
        "verify_token":"MOD_EXP_OK"
    },
    "CB_08": {
        "id":"CB_08", "category":"Cipher Breaker", "title":"Salt Brute Force",
        "description":"Brute force 3-digit salt (000-999) to match target hash",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"crack_salt",
        "template":"""def crack_salt(target_hash, hash_func):
    \"\"\"Brute force 3-digit salt (0-999) to match target_hash.\"\"\"
    for salt in range(1000):
        if hash_func(salt) == target_hash:
            return salt
    return -1""",
        "test_harness":"""import hashlib
def test_hash(salt):
    return hashlib.md5(f"password{salt:03d}".encode()).hexdigest()[:6]
target = test_hash(342)
result = crack_salt(target, test_hash)
verify_val = result""",
        "expected_output": 342,
        "verify_token":"SALT_CRACKED"
    },
    "CB_09": {
        "id":"CB_09", "category":"Cipher Breaker", "title":"Bit Rotation",
        "description":"Circular left-rotate 32-bit integer by n positions",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"rotate_left",
        "template":"""def rotate_left(value, n):
    \"\"\"Circular left-rotate 32-bit int by n positions.\"\"\"
    n = n % 32
    # TODO: Shift left, wrap around
    return value & 0xFFFFFFFF""",
        "test_harness":"""result = rotate_left(1, 1)
verify_val = result""",
        "expected_output": 2,
        "verify_token":"BIT_ROTATED"
    },
    "CB_10": {
        "id":"CB_10", "category":"Cipher Breaker", "title":"HMAC Verification",
        "description":"Verify HMAC-SHA256 signature given key and message",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"verify_hmac",
        "template":"""def verify_hmac(message, key, signature):
    \"\"\"Verify HMAC-SHA256 signature.\"\"\"
    import hmac
    import hashlib
    expected = hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return expected == signature""",
        "test_harness":"""import hmac, hashlib
message = "hello"
key = "secret"
sig = hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
result = verify_hmac(message, key, sig)
verify_val = int(result)""",
        "expected_output": 1,
        "verify_token":"HMAC_VERIFIED"
    },
    
    # ─ STREAM VECTOR (Data Engineering) ─
    "SV_06": {
        "id":"SV_06", "category":"Stream Vector", "title":"Streaming Median",
        "description":"Find median of streaming data using min/max heaps",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"streaming_median",
        "template":"""def streaming_median(stream):
    \"\"\"Find median of stream using heaps. Return final median.\"\"\"
    import heapq
    small = []  # max heap (negated)
    large = []  # min heap
    
    for num in stream:
        # TODO: Maintain balanced heaps and compute median at each step
        pass
    
    if len(small) > len(large):
        return float(-small[0])
    return (-small[0] + large[0]) / 2.0""",
        "test_harness":"""stream = [1, 2, 3, 4, 5]
result = streaming_median(stream)
verify_val = result""",
        "expected_output": 3.0,
        "verify_token":"MEDIAN_CALC"
    },
    "SV_07": {
        "id":"SV_07", "category":"Stream Vector", "title":"Delta Compression",
        "description":"Compress data by storing differences between consecutive elements",
        "difficulty":"EASY", "ap_reward":500, "function_name":"delta_compress",
        "template":"""def delta_compress(data):
    \"\"\"Return list of differences: [data[0], data[1]-data[0], data[2]-data[1], ...]\"\"\"
    if not data:
        return []
    result = [data[0]]
    # TODO: Append differences
    return result""",
        "test_harness":"""data = [10, 15, 13, 20, 18]
result = delta_compress(data)
verify_val = sum(result)""",
        "expected_output": 46,
        "verify_token":"DELTA_COMP"
    },
    "SV_08": {
        "id":"SV_08", "category":"Stream Vector", "title":"Cumulative Sum Limit",
        "description":"Find index where cumulative sum exceeds threshold",
        "difficulty":"EASY", "ap_reward":500, "function_name":"cumsum_limit",
        "template":"""def cumsum_limit(data, threshold):
    \"\"\"Find index where cumsum(data[:i+1]) > threshold. Return -1 if never.\"\"\"
    total = 0
    for i, val in enumerate(data):
        total += val
        if total > threshold:
            return i
    return -1""",
        "test_harness":"""data = [1, 2, 3, 4, 5]
result = cumsum_limit(data, 8)
verify_val = result""",
        "expected_output": 3,
        "verify_token":"CUMSUM_LIMIT"
    },
    "SV_09": {
        "id":"SV_09", "category":"Stream Vector", "title":"Inner Join",
        "description":"Perform inner join on two list-of-dicts by foreign key",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"inner_join",
        "template":"""def inner_join(left, right, left_key, right_key):
    \"\"\"Inner join two list-of-dicts by key.\"\"\"
    result = []
    right_dict = {r[right_key]: r for r in right}
    for l in left:
        if l[left_key] in right_dict:
            result.append({**l, **right_dict[l[left_key]]})
    return result""",
        "test_harness":"""left = [{"id":1, "name":"Alice"}, {"id":2, "name":"Bob"}]
right = [{"id":1, "age":25}, {"id":3, "age":30}]
result = inner_join(left, right, "id", "id")
verify_val = len(result)""",
        "expected_output": 1,
        "verify_token":"JOIN_SUCCESS"
    },
    "SV_10": {
        "id":"SV_10", "category":"Stream Vector", "title":"Longest Increasing Subsequence",
        "description":"Find length of longest strictly increasing subsequence",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"longest_increasing_subseq",
        "template":"""def longest_increasing_subseq(arr):
    \"\"\"Find LIS length using dynamic programming or binary search.\"\"\"
    if not arr:
        return 0
    # TODO: DP or O(n log n) approach
    return 0""",
        "test_harness":"""arr = [10, 9, 2, 5, 3, 7, 101, 18]
result = longest_increasing_subseq(arr)
verify_val = result""",
        "expected_output": 4,
        "verify_token":"LIS_LENGTH"
    },
    
    # ─ STRATEGY MATRIX (Game Theory) ─
    "SM_06": {
        "id":"SM_06", "category":"Strategy Matrix", "title":"Alpha-Beta Pruning",
        "description":"Implement alpha-beta pruning to prune minimax tree",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"alpha_beta",
        "template":"""def alpha_beta(node, depth, is_max, alpha, beta, eval_func):
    \"\"\"Alpha-beta pruning. eval_func(node) returns node score.\"\"\"
    if depth == 0 or is_terminal(node):
        return eval_func(node)
    
    if is_max:
        value = float('-inf')
        for child in get_children(node):
            # TODO: Recursive call with alpha/beta updates
            if value >= beta:
                break  # Beta cutoff
        return value
    else:
        value = float('inf')
        for child in get_children(node):
            # TODO: Recursive call
            if value <= alpha:
                break  # Alpha cutoff
        return value""",
        "test_harness":"""def is_terminal(n): return n > 100
def get_children(n): return [n+1, n+2] if n <= 100 else []
def eval_func(n): return n % 7
result = alpha_beta(50, 3, True, float('-inf'), float('inf'), eval_func)
verify_val = result % 7""",
        "expected_output": 3,
        "verify_token":"PRUNED_VAL"
    },
    "SM_07": {
        "id":"SM_07", "category":"Strategy Matrix", "title":"0/1 Knapsack",
        "description":"Solve 0/1 knapsack problem with DP. Max weight items by value.",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"knapsack_01",
        "template":"""def knapsack_01(items, capacity):
    \"\"\"0/1 Knapsack DP. items = [(weight, value), ...]. Return max value.\"\"\"
    dp = [0] * (capacity + 1)
    for weight, value in items:
        for w in range(capacity, weight - 1, -1):
            # TODO: Update DP
            pass
    return dp[capacity]""",
        "test_harness":"""items = [(2,3), (3,4), (4,5), (5,6)]
result = knapsack_01(items, 8)
verify_val = result""",
        "expected_output": 13,
        "verify_token":"KNAP_OPTIMIZED"
    },
    "SM_08": {
        "id":"SM_08", "category":"Strategy Matrix", "title":"Connect-4 Solver",
        "description":"Find winning move in 4x4 connect-four given board state",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"connect4_win",
        "template":"""def connect4_win(board):
    \"\"\"Find column to play (0-3) to win immediately. Return -1 if none.\"\"\"
    for col in range(4):
        # TODO: Simulate drop, check for 4-in-a-row
        pass
    return -1""",
        "test_harness":"""board = [['X','X','X','.'], ['.','.','.','.'],['.','.','.','.'],['.','.','.','.']]
result = connect4_win(board)
verify_val = result + 1""",
        "expected_output": 4,
        "verify_token":"WIN_MOVE"
    },
    "SM_09": {
        "id":"SM_09", "category":"Strategy Matrix", "title":"Nash Equilibrium",
        "description":"Find Nash equilibrium mixed strategy for 2x2 payoff matrix",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"nash_equilibrium",
        "template":"""def nash_equilibrium(payoff_matrix):
    \"\"\"Compute mixed strategy Nash Eq for 2x2 game.
    payoff_matrix = [[A,B],[C,D]] for player 1.
    Return (p, q) where p=prob player 1 plays strategy 0, q=prob player 2 plays strategy 0.\"\"\"
    # TODO: Solve using indifference conditions
    return (0.5, 0.5)""",
        "test_harness":"""payoff = [[3,0],[5,1]]
p, q = nash_equilibrium(payoff)
verify_val = round(p + q, 1)""",
        "expected_output": 1.0,
        "verify_token":"NASH_EQUIL"
    },
    "SM_10": {
        "id":"SM_10", "category":"Strategy Matrix", "title":"State Prediction",
        "description":"Predict game state after 3 moves given opponent behavior",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"predict_state",
        "template":"""def predict_state(initial_state, my_moves, opponent_strategy):
    \"\"\"Simulate 3 moves and return final state.
    opponent_strategy(state) returns opponent's next move.\"\"\"
    state = initial_state
    for i in range(3):
        state = apply_move(state, my_moves[i], True)
        state = apply_move(state, opponent_strategy(state), False)
    return state

def apply_move(state, move, is_player):
    # TODO: Apply move to state
    return state""",
        "test_harness":"""initial = 100
def opponent(s): return s - 5
def my_m(i): return 10
moves = [my_m(0), my_m(1), my_m(2)]
result = predict_state(initial, moves, opponent)
verify_val = result""",
        "expected_output": 100,
        "verify_token":"STATE_PRED"
    },
    
    # ─ ANOMALY GUARD (Statistical) ─
    "AG_06": {
        "id":"AG_06", "category":"Anomaly Guard", "title":"Change-Point Detection",
        "description":"Find index where mean shifts by >30% (compare pre/post mean)",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"detect_changepoint",
        "template":"""def detect_changepoint(data, threshold=0.30):
    \"\"\"Find index i where |mean(data[i:]) - mean(data[:i])| / mean(data[:i]) > threshold.\"\"\"
    for i in range(1, len(data)):
        pre_mean = sum(data[:i]) / i
        post_mean = sum(data[i:]) / (len(data) - i)
        if abs(post_mean - pre_mean) / pre_mean > threshold:
            return i
    return -1""",
        "test_harness":"""data = [1,2,1,2,1,2] + [10,10,10,10]
result = detect_changepoint(data)
verify_val = result""",
        "expected_output": 6,
        "verify_token":"SHIFT_DETECTED"
    },
    "AG_07": {
        "id":"AG_07", "category":"Anomaly Guard", "title":"Volatility Detection",
        "description":"Compute variance in sliding 3-window. Return max variance.",
        "difficulty":"EASY", "ap_reward":500, "function_name":"max_volatility",
        "template":"""def max_volatility(data, window=3):
    \"\"\"Compute variance for each sliding window. Return max variance.\"\"\"
    max_var = 0
    for i in range(len(data) - window + 1):
        window_data = data[i:i+window]
        mean = sum(window_data) / window
        var = sum((x - mean)**2 for x in window_data) / window
        max_var = max(max_var, var)
    return max_var""",
        "test_harness":"""data = [1, 1, 5, 1, 1]
result = max_volatility(data, 3)
verify_val = round(result, 2)""",
        "expected_output": 5.33,
        "verify_token":"VOLATILITY_OK"
    },
    "AG_08": {
        "id":"AG_08", "category":"Anomaly Guard", "title":"Pearson Correlation",
        "description":"Compute Pearson correlation between two streams. Return True if r > 0.7.",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"is_correlated",
        "template":"""def is_correlated(x, y, threshold=0.7):
    \"\"\"Compute Pearson r. Return True if |r| > threshold.\"\"\"
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x))) / len(x)
    std_x = (sum((xi - mean_x)**2 for xi in x) / len(x)) ** 0.5
    std_y = (sum((yi - mean_y)**2 for yi in y) / len(y)) ** 0.5
    r = cov / (std_x * std_y)
    return abs(r) > threshold""",
        "test_harness":"""x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
result = is_correlated(x, y)
verify_val = int(result)""",
        "expected_output": 1,
        "verify_token":"CORR_POSITIVE"
    },
    "AG_09": {
        "id":"AG_09", "category":"Anomaly Guard", "title":"Logistic Regression",
        "description":"Apply logistic function sigmoid(x) = 1/(1+e^-x) and threshold at 0.5",
        "difficulty":"EASY", "ap_reward":500, "function_name":"logistic_predict",
        "template":"""def logistic_predict(x, threshold=0.5):
    \"\"\"Compute sigmoid(x) and return True if sigmoid(x) > threshold.\"\"\"
    import math
    sigmoid = 1 / (1 + math.exp(-x))
    return sigmoid > threshold""",
        "test_harness":"""result = logistic_predict(0.5)
verify_val = int(result)""",
        "expected_output": 1,
        "verify_token":"LOGISTIC_VAL"
    },
    "AG_10": {
        "id":"AG_10", "category":"Anomaly Guard", "title":"Isolation Forest",
        "description":"Check if value is an outlier: value > (mean + 2*std) or value < (mean - 2*std)",
        "difficulty":"EASY", "ap_reward":500, "function_name":"is_outlier",
        "template":"""def is_outlier(value, cluster, sigma=2):
    \"\"\"Check if value > mean + sigma*std or < mean - sigma*std.\"\"\"
    mean = sum(cluster) / len(cluster)
    var = sum((x - mean)**2 for x in cluster) / len(cluster)
    std = var ** 0.5
    return value > mean + sigma*std or value < mean - sigma*std""",
        "test_harness":"""cluster = [1, 2, 3, 4, 5]
result = is_outlier(10, cluster)
verify_val = int(result)""",
        "expected_output": 1,
        "verify_token":"ISOLATION_TRUE"
    },
    
    # ─ RESOURCE OPTIMIZER (Graph Algorithms) ─
    "RO_06": {
        "id":"RO_06", "category":"Resource Optimizer", "title":"A* Pathfinding",
        "description":"Find shortest path in 5x5 grid using A* with Manhattan heuristic",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"astar_path",
        "template":"""def astar_path(grid, start, goal):
    \"\"\"A* pathfinding. grid[i][j] = 1 if obstacle, 0 if free.
    Return path length or -1 if no path.\"\"\"
    import heapq
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    
    def heuristic(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # TODO: Reconstruct path length
            return len(came_from) + 1
        for next_pos in get_neighbors(current):
            # TODO: A* loop
            pass
    return -1

def get_neighbors(pos):
    r, c = pos
    return [(r+dr, c+dc) for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)] 
            if 0<=r+dr<5 and 0<=c+dc<5]""",
        "test_harness":"""grid = [[0]*5 for _ in range(5)]
result = astar_path(grid, (0,0), (4,4))
verify_val = result""",
        "expected_output": 9,
        "verify_token":"A_STAR_DONE"
    },
    "RO_07": {
        "id":"RO_07", "category":"Resource Optimizer", "title":"Max-Flow",
        "description":"Find max flow (bottleneck capacity) using Ford-Fulkerson",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"max_flow",
        "template":"""def max_flow(capacity, source, sink, n_nodes):
    \"\"\"Ford-Fulkerson max flow. capacity[i][j] = edge capacity.\"\"\"
    flow = 0
    residual = [row[:] for row in capacity]
    
    def dfs(u, target, visited, min_cap):
        if u == target:
            return min_cap
        visited.add(u)
        for v in range(n_nodes):
            if v not in visited and residual[u][v] > 0:
                # TODO: DFS to find augmenting path
                pass
        return 0
    
    while True:
        path_flow = dfs(source, sink, set(), float('inf'))
        if path_flow == 0:
            break
        flow += path_flow
    return flow""",
        "test_harness":"""cap = [[0,10,10,0],[0,0,2,8],[0,0,0,10],[0,0,0,0]]
result = max_flow(cap, 0, 3, 4)
verify_val = result""",
        "expected_output": 20,
        "verify_token":"MAX_FLOW_OK"
    },
    "RO_08": {
        "id":"RO_08", "category":"Resource Optimizer", "title":"Traveling Salesman",
        "description":"Find TSP tour cost for 5 cities using nearest-neighbor heuristic",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"tsp_nearest_neighbor",
        "template":"""def tsp_nearest_neighbor(dist_matrix, start=0):
    \"\"\"TSP nearest-neighbor heuristic. Return tour cost.\"\"\"
    n = len(dist_matrix)
    visited = [False] * n
    visited[start] = True
    current = start
    cost = 0
    
    for _ in range(n - 1):
        nearest = -1
        min_dist = float('inf')
        for j in range(n):
            if not visited[j] and dist_matrix[current][j] < min_dist:
                # TODO: Find nearest unvisited city
                pass
        cost += min_dist
        current = nearest
        visited[nearest] = True
    
    cost += dist_matrix[current][start]  # Return to start
    return cost""",
        "test_harness":"""dist = [[0,1,2,3,4],[1,0,2,3,4],[2,2,0,1,5],[3,3,1,0,2],[4,4,5,2,0]]
result = tsp_nearest_neighbor(dist, 0)
verify_val = result""",
        "expected_output": 10,
        "verify_token":"TSP_OPTIMAL"
    },
    "RO_09": {
        "id":"RO_09", "category":"Resource Optimizer", "title":"Minimum Spanning Tree",
        "description":"Find MST cost using Prim's algorithm. Edges as [(u,v,weight),...]",
        "difficulty":"MEDIUM", "ap_reward":750, "function_name":"mst_prim",
        "template":"""def mst_prim(n_nodes, edges):
    \"\"\"Prim's MST. edges = [(u, v, weight), ...]. Return total weight.\"\"\"
    visited = [False] * n_nodes
    visited[0] = True
    total_weight = 0
    edge_queue = []
    
    for u, v, w in edges:
        if visited[u] != visited[v]:
            edge_queue.append((w, u, v))
    
    edge_queue.sort()
    
    while edge_queue:
        w, u, v = edge_queue.pop(0)
        # TODO: Add edge if it connects to unvisited node
        pass
    
    return total_weight""",
        "test_harness":"""edges = [(0,1,1), (1,2,3), (0,2,2), (2,3,1), (1,3,2)]
result = mst_prim(4, edges)
verify_val = result""",
        "expected_output": 5,
        "verify_token":"MST_WEIGHT"
    },
    "RO_10": {
        "id":"RO_10", "category":"Resource Optimizer", "title":"Betweenness Centrality",
        "description":"Find node with highest betweenness centrality in graph",
        "difficulty":"HARD", "ap_reward":1000, "function_name":"highest_centrality",
        "template":"""def highest_centrality(n_nodes, edges):
    \"\"\"Compute betweenness centrality. Return node index with max centrality.\"\"\"
    from collections import defaultdict, deque
    
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    
    centrality = [0] * n_nodes
    
    for s in range(n_nodes):
        # BFS from s
        visited = {s}
        queue = deque([(s, 0)])
        paths = [[] for _ in range(n_nodes)]
        paths[s] = [[s]]
        
        while queue:
            # TODO: BFS to count shortest paths through each node
            pass
    
    return centrality.index(max(centrality))""",
        "test_harness":"""edges = [(0,1), (0,2), (1,2), (1,3), (2,3)]
result = highest_centrality(4, edges)
verify_val = result""",
        "expected_output": 1,
        "verify_token":"CENTRALITY_ID"
    },
}

DIFF_COLOR = {"EASY": "#00CC88", "MEDIUM": "#FFB800", "HARD": "#FF2244"}
EVENT_COLORS = {
    "ATTACK":"#FF2244","BACKSTAB":"#9933FF","ALLIANCE":"#00CC88",
    "SUSPICION":"#FFB800","TASK":"#00E5FF","SYS":"#3a3a5a","WS_TX":"#00CC88",
}

import math

def generate_amoeba_points(n=30, width=600, height=500):
    points = []
    phi = (1 + math.sqrt(5)) / 2
    for i in range(n):
        r = 200 * math.sqrt((i + 0.5) / n)
        theta = 2 * math.pi * i / phi
        noiseX = math.sin(i * 123) * 15
        noiseY = math.cos(i * 321) * 15
        x = width / 2 + r * math.cos(theta) + noiseX
        y = height / 2 + r * math.sin(theta) + noiseY
        points.append((x, y))
    return points

def get_amoeba_adjacency(n=30):
    from scipy.spatial import Delaunay
    points = generate_amoeba_points(n)
    tri = Delaunay(points)
    adj = {i: set() for i in range(n)}
    for simplex in tri.simplices:
        adj[simplex[0]].update([simplex[1], simplex[2]])
        adj[simplex[1]].update([simplex[0], simplex[2]])
        adj[simplex[2]].update([simplex[0], simplex[1]])
    return {k: list(v) for k, v in adj.items()}
