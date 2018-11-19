import random

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

# Miller-Rabin: return value of false means n is not prime; return value of
# true means n is probably prime. k is the number of witness trials. Larger k
# implies greater accuracy.
def is_prime(n, k = 8):
  if n == 0 or n == 1:
    return False
  if n == 2:
    return True

  d = n - 1
  s = 0
  while d % 2 == 0:
    d = d // 2
    s += 1

  def witness(a):
    if pow(a, d, n) == 1:
      return False
    for i in range(s):
      if pow(a, 2**i * d, n) == n - 1:
        return False
    return True

  for i in range(k):
    a = random.randint(2, n - 1)
    if witness(a):
      return False
  return True

def chinese_remainder(a, n):
  s = 0
  prod = 1
  for n_i in n:
    prod *= n_i

  for n_i, a_i in zip(n, a):
    p = prod // n_i
    s += a_i * modinv(p, n_i) * p
  return s % prod

# Taken from
# eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python
def modular_sqrt(a, p):
  """ Find a quadratic residue (mod p) of 'a'. p
      must be an odd prime.

      Solve the congruence of the form:
        x^2 = a (mod p)
      And returns x. Note that p - x is also a root.

      0 is returned is no square root exists for
      these a and p.

      The Tonelli-Shanks algorithm is used (except
      for some simple cases in which the solution
      is known from an identity). This algorithm
      runs in polynomial time (unless the
      generalized Riemann hypothesis is false).
  """
  # Simple cases
  #
  if legendre_symbol(a, p) != 1:
    return 0
  elif a == 0:
    return 0
  elif p == 2:
    return p
  elif p % 4 == 3:
    return pow(a, (p + 1) // 4, p)

  # Partition p-1 to s * 2^e for an odd s (i.e.
  # reduce all the powers of 2 from p-1)
  #
  s = p - 1
  e = 0
  while s % 2 == 0:
    s //= 2
    e += 1

  # Find some 'n' with a legendre symbol n|p = -1.
  # Shouldn't take long.
  #
  n = 2
  while legendre_symbol(n, p) != -1:
    n += 1

  # Here be dragons!
  # Read the paper "Square roots from 1; 24, 51,
  # 10 to Dan Shanks" by Ezra Brown for more
  # information
  #

  # x is a guess of the square root that gets better
  # with each iteration.
  # b is the "fudge factor" - by how much we're off
  # with the guess. The invariant x^2 = ab (mod p)
  # is maintained throughout the loop.
  # g is used for successive powers of n to update
  # both a and b
  # r is the exponent - decreases with each update
  #
  x = pow(a, (s + 1) // 2, p)
  b = pow(a, s, p)
  g = pow(n, s, p)
  r = e

  while True:
    t = b
    m = 0
    for m in range(r):
      if t == 1:
        break
      t = pow(t, 2, p)

    if m == 0:
      return x

    gs = pow(g, 2 ** (r - m - 1), p)
    g = (gs * gs) % p
    x = (x * gs) % p
    b = (b * g) % p
    r = m

def legendre_symbol(a, p):
  """ Compute the Legendre symbol a|p using
      Euler's criterion. p is a prime, a is
      relatively prime to p (if p divides
      a, then a|p = 0)

      Returns 1 if a has a square root modulo
      p, -1 otherwise.
  """
  ls = pow(a, (p - 1) // 2, p)
  return -1 if ls == p - 1 else ls
