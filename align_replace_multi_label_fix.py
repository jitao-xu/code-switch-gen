# -*- coding: utf-8 -*-

import numpy as np
import os
import argparse
import multiprocessing
from functools import partial
from time import time
import string

def random_replace(s_unit, t_unit, num_rep, mode):
    """
    Randomly replace units in src by corresponding alignment in t_unit.
    
    s_unit: Source alignment units.
    t_unit: Target alignment units.
    num_rep: Maximum number of replacement.
    mode: replace source sentence or target sentence.
    return: The replaced code-switched sentence.
    """

    u_len = len(s_unit)
    choices = list(range(u_len))
    replaced_pos = []
    for u in range(num_rep):
        if not choices:
            break
        valid = False
        ind = np.random.choice(choices)
        while not valid:
            if s_unit[ind] == "" or t_unit[ind] == "":
                choices.remove(ind)
                if not choices:
                    break
                ind = np.random.choice(choices)
                continue
            else:
                key_list = list(t_unit[ind]) # list of keys
                if not is_consecutive(key_list):
                    choices.remove(ind)
                    if not choices:
                        break
                    ind = np.random.choice(choices)
                    continue
                else:
                    valid = True
        if choices:
            if mode == "src":
                s_unit[ind] = t_unit[ind]
            else:
                t_unit[ind] = s_unit[ind]
            replaced_pos.append(ind)
            choices.remove(ind)
    if mode == "src":
        return s_unit, replaced_pos
    else:
        return t_unit, replaced_pos


def is_consecutive(sequence):
    return sequence[-1] - sequence[0] == len(sequence) - 1 and len(sequence) == len(set(sequence))


def get_replace_number(mode, src_len, tgt_len, max_rep):
    """
    Compute the number of replacement. The probability of keep the original sentence is 0.5. 
    The probability of replace once is 0.25, replace twice is 0.125, etc.

    mode: Replace source sentence or target sentence.
    src_len: Source sentence length.
    tgt_len: Target sentence length.
    max_rep: Maximum replacement number.

    return: Computed replacement number.
    """

    length = src_len if mode == "src" else tgt_len
    max_rep = min(int(length / 2), max_rep)
    prob = [1 / (2 ** (i + 1)) for i in range(max_rep + 1)]
    prob.append(1 / 2 ** (max_rep + 1))
    num_rep = np.random.choice(len(prob), p=prob)
    while num_rep == max_rep + 1:
        num_rep = np.random.choice(len(prob), p=prob)

    return num_rep


def get_align_units(line):
    """
    Return seperated alignment units from alignment line.
    
    line: line in alignment file.
    return: list of source unit and list of target unit.
    """
    
    tmp = line.split(" ")
    s_unit = []
    t_unit = []
    for unit in tmp:
        tmp_unit = unit.split("‖")
        if len(tmp_unit) < 2:
            print(line)
            raise ValueError("tmp_unit length < 2")
        if tmp_unit[0] == "":
            s_unit.append("")
        else:
            s_unit.append({int(u.split("．", 1)[0]): u.split("．", 1)[1] for u in tmp_unit[0].split("＿")})
        if tmp_unit[1] == "":
            t_unit.append("")
        else:
            try:
                t_unit.append({int(u.split("．", 1)[0]): u.split("．", 1)[1] for u in tmp_unit[1].split("＿")})
            except:
                print(line + "\n")
                for u in tmp_unit[1].split("＿"):
                    print(u)
                    print(u.split("．")[0], u.split("．")[1])
                raise ValueError("t_unit[1].split problem")
    return s_unit, t_unit


def equal_values(dict_1, dict_2):
    return " ".join(v for _, v in dict_1.items()) == " ".join(v for _, v in dict_2.items())


