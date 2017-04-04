import codecs
import sys

import wx
import sheet

# from pywxgrideditmixin import PyWXGridEditMixin

# import sys
# app = wx.PySimpleApp()
# frame = wx.Frame(None, -1, size=(700,500), title = "wx.Grid example")
# 
# grid = wx.grid.Grid(frame)
# grid.CreateGrid(20,6)
# 
# # To add capability, mix it in, then set key handler, or add call to grid.Key() in your own handler
# wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)
# grid.__init_mixin__()
# 
# grid.SetDefaultColSize(70, 1)
# grid.EnableDragGridSize(False)
# 
# grid.SetCellValue(0,0,"Col is")
# grid.SetCellValue(1,0,"Read Only")
# grid.SetCellValue(1,1,"hello")
# grid.SetCellValue(2,1,"23")
# grid.SetCellValue(4,3,"greren")
# grid.SetCellValue(5,3,"geeges")
# 
# # make column 1 multiline, autowrap
# cattr = wx.grid.GridCellAttr()
# cattr.SetEditor(wx.grid.GridCellAutoWrapStringEditor())
# #cattr.SetRenderer(wx.grid.GridCellAutoWrapStringRenderer())
# grid.SetColAttr(1, cattr)
# 
# frame.Show(True)
# app.MainLoop()


newline=u'\r\n' if sys.platform=='win32' else u'\n'

class Grid(sheet.CSheet):
    def __init__(self, *args, **kwds):
        sheet.CSheet.__init__(self, *args, **kwds)
        self.rowcursor=0        
    
    def MakeArray(self):
        nrows=self.GetNumberRows()
        ncols=self.GetNumberCols()
        array=[]
        lastrow=0
        for rownum in range(0,nrows):
            line=[]
            for colnum in range(0,ncols):
                value=self.GetCellValue(rownum,colnum)
                line.append(value)
                if value!=u"":
                    lastrow=rownum+1
            array.append(line)
        return array[:lastrow]
    
    def Save(self, path, headers=False):
        output=self.MakeArray()
        if headers==True:
            line=[]
            for colnum in range(self.GetNumberCols()):
                line.append(self.GetColLabelValue(colnum))
            output.insert(0,line)
        f=codecs.open(path,'w','utf-8')
        for line in output:
            f.write(u'\t'.join(line))
            f.write(newline)
        f.close()
    
    def Fill(self,inputseqs):
        self.ClearGrid()
        nrows=self.GetNumberRows()
        nseqs=len(inputseqs)
        if nseqs>nrows:
            maxrow=nrows
            # an exception should be raised here, so that
            # the caller can alert the user
        else:
            maxrow=nseqs
        for rownum,row in enumerate(inputseqs[0:maxrow]):
            for colnum,value in enumerate(row):
                self.SetCellValue(rownum,colnum,value)
    
    def ReadFill(self, path):
        f=codecs.open(path,'rU','utf-8')
        inputseqs=[]
        for line in f:
            fields=line.strip(u'\n').split(u'\t')
            inputseqs.append(fields)
        f.close()
        self.Fill(inputseqs)
    
    def ImportData(self):
        dialog=wx.FileDialog(self.GetParent(), "Choose a file","",style=wx.OPEN)
        if wx.ID_OK==dialog.ShowModal():
            path=dialog.GetPath()
            self.ReadFill(path)
        else:
            pass
        dialog.Destroy()

    def SaveData(self, headers=False):
        dialog=wx.FileDialog(self,"Choose a file","",style=wx.SAVE)
        if wx.ID_OK==dialog.ShowModal():
            path=dialog.GetPath()
            self.Save(path, headers=headers)
        else:
            pass
        dialog.Destroy()

    def DisplayRow(self, fields, rownum=None):
        if rownum==None:
            rownum=self.rowcursor
        if rownum+1>=self.GetNumberRows():
            self.AppendRows(1)
        for colnum,value in enumerate(fields):
            self.SetCellValue(rownum,colnum,fields[colnum])
        self.rowcursor=rownum+1
        self.AutoSizeColumns()
        self.ForceRefresh()


class InputGrid(Grid):
    def __init__(self, *args, **kwds):
        Grid.__init__(self, *args, **kwds)
    
    def Segment(self, generator, replace=False):
        array=self.MakeArray()
        warnings=[]
        for rownum, (word, segments, expression) in enumerate(array):
            word=word.replace(u' ','')  # remove spaces
            if segments==u"" or replace==True:
                segments=generator.lookup(word)
                segments=u"" if segments==None else segments
                self.SetCellValue(rownum,1,segments)
                if word!="" and segments=="":
                    message=u"row %d: no segments found for %s" % (rownum+1, word)
                    warnings.append(message)
        return warnings
    

class ResultsGrid(Grid):
    def __init__(self, *args, **kwds):
        Grid.__init__(self, *args, **kwds)
    
