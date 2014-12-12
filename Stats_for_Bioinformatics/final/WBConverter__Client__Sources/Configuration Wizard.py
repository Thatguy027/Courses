#! usr/bin/python
# -*- coding: utf-8 -*-

####
##  Copyright © 2010 CIML
##
##  This file is part of WormBase Converter.
##
##  WormBase Converter is free software: you can redistribute it  
##  and/or modify it under the terms of the GNU General Public License  
##  as published by the Free Software Foundation, either version 3 of 
##  the License, or (at your option) any later version.
##
##  WormBase Converter is distributed in the hope that it will be 
##  useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
##  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with WormBase Converter. If not, see <http://www.gnu.org/licenses/>.
####

from Tkinter import *
import ttk, tkMessageBox
import ConfigParser, os, urllib
import updater


class MyConfigParser (ConfigParser.ConfigParser):
    
    filename = ""
    
    def __init__ (self, filename):
        self.filename = filename
        ConfigParser.ConfigParser.__init__(self)
        ConfigParser.ConfigParser.read(self, self.filename)
    
    def set(self, section, option, value):
        ConfigParser.ConfigParser.set(self, section, option, value)
        ConfigParser.ConfigParser.write(self, open(self.filename, 'w'))

    def setboolean(self, section, option, value):
        try :
            if (bool(value) == True) :
                self.set(section, option, 'True')
            else :
                self.set(section, option, 'False')
        except :
            self.set(section, option, 'False')




class Configuration_Wizard :

    __CFG = None
    __window = None
    
    __installation_profile = None
    __language = None
    
    __server_host = None
    __res_server_host = None
    __check_updates = None
    __check_parameters = None
    

    def __init__ (self) :
        
            # Test la présence du fichier de configuration
        try :
            self.__CFG = MyConfigParser('config.ini')
            self.__CFG.get('WORMBASE', 'language')
        except :
            tkMessageBox.showinfo("ERROR", "Unable to find the file : \"config.ini\".\nThe Configuration Wizard must be launch in the installation folder...")
        else :
            self.__display_window ()
        
        
        
    def __display_window (self) :
        
        self.__window = Tk()
        self.__window.title("Configuration Wizard")
        self.__window.resizable(width=False, height=False)
        
        
            # Configuration de base
        gr = Frame()
        gr.pack(padx=5, pady=5)  
          
        self.__installation_profile = StringVar()
        Label(gr, text="Installation profile :").grid(row=1, column=1, sticky=W)
        Entry(gr, textvariable=self.__installation_profile, justify=LEFT, state='readonly').grid(row=1, column=2, padx=5, pady=5, sticky=W+E)
        
        self.__language = StringVar()
        Label(gr, text="Language :").grid(row=2, column=1, sticky=W)
        self.lang_combo = ttk.Combobox(gr, textvariable=self.__language, state='readonly')
        self.lang_combo.grid(row=2, column=2, padx=5, pady=5, sticky=W+E)
      
        
            # Configuration spécifique          
        if (self.__CFG.get('UPDATE', 'install') == 'SERVER') :
            ttk.Separator(gr, orient=HORIZONTAL).grid(row=6, column=1, columnspan=2, padx=80, pady=5, sticky=W+E)

            self.__server_host = StringVar()
            Label(gr, text="Host address :").grid(row=7, column=1, sticky=W)
            Entry(gr, textvariable=self.__server_host, justify=LEFT).grid(row=7, column=2, padx=5, pady=2, sticky=W+E)
            self.__server_host.set("http://")

            self.__res_server_host = StringVar()
            Button(gr, text="Test the server", command=self.__test_server_host).grid(row=8, column=1, padx=5, pady=2)
            self.res_entry = Entry(gr, textvariable=self.__res_server_host, justify=LEFT, state='readonly')
            self.res_entry.grid(row=8, column=2, padx=5, pady=2, sticky=W+E)
            
            ttk.Separator(gr, orient=HORIZONTAL).grid(row=9, column=1, columnspan=2, padx=80, pady=5, sticky=W+E)
            
            self.__check_updates = IntVar()
            Checkbutton(gr, text=' Check new releases on startup', justify=LEFT, variable=self.__check_updates).grid(row=10, column=1, columnspan=2, padx=5, pady=2, sticky=W)    
            self.__check_updates.set(True)
        
            self.__check_parameters = IntVar()
            Checkbutton(gr, text=' Check update parameters on startup', justify=LEFT, variable=self.__check_parameters).grid(row=11, column=1, columnspan=2, padx=5, pady=2, sticky=W)    
            self.__check_parameters.set(True)


            # Boutons de sauvegarde
        ttk.Separator(gr, orient=HORIZONTAL).grid(row=12, column=1, columnspan=2, padx=15, pady=5, sticky=W+E)
        
        Button(gr, text="SAVE THIS CONFIGURATION", command=self.__save).grid(row=13, column=1, columnspan=2, padx=5, pady=5)

         
        self.__set_default_settings()

        self.__window.mainloop()
        
        
        
    def __set_default_settings (self) :
    
            # Profil d'installation
        if (self.__CFG.get('UPDATE', 'install') == 'LOCAL') :
            self.__installation_profile.set("LOCAL installation")
        elif (self.__CFG.getboolean('UPDATE', 'access') == True) :
            self.__installation_profile.set("CLIENT installation (Admin)")     
        else :
            self.__installation_profile.set("CLIENT installation")
        
            # Liste des langues
        lang = self.__get_languages()
        self.lang_combo.config(values=lang)
        self.__language.set(lang[0])
        
        
        
    def __test_server_host (self) :
        if (self.__server_host.get()[:7] != "http://") : self.__server_host.set("http://" + self.__server_host.get())
        if (self.__server_host.get()[-1] != "/") : self.__server_host.set(self.__server_host.get() + "/")
    
        try :
            f = urllib.urlopen(self.__server_host.get() + 'launcher.php')
            res = f.read().strip().replace('\r\n', '\n').split('\n')
            if (res[-1] != "<html><body>HOST VALID</body></html>") :
                raise
        except :
            self.res_entry.config(fg = 'red')
            self.__res_server_host.set("ERROR : Bad host address")
        else :
            self.res_entry.config(fg = 'green3')
            self.__res_server_host.set("OK : Host address valid")
            

        
    def __get_languages (self) :
        languages = []
    
        for lang in os.listdir('language') :
            languages.append(lang)
            
        return languages
        
        
    def __save (self) :
        
        self.__CFG.set('WORMBASE', 'language', "language/" + self.__language.get())
        
        if (self.__CFG.get('UPDATE', 'install') == "SERVER") :
            self.__CFG.set('UPDATE', 'server_host', self.__server_host.get())
            self.__CFG.setboolean('WORMBASE', 'update_on_startup', self.__check_updates.get())
            self.__CFG.setboolean('WORMBASE', 'params_on_startup', self.__check_parameters.get())

        self.__window.destroy()


cfg = Configuration_Wizard()