# def replace_alignment(fsrc, ftgt, falign, args, i):
def replace_alignment(i):
    """
    Replace alignments by randomly selecting source or target sentence uniformly.
    
    fsrc: source sentences
    ftgt: target sentences
    falign: alignment sentences
    args: input arguments
    i: index in total lines
    return: replaced sentence and corresponding tags
    """

    # src = fsrc[i].replace("\n", "")
    src = fsrc[i].strip()
    # src_len = len(src.split(" "))
    src_len = len(src.split())

    # tgt = ftgt[i].replace("\n", "")
    tgt = ftgt[i].strip()
    # tgt_len = len(tgt.split(" "))
    tgt_len = len(tgt.split())

    line = falign[i].replace("\n", "")
    mode = "src" if np.random.choice(2) == 0 else "tgt"
    num_rep = get_replace_number(mode, src_len, tgt_len, args.max_rep)
    s_unit, t_unit = get_align_units(line) 

    if num_rep == 0:
        if mode == "src": 
            # cs_sentence = src.split(" ")
            cs_sentence = src.split()
            labels = ["lang1" for t in range(src_len)]
        else:
            # cs_sentence = tgt.split(" ")
            cs_sentence = tgt.split()
            labels = ["lang2" for t in range(tgt_len)]

    else:
        replaced_units, pos = random_replace(s_unit.copy(), t_unit.copy(), num_rep, mode)

        if not replaced_units: # No valid alignments
            # cs_sentence = src.split(" ") if mode == "src" else tgt.split(" ")
            cs_sentence = src.split() if mode == "src" else tgt.split()
            labels = ["lang1" for t in range(src_len)] if mode == "src" else ["lang2" for t in range(tgt_len)]
            # return cs, label

        else:
            cs_sentence = []
            labels = []
            if mode == "src":
                for u in range(len(replaced_units)):
                    if replaced_units[u] != "":
                        cs_sentence += [replaced_units[u][k] for k in replaced_units[u]] 
                        amb = True if s_unit[u] and t_unit[u] and is_consecutive(list(t_unit[u])) and equal_values(s_unit[u], t_unit[u]) else False
                        for k in replaced_units[u]:
                            if amb:
                                labels.append("ambiguous")
                            elif u in pos:
                                labels.append("lang2")
                            else:
                                labels.append("lang1")
                # cs_sentence = " ".join(tok for tok in cs_sentence) + "\n"
                # labels = " ".join(l for l in labels) + "\n"

            else:
                # tgt_dict = {ind: tok for ind, tok in enumerate(tgt.split(" "))}
                # label_dict = {ind: "lang2" for ind in range(len(tgt.split(" ")))}
                tgt_dict = {ind: tok for ind, tok in enumerate(tgt.split())}
                label_dict = {ind: "lang2" for ind in range(len(tgt.split()))}
                amb = []
                for u in range(len(t_unit)):
                    if s_unit[u] and t_unit[u] and is_consecutive(list(t_unit[u])) and equal_values(s_unit[u], t_unit[u]):
                        amb.append(True)
                        for ind in t_unit[u]:
                            label_dict[ind] = "ambiguous"
                    else:
                        amb.append(False)

                for p in pos:
                    unit_inds = list(t_unit[p])
                    if not amb[p]:
                        tgt_dict[unit_inds[0]] = " ".join(replaced_units[p][k] for k in replaced_units[p])
                        label_dict[unit_inds[0]] = " ".join("lang1" for k in replaced_units[p])
                        for ind in range(1, len(unit_inds)):
                            tgt_dict[unit_inds[ind]] = ""
                            label_dict[unit_inds[ind]] = ""
                # cs_sentence = " ".join(tgt_dict[k] for k in tgt_dict if tgt_dict[k] != "") + "\n"
                # labels = " ".join(label_dict[k] for k in label_dict if label_dict[k] != "") + "\n"
                for k in tgt_dict:
                    if tgt_dict[k] != "":
                        cs_sentence += tgt_dict[k].split(" ")
                        labels += label_dict[k].split(" ")

    for t, tok in enumerate(cs_sentence):
        if tok in punc:
            labels[t] = "other"
        else:
            is_punc = True
            for c in tok:
                if c not in punc:
                    is_punc = False
                    break
            if is_punc:
                labels[t] = "other"

    cs_sentence = " ".join(tok for tok in cs_sentence) + "\n"
    labels = " ".join(l for l in labels) + "\n"
    dominant = "lang1" if mode == "src" else "lang2"

    return cs_sentence, labels, dominant


def main():

    print("Start multi process")
    tic = time()
    pool = multiprocessing.Pool()
    length = len(falign)

    # func = partial(replace_alignment, fsrc, ftgt, falign, args)
    res = pool.map(replace_alignment, list(range(length)), chunksize=length // os.cpu_count())
    # res = pool.imap(func, list(range(length)), chunksize=length // os.cpu_count())
    # res = pool.map(func, list(range(length)), chunksize=16384)
    # res = pool.map(replace_alignment, list(range(length)), chunksize=16384)
    toc = time()
    print("Multi process time: %.2f s" % (toc - tic))
    print("End multi process")

    with open(args.output + ".cs", "w") as f, open(args.output + ".label", "w") as fl, open(args.output + ".dom", "w") as fd:
        for r in res:
            f.write(r[0])
            fl.write(r[1])
            fd.write(r[2] + "\n")
            

if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-s', '--source', required=True, help="Source file path")
    argparser.add_argument('-t', '--target', required=True, help="Target file path")
    argparser.add_argument('-a', '--align', required=True, help="Alignmenet file path")
    argparser.add_argument('-n', '--max_rep', type=int, default=3, help="Maximum replacement per sentence")
    argparser.add_argument('-o', '--output', required=True, help="Output prefix")
    args = argparser.parse_args()

    print("Loading source and target files...")
    fsrc = [l for l in open(args.source)]
    ftgt = [l for l in open(args.target)]
    print("Loading alignment file...")
    falign = [l for l in open(args.align)]
    punc = set(string.punctuation + string.digits)
    for p in ["&amp;", "&#124;", "&lt;", "&gt;", "&apos;", "&quot;", "&#91;", "&#93;"]:
        punc.add(p)

    main()
