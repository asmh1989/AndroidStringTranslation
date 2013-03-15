#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

from xml.etree import ElementTree
from xml.dom.minidom import Document
from xlwt import Workbook
from xlrd import open_workbook
import os
import subprocess
import time
import re
import sys
reload(sys) 
sys.setdefaultencoding('utf-8') 

current_path=os.getcwd()
searchPath=["/frameworks/base/core", "/frameworks/base/packages", "/packages/apps", "/packages/providers", "/packages/wallpapers"]
sample_path="/home/sun/sshfs/data/sunminhua/svn/R20_0503_SC"  # for my ubuntu
project_name='R20SC'
#sample_path="/Volumes/linux/R10"       #for my Mac OS
translate="values-in-rID"
sheetName=["f$b$c$", "f$b$p$", "p$a$", "p$p$", "p$w$"]
XMLlist=["/res/values/strings.xml", "/res/values/arrays.xml"]

xlsStrings=Workbook()
xlsArrays=Workbook()

xlsList=[xlsStrings, xlsArrays]


def run_process(sub):
    while 1:
        ret=subprocess.Popen.poll(sub)
        if ret==0:
            break;
        elif ret is None:
            time.sleep(1)
        else:
            break;

def _isAdd(text):
        temp=str(text)
        p=re.compile('[a-z]+', re.IGNORECASE)
        m=p.search(temp)
        return  m

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
        if not (text is None) and _isAdd(text):
            #print "name = %s, text=%s"%(name, str(text))
            if text[0] == '\n':
                #print "find name=%s, text=%s"%(name, text)
                ll=str(text).split("\n")
                newText=''
                for l in ll:
                    if not l.isspace():
                        newText += l.strip()
                    #print "line : %s"%l 
                text=newText
                #print "xiu find  name=%s, text=%s"%(name, text)
            node_string=[name, product, text]
            L_String.append(node_string)
#        else :
#            print "not add text = %s"%str(text)
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
                if _isAdd(text):
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
            if _isAdd(text):
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
    #out = open("temp.out", 'w')
    needTransStrings=list()
    for t in range(0, len(xml1)):
        strings=sorted(xml1[t], key=lambda x:x[0])
        translateStrings=list()
        if len(xml2) > 0:
            translateStrings=sorted(xml2[t], key=lambda x:x[0])
        willDel=list()
        a=0
        b=0
        #print "strings's len = %d, translateStrings's len = %d"%(len(strings), len(translateStrings))
        
        for i in range(0,len(strings)):
            name=strings[a][0];
            if not b < len(translateStrings):
                break;
            transName=translateStrings[b][0];
#            print "name = %s, transName = %s cmp = %d"%(name, transName, cmp(name, transName))
            while cmp(name, transName) > 0:
                b+=1
                transName=translateStrings[b][0]
            if cmp(name, transName) == 0:
                if _isTheOne(t, a, b, strings, translateStrings):
         #           print "strings name=%s has been translated, a=%d, b=%d"%(name, a, b)
                    num=[a, b]
                    b+=1
                    willDel.append(num)
            a+=1
    
        while len(willDel) > 0:
            number=willDel.pop()
        #    print "will del (%d, %d)"%(number[0], number[1])
            del strings[number[0]]
            del translateStrings[number[1]]
#        print >> out, " --------------%d------------"%t
#        for i in strings:
#            print >> out, "strings name = %s, product=%s, values = %s"%(i[0], i[1], i[2])
#        print >> out, "strings's len = %d, translateStrings's len = %d"%(len(strings), len(translateStrings))
        needTransStrings.append(strings)

    return needTransStrings


