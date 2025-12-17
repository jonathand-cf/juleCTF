import binascii
import struct

def read_varint(data, i=0):
    num = 0
    shift = 0
    start_i = i
    while True:
        if i >= len(data):
            raise Exception("VarInt read out of bounds")
        b = data[i]
        i += 1
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return num, i

def parse_stream(filename):
    # Reassemble full binary stream from sequence
    packets = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2: continue
            try:
                # seq = int(parts[0]) - not needed if we trust the order or sort?
                # stream1_server.txt is sorted by seq.
                payload_hex = parts[1].replace(':', '')
                payload = binascii.unhexlify(payload_hex)
                packets.append(payload)
            except:
                pass
                
    full_data = b"".join(packets)
    print(f"Total stream size: {len(full_data)}")
    
    # Parse MC Packets
    i = 0
    count = 0
    while i < len(full_data):
        try:
            # Packet Length
            length, i = read_varint(full_data, i)
            if i + length > len(full_data):
                print(f"Packet {count}: Length {length} exceeds buffer (at {i})")
                break
                
            packet_data = full_data[i : i+length]
            i += length
            
            # Packet ID (VarInt)
            pid, offset = read_varint(packet_data, 0)
            payload = packet_data[offset:]
            
            print(f"Packet {count}: Len {length}, ID 0x{pid:x} ({pid}), Payload Len {len(payload)}")
            
            # Heuristics
            # If payload looks like Base64
            if count == 0:
                # Packet 0 should be the JSON response
                # It starts with a VarInt for string length
                # Skip the length VarInt
                val, jump = read_varint(payload, 0)
                json_data = payload[jump:]
                print(f"Packet 0 JSON len: {len(json_data)}")
                with open('packet0.json', 'wb') as f:
                    f.write(json_data)
            
            if len(payload) > 20:
                print(f"  Start: {payload[:20]}")
                try:
                    txt = payload.decode('ascii')
                    if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in txt):
                        print(f"  -> Base64 candidate")
                except:
                    pass
            
            count += 1
        except Exception as e:
            print(f"Parse error at {i}: {e}")
            break

parse_stream('stream1_server.txt')
