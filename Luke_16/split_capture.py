def read_varint(data, i=0):
    num = 0
    shift = 0
    while True:
        b = data[i]
        i += 1
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return num, i

def split_packets(raw):
    i = 0
    packets = []
    while i < len(raw):
        length, i = read_varint(raw, i)
        packet = raw[i:i+length]
        packets.append(packet)
        i += length
    return packets