def _readXML(xml1, xml2, sheetname, xls):
    stringsXML=_readXMLStrings(xml1)
    translateStringsXML=list()
    if os.path.exists(xml2):
        translateStringsXML=_readXMLStrings(xml2)
    needTranslateStringXML=_compareStringXML(stringsXML, translateStringsXML)
    sheet=""

    if len(needTranslateStringXML[0]) + len(needTranslateStringXML[1]) + len(needTranslateStringXML[2]) < 1:
        print "sheetName = %s is null"%sheetname
        return
    else:
        #print needTranslateStringXML
        print "sheetName = %s will add"%sheetname
        sheet=xls.add_sheet(sheetname)
        sheet.write(0,1,"values")
        sheet.write(0,2,translate)
        
    l=1
    for strings in needTranslateStringXML[0]:  #<strings>
        if strings[1] == "":
            sheet.write(l,0,strings[0])
        else:
            sheet.write(l,0,strings[0]+":"+strings[1])
        sheet.write(l,1,strings[2])
        l+=1
    for arrays in needTranslateStringXML[1]:    #<strings-array>
        sheet.write(l,0,"arrays:"+arrays[0])
        l+=1
        for item in arrays[1]:
            sheet.write(l,0,"item")
            sheet.write(l,1,item)
            l+=1
        sheet.write(l,0,"arrays:"+arrays[0])
        l+=1
    for plurals in needTranslateStringXML[2]:   #<plurals>
        #print "i = %d, plurals[0] = %s"%(l, plurals[0])
        sheet.write(l,0,"plurals:"+plurals[0])
        l+=1
        for item in plurals[1]:
            sheet.write(l,0,item[0])
            sheet.write(l,1,item[1])
            l+=1
        sheet.write(l,0,"plurals:"+plurals[0])
        l+=1
def mkNewdir(path):
    if not os.path.exists(path):
        os.mkdir(path) 

def getNewFile(project, sheetName):
    newfile=''
    pwd = current_path+'/'+project
    mkNewdir(pwd)
    for path in sheetName.split('$'):
        if path == 'f':
            newfile += '/frameworks'
        elif path == 'b':
            newfile += '/base'
        elif path == 'c':
            newfile += '/core'
        elif path == 'p':
                newfile += '/packages'
        elif path == 'a':
            newfile += '/apps'
        elif path == 'p':
            newfile += '/providers'
        elif path == 'w':
            newfile += '/wallpapers'
        else :
            newfile += '/'+path
        mkNewdir(pwd+newfile)
    print "need mkdir file = %s"%newfile
    newfile += '/res'
    mkNewdir(pwd+newfile)
    return newfile


def _startParse(project, xlsname, whichxml):
    wb=open_workbook(xlsname, encoding_override='cp1252')
    for sheet in wb.sheets():
        tlan = []
        print "sheet name = %s, rows = %d, cols = %d"%(sheet.name, sheet.nrows, sheet.ncols)
        for lan in range(2, sheet.ncols):
            print "add trans lan = %s"%sheet.cell(0, lan).value
            tlan.append(sheet.cell(0, lan).value)
        newfile= current_path+'/'+project+getNewFile(project, sheet.name)
        for lan in range(2, sheet.ncols):
            curPath = newfile+'/'+sheet.cell(0, lan).value
            mkNewdir(curPath)
            xml = Document()
            xmlstore = xml.createElement('resources')
            xmlstore.setAttribute('xmlns:xliff', 'urn:oasis:names:tc:xliff:document:1.2')
            xml.appendChild(xmlstore)
            for row in range(1, sheet.nrows):
                rowValue = sheet.cell(row, 0).value
                print 'row = %s, rowValue = %s, len = %d'%(row, rowValue, len(rowValue))
                whichValue=''    
                if not rowValue.find('arrays'): 
                    print "find arrays........."
                    whichValue='array'
                elif not rowValue.find('plurals'):
                    whichValue='plurals'
                else :
                    whichValue='strings'
                if whichValue != 'strings':
                    if (row+1) == sheet.nrows:
                        print '......last line'
                        continue
                    elif not sheet.cell(row+1,0).value.find(whichValue+'s:'):
                        print '......close..close'
                        continue
                    else:
                        atter=sheet.cell(row, 0).value.split(':')[1]
                        #print 'find row = %s, value = %s'%(row, rowValue)
                        cell = ''
                        secName=''
                        if whichValue == 'array':
                            secName='string-array'
                        elif whichValue == 'plurals':
                            secName='plurals'
                        cell = xml.createElement(secName)
                        print '%s name=%s'%(secName,atter)
                        cell.setAttribute('name', atter)
                        xmlstore.appendChild(cell)
                        while row < (sheet.nrows - 1):
                            row = row+1
                            if not sheet.cell(row, 0).value.find(whichValue+'s:'):
                                break;
                            name=sheet.cell(row, 0).value
                            value=sheet.cell(row, lan).value
                            if len(value) > 0:
                                print 'cell %s, value = %s'%(name, value)
                                cell2 = xml.createElement(name)
                                cell2_value=xml.createTextNode(value)
                                cell2.appendChild(cell2_value)
                                cell.appendChild(cell2)
                        row = row+1
                else:
                    StringName=sheet.cell(row,0).value
                    StringValue=sheet.cell(row,lan).value
                    if len(StringValue) > 0:
                        cellStrings=xml.createElement('string')
                        cellStrings.setAttribute('name', StringName)
                        cellString_value=xml.createTextNode(StringValue)
                        cellStrings.appendChild(cellString_value)
                        xmlstore.appendChild(cellStrings)

                #elif rowValue.find('plurals:'):
                #    whichValue='plural'
                #else :
                #    whichValues='string'
            f=open(curPath+'/'+whichxml+'.xml', 'w')
            f.write(xml.toprettyxml(indent = '\t', newl='\n', encoding='utf-8'))
            f.close()



