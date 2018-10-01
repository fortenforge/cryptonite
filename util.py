import math
import base64
import binascii

def unhex(a):
  return binascii.unhexlify(a)

def enhex(a):
  return binascii.hexlify(a)

def b64e(a):
  return base64.b64encode(a)

def b64d(a):
  return base64.b64decode(a)

def int_to_str(n):
  s = '{0:x}'.format(n)
  s = '0' + s if len(s) % 2 == 1 else s
  return unhex(s)

def str_to_int(s):
  return int(enhex(s), 16)

def xor(c, k):
  if len(c) < len(k):
    return xor(k, c)
  p = ''
  l = len(k)
  for i in range(len(c)):
    p += chr(ord(c[i])^ord(k[i%l]))
  return p
