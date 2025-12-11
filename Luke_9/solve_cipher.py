
cipher = "NSB{xk3_o0ex4b_0o3iq_dk3i_3a3ef_b1vkx_e3z3zp3eq_cke1qxz4q}"

def decrypt_and_releet(cipher):
    def decrypt_char(c):
        # Mappings derived from XOR analysis
        xors = {
            'N': 4,              # N->J
            'S': 6,              # S->U
            'B': 14, 'b': 14, 'p': 14, # B->L, b->l, p->b
            'x': 12,             # x->t
            'k': 3,              # k->h
            'o': 31, 'f': 31,    # o->p, f->y
            'e': 23, 'z': 23, 'a': 23, # e->r, z->m, a->v
            'd': 19,             # d->w
            'q': 2,              # q->s
            'i': 7,              # i->n
            'v': 17,             # v->g
            'c': 0               # c->c
        }
        
        # Leet characters (0,1,3,4) must be handled separately/passed through 
        # or mapped if they act as substitution source.
        # But here 0,1,3,4 are the "Cipher" chars representing vowels.
        # 0->o, 1->i, 3->e, 4->a
        if c == '0': return 'o'
        if c == '1': return 'i'
        if c == '3': return 'e'
        if c == '4': return 'a'
        
        if c in xors:
            return chr(ord(c) ^ xors[c])
        return c

    plain = "".join([decrypt_char(c) for c in cipher])
    
    # Re-apply Leet for final flag
    leet_map = { 'o': '0', 'i': '1', 'e': '3', 'a': '4' }
    leeted = ""
    for c in plain:
        leeted += leet_map.get(c, c)
            
    return leeted

print(f"Decoded: {decrypt_and_releet(cipher)}")
