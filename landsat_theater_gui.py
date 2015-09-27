# jon klein, jtklein@alaska.edu
# .. simple GUI front-end for downloading and displaying landsat images

import wx
import time
import datetime
import pdb
import subprocess

from landsat_theater import landsat_search, landsat_download, annotate_landsat_images, record_image_filename

def main():
    app = wx.PySimpleApp()
    window = SetupFrame()
    app.MainLoop()

class SetupFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Landsat Theater", size = (500,300))
        
        self.init_ui()
        #self.Centre()
        self.Show(True)

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        gs = wx.GridSizer(6, 2, 5, 5)
    
        self.locationlabel = wx.StaticText(self, -1, "Location:")
        self.locationctl = wx.TextCtrl(self)

        self.startlabel = wx.StaticText(self, -1, "Start Date (MM/DD/YYYY):")
        self.startctl = wx.TextCtrl(self)

        self.endlabel = wx.StaticText(self, -1, "End Date: (MM/DD/YYYY):")
        self.endctl = wx.TextCtrl(self)

        self.recordlabel = wx.StaticText(self, -1, "Max Records:")
        self.maxrecords = wx.TextCtrl(self)

        self.cloudlabel = wx.StaticText(self, -1, "Max Cloud Coverage (%):")
        self.maxclouds = wx.TextCtrl(self)

        self.downloadbutton = wx.Button(self, id=-1, label='Download')
        self.displaybutton = wx.Button(self, id=-1, label='Display')

        gs.AddMany([\
            (self.locationlabel, 0, wx.EXPAND),\
            (self.locationctl, 0, wx.EXPAND),\
            (self.startlabel, 0, wx.EXPAND),\
            (self.startctl, 0, wx.EXPAND),\
            (self.endlabel, 0, wx.EXPAND),\
            (self.endctl, 0, wx.EXPAND),\
            (self.recordlabel, 0, wx.EXPAND),\
            (self.maxrecords, 0, wx.EXPAND),\
            (self.cloudlabel, 0, wx.EXPAND),\
            (self.maxclouds, 0, wx.EXPAND),\
            (self.downloadbutton, 0, wx.EXPAND),\
            (self.displaybutton, 0, wx.EXPAND)])

        
        self.locationctl.SetValue('Deadhorse, AK')
        self.startctl.SetValue('03/01/2015')
        self.endctl.SetValue('09/01/2015')
        self.maxclouds.SetValue('30')
        self.maxrecords.SetValue('10')
        
        self.downloadbutton.Bind(wx.EVT_BUTTON, self.downloadClick)
        self.displaybutton.Bind(wx.EVT_BUTTON, self.displayClick)
        vbox.Add(gs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)


    def downloadClick(self, event):
        print 'detected Download button press!'
        location = self.locationctl.GetValue()
        startdate = read_time(self.startctl.GetValue())
        enddate = read_time(self.endctl.GetValue())
        maxrecords = self.maxrecords.GetValue()
        maxclouds = self.maxclouds.GetValue()
        records = landsat_search(location, startdate = startdate, enddate = enddate, maxcloud = maxclouds, maxreturns = maxrecords)    
        landsat_download(records)
        annotate_landsat_images(records, location = location)
    
    def displayClick(self, event):
        print 'detected Display button press!'
        location = self.locationctl.GetValue()
        startdate = read_time(self.startctl.GetValue())
        enddate = read_time(self.endctl.GetValue())
        maxrecords = self.maxrecords.GetValue()
        maxclouds = self.maxclouds.GetValue()
        records = landsat_search(location, startdate = startdate, enddate = enddate, maxcloud = maxclouds, maxreturns = maxrecords)    
        print 'found {} records matching search'.format(len(records))
        spawn_landsat_displays(records) 

def spawn_landsat_displays(records, fullscreen = False, eog = False):
    windows = []
    for (i,record) in enumerate(records):
        imgname = record_image_filename(record, 'annotated')

        if eog:
            command = ['eog', imgname, '--new-instance']
            if fullscreen:
                command.append('--fullscreen')
            subprocess.Popen(command)
        else:
            command = ['cp', imgname, 'images/screen{}'.format(i)]
            subprocess.Popen(command)
        
        

def read_time(timestr):
    epochtime = time.mktime(time.strptime(timestr, '%m/%d/%Y'))
    return datetime.datetime.fromtimestamp(epochtime)

if __name__ == '__main__': 
    main()
