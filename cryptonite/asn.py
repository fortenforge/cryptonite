from util import *

# I tried very hard to leverage an existing python ASN.1 module to do what I
# wanted and came up lacking. So, I decided to write one myself.
def asn_decode(blob):
  blob = b64d(blob)
  return asn_decode_helper(blob)[0]

# Decodes the first ASN.1 content it parses and returns the rest of the blob
def asn_decode_helper(blob):
  if len(blob) == 0:
    return None, None

  c = ord(blob[0]) & 0b00011111
  blob = blob[1:]
  length, content = parse_length(blob)
  rest = content[length:]
  content = content[:length]
  # print 'c: {}'.format(c)
  # print 'length: {}'.format(length)
  # print 'content: {}'.format(repr(content))
  # print 'rest: {}'.format(repr(rest))
  # print '-----'

  if c == 0:
    return asn_decode_helper(blob)
  elif c == 1:
    # Boolean
    return ord(content[0]) != 0, rest
  elif c == 2:
    # Integer
    n = str_to_int(content)

    # two's complement nonsense
    h = ord(content[0]) >> 7
    n -= (h << (len(content) * 8))
    return n, rest
  elif c == 3:
    # Bit String
    # sometimes the bit string itself is DER-encoded. we'll try to decode it if
    # we can, and just return the raw bytes if we can't.
    try:
      decoded, _ = asn_decode_helper(content)
      return decoded, rest
    except Exception:
      return content, rest
  elif c == 6:
    # Object Identifier
    first_id = ord(content[0])
    first = '{}.{}'.format(first_id // 40, first_id % 40)
    after = ''
    content = content[1:]
    subident = 0
    for x in content:
      x = ord(x)
      if x >> 7 == 0:
        # terminal
        subident = (subident << 7) + x
        after += '.{}'.format(subident)
        subident = 0
      else:
        x ^= 0b10000000
        subident = (subident << 7) + x
    return (first + after if after else first), rest
  elif c == 16:
    # Sequence
    seq = []
    while len(content) > 0:
      next, content = asn_decode_helper(content)
      seq.append(next)
    return seq, rest
  else:
    # Something else
    return content, rest

# takes a blob starting with the length field, parses it, and returns the
# integer length, and the rest of the blob
def parse_length(blob):
  c = ord(blob[0])

  if c & 0b10000000 == 0:
    # short form
    return c, blob[1:]
  else:
    # long form
    blob = blob[1:]
    len_of_len = c ^ 0b10000000
    length = str_to_int(blob[:len_of_len])
    return length, blob[len_of_len:]

if __name__ == '__main__':
  pub_key = '''MIIEsTCCA5mgAwIBAgIQBOHnpNxc8vNtwCtCuF0VnzANBgkqhkiG9w0BAQsFADBsMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cuZGlnaWNlcnQuY29tMSswKQYDVQQDEyJEaWdpQ2VydCBIaWdoIEFzc3VyYW5jZSBFViBSb290IENBMB4XDTEzMTAyMjEyMDAwMFoXDTI4MTAyMjEyMDAwMFowcDELMAkGA1UEBhMCVVMxFTATBgNVBAoTDERpZ2lDZXJ0IEluYzEZMBcGA1UECxMQd3d3LmRpZ2ljZXJ0LmNvbTEvMC0GA1UEAxMmRGlnaUNlcnQgU0hBMiBIaWdoIEFzc3VyYW5jZSBTZXJ2ZXIgQ0EwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC24C/CJAbIbQRf1+8KZAayfSImZRauQkCbztyfn3YHPsMwVYcZuU+UDlqUH1VWtMICKq/QmO4LQNfE0DtyyBSe75CxEamu0si4QzrZCwvV1ZX1QK/IHe1NnF9Xt4ZQaJn1itrSxwUfqJfJ3KSxgoQtxq2lnMcZgqaFD15EWCo3j/018QsIJzJa9buLnqS9UdAn4t07QjOjBSjEuyjMmqwrIw14xnvmXnG3Sj4I+4G3FhahnSMSTeXXkgisdaScus0Xsh5ENWV/UyU50RwKmmMbGZJ0aAo3wsJSSMs5WqK24V3B3aAguCGikyZvFEohQcftbZvySC/zA/WiaJJTL17jAgMBAAGjggFJMIIBRTASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBhjAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwNAYIKwYBBQUHAQEEKDAmMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdpY2VydC5jb20wSwYDVR0fBEQwQjBAoD6gPIY6aHR0cDovL2NybDQuZGlnaWNlcnQuY29tL0RpZ2lDZXJ0SGlnaEFzc3VyYW5jZUVWUm9vdENBLmNybDA9BgNVHSAENjA0MDIGBFUdIAAwKjAoBggrBgEFBQcCARYcaHR0cHM6Ly93d3cuZGlnaWNlcnQuY29tL0NQUzAdBgNVHQ4EFgQUUWj/kK8CB3U8zNllZGKiErhZcjswHwYDVR0jBBgwFoAUsT7DaQP4v0cB1JgmGggC72NkK8MwDQYJKoZIhvcNAQELBQADggEBABiKlYkD5m3fXPwdaOpKj4PWUS+Na0QWnqxj9dJubISZi6qBcYRb7TROsLd5kinMLYBq8I4g4Xmk/gNHE+r1hspZcX30BJZr01lYPf7TMSVcGDiEo+afgv2MW5gxTs14nhr9hctJqvIni5ly/D6q1UEL2tU2ob8cbkdJf17ZSHwD2f2LSaCYJkJA69aSEaRkCldUxPUd1gJea6zuxICaEnL6VpPX/78whQYwvwt/Tv9XBZ0k7YXDK/umdaisLRbvfXknsuvCnQsH6qqF0wGjIChBWUMo0oHjqvbsezt3tkBigAVBRQHvFwY+3sAzm2fTYS5yh+Rp/BIAV0AecPUeybQ='''
  print repr(asn_decode(pub_key))
