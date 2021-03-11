from app import sbox_table
xor_profile = []
for sbox in sbox_table:
    sbox_xor_profile = []
    for i in range(16):
        sbox_xor_profile.append([0 for i in range(16)])
        for j in range(16):
            a, b = sbox[j], sbox[(j+i) % 16]
            sbox_xor_profile[i][abs(a-b)] += 1
    xor_profile.append(sbox_xor_profile)

for i in range(12):
    print(f"----------------------------------------\nsbox {i}:\n")
    round_maxes = []
    for j in range(16):
        round_max = max(xor_profile[i][j])
        if j != 0:
            round_maxes.append(round_max)
        print(xor_profile[i][j], round_max)
    print("sbox max characteristics:",max(round_maxes))
