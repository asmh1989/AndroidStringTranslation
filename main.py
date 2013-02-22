#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

from xml.etree import ElementTree
import os
import sys
import subprocess
import time

current_path=os.getcwd()
searchPath=["/frameworks/base/core"]#, "/frameworks/base/packages", "/packages/apps/", "/packages/providers", "/packages/wallpapers"]
sample_path="/home/sun/svn/x3002m"
translate="es"

def run_process(sub):
    while 1:
        ret=subprocess.Popen.poll(sub)
        if ret==0:
            break;
        elif ret is None:
            time.sleep(1)
        else:
            break;

def _readXMLStrings(xml1):
    root=ElementTree.fromstring(open(xml1).read())
    strings_node=root.iter("string")
    L_String=list()
    for node in strings_node:
        #if node.attrib.has_key("name")>0:
        name=""
        name=node.attrib['name']
        product=""
        if node.attrib.has_key("product")>0:
            product=node.attrib['product']
        text=""
        text=node.text
        node_string=[name, product, text]
        L_String.append(node_string)
#    for l in L_String:
#        print "string name=%s, product=%s, value=%s"%(l[0], l[1], l[2])
    string_array_node=root.iter("string-array")
    L_String_array=list()
    for node in string_array_node:
        name=""
        name=node.attrib['name']
        translatable=""
        if node.attrib.has_key("translatable")>0:
            translatable=node.attrib['translatable']
        if translatable == "":
            L_Item=list()
            for item in node.iter("item"):
                text=""
                text=item.text
                L_Item.append(text)
            node_string_array=[name, L_Item]
            L_String_array.append(node_string_array)
#    for l in L_String_array:
#        print "string-array name = %s item:"%(l[0])
#        print (l[1])
    plurals_node=root.iter("plurals")
    L_Plurals=list()
    for node in plurals_node:
        name=""
        name=node.attrib['name']
        plurals_item_node=node.iter("item")
        L_Item=list()
        for item in plurals_item_node:
            quantity=""
            quantity=item.attrib['quantity']
            text=""
            text=item.text
            plurals=[quantity, text]
            L_Item.append(plurals)
        plurals=[name, L_Item]
        L_Plurals.append(plurals)
#    for l in L_Plurals:
#        print "plurals name = %s item : "%l[0]
#        print (l[1])
    return [L_String, L_String_array, L_Plurals]

def _isTheOne(i, a, b, strings, transStrings):
    if i == 0:          # for <strings>
        return transStrings[b][2] != "" and strings[a][1] == transStrings[b][1]
    if i == 1:          # for <strings-array>
        return len(strings[a][1]) == len(transStrings[b][1])
    if i == 2:          # for <plurals>
        return len(strings[a][1]) == len(transStrings[b][1])
        

def _compareStringXML(xml1, xml2):
    out = open("temp.out", 'w')
    needTransStrings=list()
    for t in range(0, len(xml1)):
        strings=sorted(xml1[t], key=lambda x:x[0]) 
        translateStrings=sorted(xml2[t], key=lambda x:x[0])
        willDel=list()
        a=0
        b=0
        print "strings's len = %d, translateStrings's len = %d"%(len(strings), len(translateStrings))
        
        for i in range(0,len(strings)):
            name=strings[a][0];
            if not b < len(translateStrings):
                break;
            transName=translateStrings[b][0];
            print "name = %s, transName = %s cmp = %d"%(name, transName, cmp(name, transName))
            while cmp(name, transName) > 0:
                transName=translateStrings[++b][0]
            if cmp(name, transName) == 0:
                if _isTheOne(t, a, b, strings, translateStrings):
                    print "strings name=%s has been translated, a=%d, b=%d"%(name, a, b)
                    num=[a, b]
                    b+=1
                    willDel.append(num)
            a+=1
    
        while len(willDel) > 0:
            number=willDel.pop()
            print "will del (%d, %d)"%(number[0], number[1])
            del strings[number[0]]
            del translateStrings[number[1]]
        print >> out, " --------------%d------------"%t
        for i in strings:
            print >> out, "strings name = %s, product=%s, values = %s"%(i[0], i[1], i[2])
        print >> out, "strings's len = %d, translateStrings's len = %d"%(len(strings), len(translateStrings))
        needTransStrings.append(strings)


