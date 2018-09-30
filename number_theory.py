def extended_gcd(aa, bb):
  lastrem, remainder = abs(aa), abs(bb)
  x, lastx, y, lasty = 0, 1, 1, 0
  while remainder:
    lastrem, (quotient, remainder) = remainder, divmod(lastrem, remainder)
    x, lastx = lastx - quotient*x, x
    y, lasty = lasty - quotient*y, y
  return lastrem, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)

def modinv(a, m):
  g, x, y = extended_gcd(a, m)
  if g != 1:
    raise ValueError
  return x % m

# Uses Newton's method
def iroot(k, n):
  u, s = n, n+1
  while u < s:
    s = u
    t = (k-1) * s + n // pow(s, k-1)
    u = t // k
  return s
