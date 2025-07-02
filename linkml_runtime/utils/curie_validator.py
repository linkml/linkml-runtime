import re

"""
Regex for CURIEs

These regex are directly derived from the collected ABNF in RFC3986
(except for DIGIT, ALPHA and HEXDIG, defined by RFC2234).

They should be processed with re.VERBOSE.
"""


### basics

DIGIT = r"[0-9]"

ALPHA = r"[A-Za-z]"

HEXDIG = r"[0-9ABCDEF]"

#   pct-encoded   = "%" HEXDIG HEXDIG
pct_encoded = r" %% %(HEXDIG)s %(HEXDIG)s" % locals()

ucschar = "(?: \u00a0-\ud7ff | \uf900-\ufdcf | \ufdf0-\uffef | \u10000-\u1fffD | \u20000-\u2fffD | \u30000-\u3fffD | \u40000-\u4fffD | \u50000-\u5fffD | \u60000-\u6fffD | \u70000-\u7fffD | \u80000-\u8fffD | \u90000-\u9fffD | \ua0000-\uafffD | \ub0000-\ubfffD | \uc0000-\ucfffD | \ud0000-\udfffD | \ue1000-\uefff )"

#   iunreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
iunreserved = r"(?: %(ALPHA)s | %(DIGIT)s | \- | \. | _ | ~ | %(ucschar)s )" % locals()

#   gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
gen_delims = r"(?: : | / | \? | \# | \[ | \] | @ )"

#   sub-delims    = "!" / "$" / "&" / "'" / "("
sub_delims = r"(?: ! | \$ | & | ' | \( | \) | \* | \+ | , | ; | = )"

#   ipchar         = iunreserved / pct-encoded / sub-delims / ":" / "@"
ipchar = r"(?: %(iunreserved)s | %(pct_encoded)s | %(sub_delims)s | : | @ )" % locals()

#   reserved      = gen-delims / sub-delims
reserved = r"(?: %(gen_delims)s | %(sub_delims)s )" % locals()

CombiningChar = "[\u0300-\u0345] | [\u0360-\u0361] | [\u0483-\u0486] | [\u0591-\u05a1] | [\u05a3-\u05b9] | [\u05bb-\u05bd] | \u05bf | [\u05c1-\u05c2] | \u05c4 | [\u064b-\u0652] | \u0670 | [\u06d6-\u06dc] | [\u06dd-\u06df] | [\u06e0-\u06e4] | [\u06e7-\u06e8] | [\u06ea-\u06ed] | [\u0901-\u0903] | \u093c | [\u093e-\u094c] | \u094d | [\u0951-\u0954] | [\u0962-\u0963] | [\u0981-\u0983] | \u09bc | \u09be | \u09bf | [\u09c0-\u09c4] | [\u09c7-\u09c8] | [\u09cb-\u09cd] | \u09d7 | [\u09e2-\u09e3] | \u0a02 | \u0a3c | \u0a3e | \u0a3f | [\u0a40-\u0a42] | [\u0a47-\u0a48] | [\u0a4b-\u0a4d] | [\u0a70-\u0a71] | [\u0a81-\u0a83] | \u0abc | [\u0abe-\u0ac5] | [\u0ac7-\u0ac9] | [\u0acb-\u0acd] | [\u0b01-\u0b03] | \u0b3c | [\u0b3e-\u0b43] | [\u0b47-\u0b48] | [\u0b4b-\u0b4d] | [\u0b56-\u0b57] | [\u0b82-\u0b83] | [\u0bbe-\u0bc2] | [\u0bc6-\u0bc8] | [\u0bca-\u0bcd] | \u0bd7 | [\u0c01-\u0c03] | [\u0c3e-\u0c44] | [\u0c46-\u0c48] | [\u0c4a-\u0c4d] | [\u0c55-\u0c56] | [\u0c82-\u0c83] | [\u0cbe-\u0cc4] | [\u0cc6-\u0cc8] | [\u0cca-\u0ccd] | [\u0cd5-\u0cd6] | [\u0d02-\u0d03] | [\u0d3e-\u0d43] | [\u0d46-\u0d48] | [\u0d4a-\u0d4d] | \u0d57 | \u0e31 | [\u0e34-\u0e3a] | [\u0e47-\u0e4e] | \u0eb1 | [\u0eb4-\u0eb9] | [\u0ebb-\u0ebc] | [\u0ec8-\u0ecd] | [\u0f18-\u0f19] | \u0f35 | \u0f37 | \u0f39 | \u0f3e | \u0f3f | [\u0f71-\u0f84] | [\u0f86-\u0f8b] | [\u0f90-\u0f95] | \u0f97 | [\u0f99-\u0fad] | [\u0fb1-\u0fb7] | \u0fb9 | [\u20d0-\u20dc] | \u20e1 | [\u302a-\u302f] | \u3099 | \u309a"

