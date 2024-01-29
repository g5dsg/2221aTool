
def get_bit(b, p):
    """Get a single bit out of a config byte."""
    return (b >> p) & 1

