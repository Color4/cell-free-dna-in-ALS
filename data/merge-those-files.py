import csv
import os
__author__ = "Arya Boudaie"
# This program merges two sorted files containing site positions, one with a list of large dmr regions of the genome
# with many methylation sites, and one with a list of single methylation sites. The program adds on the average
# methylation values for the tissues to the file with the dmr regions corresponding with those methylation sites.

new_file_name = "rrbs-merged.txt"
# Helper functions:


def flint(x):
    """
    Returns float(int(x)) - since the spreadsheet had numbers as floats
    :param x: String representing number
    :return: int of that number
    """
    return int(float(x))


def chr_int(x):
    """
    Turns chromosome number into number, needed since chromosome could be x or y
    :param x: chromosome value
    :return: int representing value of chromosome (or arbitrarily large numbers for x and y.
    """
    # Arbitrary values for x and y, they just need to be > 21.
    values = {"x": 100, "y": 101}
    x = x.lower()
    if x in values:
        return values[x]
    try:
        return int(x)
    except ValueError:
        raise ValueError("Not sure what to do with value {}".format(x))


# New file to be written, delete old one first
if os.path.exists(new_file_name):
    os.remove(new_file_name)

with open("../refer-meth/reference_matrix.txt") as dmr_file, open("RRBS_DMRs_v2.txt") as meth_file, open(new_file_name, "w") as new_csv:
    dmr_regions = csv.reader(dmr_file, delimiter="\t")
    methylation_sites = csv.reader(meth_file, delimiter="\t")
    new_file = csv.writer(new_csv, delimiter="\t")

    # For ease of remembering which are the small regions and which are the larger ones, I'll refer to them
    # as big and small
    big_line = next(dmr_regions)  # header for dmr file
    small_line = next(methylation_sites)  # header for methylation sites
    new_file.writerow(big_line + small_line[3:])  # write the combination of the headers

    # Advance both lines
    big_line = next(dmr_regions)
    small_line = next(methylation_sites)

    prev_row = []  # Keep track of the previous row written (useful for the end).
    i = 0
    # The strategy is to read through the lines in turn, starting with the first line of each, and advancing them
    # according to a set of rules to find the corresponding methylation sites for each dmr region.
    # Runs in O(n+m) time, where n is number of dmr regions, and m is number of methylation sites.
    finished_through_files = False
    while not finished_through_files:
        i+=1
        print(i)

        while not big_line:
            big_line = next(dmr_regions)
        while not small_line:
            small_line = next(methylation_sites)
        try:
            # chromosome of methylation site
            small_chr = chr_int(small_line[0])
            # start and end of methylation site (end = start+1)
            small_start, small_end = flint(small_line[1]), flint(small_line[2])

            # chromosome of dmr
            big_chr = chr_int(big_line[0])
            # smart and end of dmr (could be arbitrarily large)
            big_start, big_end = flint(big_line[1]), flint(big_line[2])

            # If chromosomes don't match, then advance the smaller line.
            if small_chr < big_chr:
                small_line = next(methylation_sites)
            elif big_chr < small_chr:
                # Every time we advance the DMR file, we must first write it's contents to the new file, since
                new_file.writerow(big_line)
                prev_row = big_line
                big_line = next(dmr_regions)
            # Now we know chr is equal on both
            else:
                # If the start of the small gap is less than the big gap, we know that methylation site doesn't fit
                # in the DMR, and we need to try the next methylation site
                if small_start < big_start:
                    small_line = next(methylation_sites)

                # This is the case where the methylation site fits in the DMR
                elif big_start <= small_start <= big_end and big_start <= small_end <= big_end:
                    # the row to write (all the data except the chr, start, end of small_line)
                    row = big_line + small_line[3:]
                    keep_going = True
                    # We need to go through the next methylation sites to see if they fits in this DMR before we write
                    # the row. We can stop at the first one that doesn't fit.
                    while keep_going:
                        # Get the data for the next line
                        small_line = next(methylation_sites)
                        small_chr = chr_int(small_line[0])
                        small_start, small_end = flint(small_line[1]), flint(small_line[2])
                        # Break out of the loop of the chromosomes don't match, or the next site is not in range
                        if small_chr != big_chr:
                            keep_going = False
                        elif big_start <= small_start <= big_end and big_start <= small_end <= big_end:
                            row += small_line[3:]
                        else:
                            keep_going = False
                    # Write the row
                    new_file.writerow(row)
                    prev_row = row
                    # Advance the DMR file to the next line, as we have written every methylation site that fits
                    # in this DMR. Note that small_line has already advanced to the next one above.
                    big_line = next(dmr_regions)
                # small interval not in range of DMR, but since small_start > big start, we have to check the next DMR
                else:
                    new_file.writerow(big_line)
                    prev_row = big_line
                    big_line = next(dmr_regions)
        # If we get here, either we went through all the methylation sites, or all the DMRs.
        # If we still have some more DMRs, we want to write them, and then finish.
        except StopIteration:
            # We kept track of the previous row written, in case the last value for big_line was not written.
            if prev_row != big_line:
                new_file.writerow(big_line)
            # Write the remaining DMR rows, then exit the loop.
            for line in dmr_regions:
                if line: new_file.writerow(line)
            finished_through_files = True
