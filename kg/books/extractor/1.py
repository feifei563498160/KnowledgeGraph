                    try:
                        print 'thread: ',j*cpus+i
                        p.apply_async(match_single,args=(pattern,data,j*cpus+i,))