def _verifyStr(str1, path, xml):
    if not os.path.exists(path+"/res/"+str1+xml):
        string = str1.split('-')
        if len(string) > 2:
            #print "str[0] = %s, str[1] = %s"%(string[0], string[1])
            str1=path+"/res/"+string[0]+'-'+string[1]+xml
    return str1
    
def _start(dirPath, whichSearch):
    search_path=sample_path+dirPath
    listpath=os.listdir(sample_path+dirPath)
    for path in listpath:
        #print "current Path = %s"%path
        packageName=path
        path=search_path+"/"+path
#        print "path = %s"%path
        if os.path.exists(path+"/res"):
            stringsXML=path+"/res/values/strings.xml"
            if len(packageName) > 24:
                packageName=packageName[0:23]       
            stringsTransXML=_verifyStr(translate, path, "/strings.xml")
            #print "find other stringsTransXML = %s"%stringsTransXML
            sheet_Name=sheetName[whichSearch]+packageName
            #sheet=xlsStrings.add_sheet(sheet_Name)
            _readXML(stringsXML, stringsTransXML, sheet_Name, xlsStrings)
            stringsXML=path+"/res/values/arrays.xml"
            if not os.path.exists(stringsXML):
                continue
            if len(packageName) > 24:
                packageName=packageName[0:23]
            stringsTransXML=_verifyStr(translate, path, "/arrays.xml")

            sheet_Name=sheetName[whichSearch]+packageName
            #sheet=xlsArrays.add_sheet(sheet_Name)
            _readXML(stringsXML, stringsTransXML, sheet_Name, xlsArrays)



if __name__=='__main__':
    par_len=len(sys.argv)
    print "pwd = %s"%current_path
#    if par_len<2:
#        print "missing a valid parameters"
#        exit(1)
    isExport = 0 
    if par_len > 1:
        translate=sys.argv[1]
        for i in range(1, par_len):
            if sys.argv[i] == '-r' :
                isExport = 1
    if isExport == 0 :
        for i in range(0,len(searchPath)):
            print "path = %s"%searchPath[i]
            _start(searchPath[i], i)
        xlsStrings.save(project_name +"_strings.xls")
        xlsArrays.save(project_name+"_arrays.xls")
    else :
        print "start export from xls"
        list = os.listdir(current_path)
        for name in list:
            if name.find(".xls") > 0:
                project = name.split('_')[0]                  #need has only one '-' string
                whichxml=''
                if name.find('arrays'):
                    whichxml = 'arrays'
                elif name.find('strings'):
                    whichxml = 'strings'
                print "find xls : %s project=%s whichxml=%s"%(name, project, whichxml)
                _startParse(project, current_path+"/"+name, whichxml)
        
    

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
