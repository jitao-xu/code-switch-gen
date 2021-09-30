# Code-Switching Generation

Source code for synthetic Code-Switched sentence generation of paper:

[**Can You Traducir This? Machine Translation for Code-Switched Input**](https://aclanthology.org/2021.calcs-1.11/)

Jitao Xu and François Yvon

## Requirements

You need to install [`fast_align`](https://github.com/clab/fast_align) and un [unfold tool](https://github.com/jmcrego/corpora-tools/tree/master/src).

## Usage

The general procedure is to first preprocess and tokenize the data, then apply fast_align and the unfold technique to get the alignment units between sentences. After that, random replacement of alignment units is performed, and finally apply BPE on it. 

Steps after `preprocess.sh` are included in the script `build_translation_data.sh`, both `word_alignment.sh` and `align_replace_multi_label_fix.py` are needed to generate CS data.

## Citation

```
@inproceedings{xu-yvon-2021-traducir,
    title = "Can You Traducir This? Machine Translation for Code-Switched Input",
    author = "Xu, Jitao  and
      Yvon, Fran{\c{c}}ois",
    booktitle = "Proceedings of the Fifth Workshop on Computational Approaches to Linguistic Code-Switching",
    month = jun,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.calcs-1.11",
    doi = "10.18653/v1/2021.calcs-1.11",
    pages = "84--94",
    abstract = "Code-Switching (CSW) is a common phenomenon that occurs in multilingual geographic or social contexts, which raises challenging problems for natural language processing tools. We focus here on Machine Translation (MT) of CSW texts, where we aim to simultaneously disentangle and translate the two mixed languages. Due to the lack of actual translated CSW data, we generate artificial training data from regular parallel texts. Experiments show this training strategy yields MT systems that surpass multilingual systems for code-switched texts. These results are confirmed in an alternative task aimed at providing contextual translations for a L2 writing assistant.",
}
```