def _readXML(xml1, xml2):
    stringsXML=_readXMLStrings(xml1)
    translateStringsXML=_readXMLStrings(xml2)
    needTranslateStringXML=_compareStringXML(stringsXML, translateStringsXML)

def _start(dirPath):
    search_path=sample_path+dirPath
    list=os.listdir(sample_path+dirPath)
    for path in list:
        path=search_path+"/"+path
        print "path = %s"%path
        if os.path.exists(path+"/res"):
            stringsXML=path+"/res/values/strings.xml"
            stringsTransXML=path+"/res/values-es/strings.xml"
            _readXML(stringsXML, stringsTransXML)


if __name__=='__main__':
    par_len=len(sys.argv)
    print "pwd = %s"%current_path
#    if par_len<2:
#        print "missing a valid parameters"
#        exit(1)
#    p=sys.argv[0]

    for path in searchPath:
        print "path = %s"%path
        _start(path)
        
    

LANGUAGES=( "中文简体 [Chinese](values-zh-rCN)",
            "中文繁体 [Chinese](values-zh-rTW)",
            "英语[English](values-en-rUS)",
            "英语[English](values-en-rAU)",
            "英语[English](values-en-rCA)",
            "英语[English](values-en-rGB)",
            "英语[English](values-en-rIE)",
            "英语[English](values-en-rIN)",
            "英语[English](values-en-rNZ)",
            "英语[English](values-en-rSG)",
            "英语[English](values-en-rZA)",
            "俄语 [русский](values-ru-rRU)",
            "法语 [français](values-fr-rFR)",
            "法语 [français](values-fr-rBE)",
            "法语 [français](values-fr-rCA)",
            "法语 [français](values-fr-rCH)",
            "罗马尼亚语 [român](values-ro-rRO)",
            "西班牙语 [español](values-es-rES)",
            "波兰语 [polski](values-pl-rPL)",
            "意大利语[italiano](values-it-rIT)",
            "乌克兰语 [Український](values-uk-rUA)",
            "匈牙利语 [magyar](values-hu-rHU)",
            "德语 [Deutsch](values-de-rDE)",
            "德语 [Deutsch](values-de-rAT)",
            "德语 [Deutsch](values-de-rCH)",
            "德语 [Deutsch](values-de-rLI)",
            "希腊语 [ελληνικά](values-el-rGR)",
            "葡萄牙语 [português](values-pt-rPT)",
            "葡萄牙语 [português](values-pt-rBR)",
            "印尼语 [Bahasa Indonesia](values-id-rID)",
            "马来西亚语 [Melayu](values-ms)",
            "土耳其语 [Türk](values-tr-rTR)",
            "越南语 [Việt](values-vi-rVN)",
            "阿拉伯语 [العربية](values-ar-rEG)",
            "阿拉伯语 [العربية](values-ar-rIL)",
            "保加利亚语 [български](values-bg-rBG)",
            "捷克语 [český](values-cs-rCZ)",
            "丹麦语 [dansk](values-da-rDK)",
            "波斯语 [فارسی](values-fa)",
            "芬兰语 [suomi](values-fi-rFI)",
            "希伯来语 [עברית](values-he-rIL)",
            "北印度语 [हिंदी](values-hi-rIN)",
            "克罗地亚语 [hrvatski](values-hr-rHR)",
            "印度尼西亚语 [Bahasa Indonesia](values-in-rID)",
            "立陶宛语 [Lietuvos](values-it-rCH)",
            "立陶宛语 [Lietuvos](values-it-rIT)",
            "拉脱维亚语 [Latvijas](values-lv-rLV)",
            "挪威语 [norske](values-nb-rNO)",
            "荷兰语 [Nederlands](values-nl-rNL)",
            "荷兰语 [Nederlands](values-nl-rBE)",
            "拉丁语 [Latin](values-rm-rCH)",
            "斯洛伐克语 [slovenských](values-sk-rSK)",
            "斯洛文尼亚语 [slovenski](values-sl-rSI)",
            "塞尔维亚语 [српском језику](values-sr-rRS)",
            "瑞典 [Svenskt](values-sv-rSE)",
            "泰语 [ภาษาไทย](values-th-rTH)",
            "韩语 [한국의](values-ko-rKR)",
            "加泰罗尼亚语 [Català](values-ca-rES)",
            "日语 [日本語](values-ja-rJP)")