Extender = "\u00b7 | \u02d0 | \u02d1 | \u0387 | \u0640 | \u0e46 | \u0ec6 | \u3005 | [\u3031-\u3035] | [\u309d-\u309e] | [\u30fc-\u30fe]"

NCNameChar = r"(?: %(ALPHA)s | %(DIGIT)s | \. | \- | _ | %(CombiningChar)s | %(Extender)s )" % locals()

prefix = r"(?: %(ALPHA)s | _ ) (?: %(NCNameChar)s )*" % locals()

### iauthority

#   dec-octet     = DIGIT                 ; 0-9
#                 / %x31-39 DIGIT         ; 10-99
#                 / "1" 2DIGIT            ; 100-199
#                 / "2" %x30-34 DIGIT     ; 200-249
#                 / "25" %x30-35          ; 250-255
dec_octet = (
    r"""(?: %(DIGIT)s |
                    [1-9] %(DIGIT)s |
                    1 %(DIGIT)s{2} |
                    2 [0-4] %(DIGIT)s |
                    25 [0-5]
                )
"""
    % locals()
)

#  IPv4address   = dec-octet "." dec-octet "." dec-octet "." dec-octet
IPv4address = r"%(dec_octet)s \. %(dec_octet)s \. %(dec_octet)s \. %(dec_octet)s" % locals()

#  h16           = 1*4HEXDIG
h16 = r"(?: %(HEXDIG)s ){1,4}" % locals()

#  ls32          = ( h16 ":" h16 ) / IPv4address
ls32 = r"(?: (?: %(h16)s : %(h16)s ) | %(IPv4address)s )" % locals()

#   IPv6address   =                            6( h16 ":" ) ls32
#                 /                       "::" 5( h16 ":" ) ls32
#                 / [               h16 ] "::" 4( h16 ":" ) ls32
#                 / [ *1( h16 ":" ) h16 ] "::" 3( h16 ":" ) ls32
#                 / [ *2( h16 ":" ) h16 ] "::" 2( h16 ":" ) ls32
#                 / [ *3( h16 ":" ) h16 ] "::"    h16 ":"   ls32
#                 / [ *4( h16 ":" ) h16 ] "::"              ls32
#                 / [ *5( h16 ":" ) h16 ] "::"              h16
#                 / [ *6( h16 ":" ) h16 ] "::"
IPv6address = (
    r"""(?:                                  (?: %(h16)s : ){6} %(ls32)s |
                                                    :: (?: %(h16)s : ){5} %(ls32)s |
                                            %(h16)s :: (?: %(h16)s : ){4} %(ls32)s |
                         (?: %(h16)s : )    %(h16)s :: (?: %(h16)s : ){3} %(ls32)s |
                         (?: %(h16)s : ){2} %(h16)s :: (?: %(h16)s : ){2} %(ls32)s |
                         (?: %(h16)s : ){3} %(h16)s ::     %(h16)s :      %(ls32)s |
                         (?: %(h16)s : ){4} %(h16)s ::                    %(ls32)s |
                         (?: %(h16)s : ){5} %(h16)s ::                    %(h16)s  |
                         (?: %(h16)s : ){6} %(h16)s ::
                  )
"""
    % locals()
)

#   IPvFuture     = "v" 1*HEXDIG "." 1*( iunreserved / sub-delims / ":" )
IPvFuture = r"v %(HEXDIG)s+ \. (?: %(iunreserved)s | %(sub_delims)s | : )+" % locals()

#   IP-literal    = "[" ( IPv6address / IPvFuture  ) "]"
IP_literal = r"\[ (?: %(IPv6address)s | %(IPvFuture)s ) \]" % locals()

