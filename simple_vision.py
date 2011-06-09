def compare_segments(seg1, seg2, slen, cwl):
    """ Do a simple template match of two segments to find the best match
    
        (Matlab version: equivalent to rs_compare_segments)
    """
    
    # assume a large difference
    min_diff = 1e6
    diffs = zeros(slen)
    min_offset = None
    
    for offset in range(0, slen-1):
        cdiff = abs( seg1[offset:cwl-1]  - seg2[0: cwl-offset-1] )
        cdiff = sum(cdiff) / (cwl - offset)
        diffs[slen - offset] = cdiff
        if(cdiff < min_diff):
            min_diff = cdiff
            min_offset = offset
    
    for offset in range(0, slen-1):
        cdiff = abs( seg1[0:cwl-offset-1] - seg2[offset:cwl] )
        cdiff = sum(cdiff) / (cwl - offset)
        diffs[slen+offset] = cdiff
        if(cdiff < min_diff):
            min_diff = cdiff
            min_offset = -offset
    
    return (min_offset, min_diff)