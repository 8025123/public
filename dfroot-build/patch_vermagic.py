#!/usr/bin/env python3
"""把 dfroot.ko 的 vermagic 改成目标值（原地改写 .modinfo，ko 大小不变）"""
import struct, sys

KO = sys.argv[1] if len(sys.argv) > 1 else 'dfroot.ko'
TARGET = sys.argv[2] if len(sys.argv) > 2 else '5.10.246-gki-gb142569a7856'
NEW_VM = ('vermagic=%s SMP preempt mod_unload modversions aarch64' % TARGET).encode()

b = bytearray(open(KO, 'rb').read())
orig_size = len(b)

def sh(i):
    e = shoff + i*64
    return (struct.unpack_from('<I', b, e)[0],   # name off
            struct.unpack_from('<Q', b, e+24)[0], # offset
            struct.unpack_from('<Q', b, e+32)[0]) # size

def cstr(buf, off):
    end = buf.find(b'\x00', off)
    return bytes(buf[off:end])

shoff = struct.unpack_from('<Q', b, 0x28)[0]
shnum = struct.unpack_from('<H', b, 0x3c)[0]
shstrndx = struct.unpack_from('<H', b, 0x3e)[0]
_, so, ss = sh(shstrndx)
shstr = bytes(b[so:so+ss])

for i in range(shnum):
    nmo, moff, msz = sh(i)
    if cstr(shstr, nmo) == b'.modinfo':
        break
else:
    raise SystemExit('no .modinfo found')

old = bytes(b[moff:moff+msz])
print('orig .modinfo size=%d' % msz)
lines = [p for p in old.split(b'\x00') if p.strip()]
keep = [p for p in lines if not p.startswith(b'vermagic=')]
plan = b''.join(p + b'\x00' for p in keep) + NEW_VM + b'\x00'

# 空间不够就先丢弃可选行
for drop in (b'description=', b'srcversion=', b'depends=', b'license='):
    if len(plan) <= msz:
        break
    keep = [p for p in keep if not p.startswith(drop)]
    plan = b''.join(p + b'\x00' for p in keep) + NEW_VM + b'\x00'
    print('dropped optional line prefix: %s' % drop.decode())

if len(plan) > msz:
    raise SystemExit('need %d bytes but .modinfo only has %d (ko too small for in-place patch)' % (len(plan), msz))

b[moff:moff+msz] = plan + b'\x00' * (msz - len(plan))
assert len(b) == orig_size
open(KO, 'wb').write(bytes(b))

# 校验
c = open(KO, 'rb').read()
i = c.find(b'vermagic=')
print('RESULT:', c[i:c.find(b'\x00', i)].decode())