#   ireg-name      = *( iunreserved / pct-encoded / sub-delims )
ireg_name = r"(?: %(iunreserved)s | %(pct_encoded)s | %(sub_delims)s )*" % locals()

#   iuserinfo      = *( iunreserved / pct-encoded / sub-delims / ":" )
iuserinfo = r"(?: %(iunreserved)s | %(pct_encoded)s | %(sub_delims)s | : )" % locals()

#   ihost          = IP-literal / IPv4address / ireg-name
ihost = r"(?: %(IP_literal)s | %(IPv4address)s | %(ireg_name)s )" % locals()

#   iport          = *DIGIT
iport = r"(?: %(DIGIT)s )*" % locals()

#   iauthority     = [ iuserinfo "@" ] ihost [ ":" iport ]
iauthority = r"(?: %(iuserinfo)s @)? %(ihost)s (?: : %(iport)s)?" % locals()


### Path

#   isegment       = *ipchar
isegment = r"%(ipchar)s*" % locals()

#   isegment-nz    = 1*ipchar
isegment_nz = r"%(ipchar)s+" % locals()

#   isegment-nz-nc = 1*( iunreserved / pct-encoded / sub-delims / "@" )
#                 ; non-zero-length segment without any colon ":"
isegment_nz_nc = r"(?: %(iunreserved)s | %(pct_encoded)s | %(sub_delims)s | @ )+" % locals()

#   ipath-abempty  = *( "/" isegment )
ipath_abempty = r"(?: / %(isegment)s )*" % locals()

#   path-absolute = "/" [ isegment-nz *( "/" isegment ) ]
ipath_absolute = r"/ (?: %(isegment_nz)s (?: / %(isegment)s )* )?" % locals()

#   ipath-noscheme = isegment-nz-nc *( "/" isegment )
ipath_noscheme = r"%(isegment_nz_nc)s (?: / %(isegment)s )*" % locals()

#   ipath-rootless = isegment-nz *( "/" isegment )
ipath_rootless = r"%(isegment_nz)s (?: / %(isegment)s )*" % locals()

#   path-empty    = 0<ipchar>
ipath_empty = r""  ### FIXME

#   path          = path-abempty    ; begins with "/" or is empty
#                 / path-absolute   ; begins with "/" but not "//"
#                 / path-noscheme   ; begins with a non-colon segment
#                 / path-rootless   ; begins with a segment
#                 / path-empty      ; zero characters
path = (
    r"""(?: %(ipath_abempty)s |
               %(ipath_absolute)s |
               %(ipath_noscheme)s |
               %(ipath_rootless)s |
               %(ipath_empty)s
            )
"""
    % locals()
)

iprivate = r"[\uE000-\uF8FF] | [\uF0000-\uFFFFD] | [\u100000-\u10FFFD]"

### Query and Fragment

#   iquery         = *( ipchar / "/" / "?" )
iquery = r"(?: %(ipchar)s | %(iprivate)s | / | \? )*" % locals()

#   ifragment      = *( ipchar / "/" / "?" )
ifragment = r"(?: %(ipchar)s | / | \? )*" % locals()


### URIs


#   irelative-part = "//" iauthority ipath-abempty
#                 / ipath-absolute
#                 / path-noscheme
#                 / path-empty
irelative_part = (
    r"""(?: (?: // %(iauthority)s %(ipath_abempty)s ) |
                        %(ipath_absolute)s |
                        %(ipath_noscheme)s |
                        %(ipath_empty)s
                    )
"""
    % locals()
)

#   irelative-ref  = irelative-part [ "?" iquery ] [ "#" ifragment ]
irelative_ref = r"%(irelative_part)s (?: \? %(iquery)s)? (?: \# %(ifragment)s)?" % locals()

CURIE = r"(?: (?: (?: %(prefix)s )? : )? %(irelative_ref)s )" % locals()
curie_validator = re.compile(f"^{CURIE}$", re.VERBOSE)

#   URI-reference = URI / relative-ref
safe_CURIE = r"(?: \[ %(CURIE)s \] )" % locals()
safe_curie_validator = re.compile(f"^{safe_CURIE}$", re.VERBOSE)


def validate_curie(input):
    print(CURIE)
    return curie_validator.match(input)


def validate_safe_curie(input):
    return safe_curie_validator.match(input)
