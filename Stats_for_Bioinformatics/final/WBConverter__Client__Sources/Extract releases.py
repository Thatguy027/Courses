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
import sys, tkFileDialog, tkMessageBox, ConfigParser, gzip, tarfile



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
            



class Installation_updates_Wizard :

    __CFG = None

    __window = None
    __archive_file = None
    __first_available = None
    __last_available = None
    __first_installed = None
    __last_installed = None
    __first_to_install = None
    __last_to_install = None   
    __install_ACeDB = None 
    
    
    def __init__ (self, cmd = False) :
    
            # Test la présence du fichier de configuration
        try :
            self.__CFG = MyConfigParser('config.ini')
            self.__CFG.get('WORMBASE', 'language')      # test de la validité du fichier
        except :
            if (cmd == False) :
                tkMessageBox.showinfo("ERROR", "Unable to find the file : \"config.ini\".\nThe Installation updates Wizard must be launch in the installation folder...")
            else :
                print "Unable to find the file : \"config.ini\".\nThe Installation updates Wizard must be launch in the installation folder..."
        else :
            if (cmd == False) :
                self.__display_window ()
       
               
    
    def __display_window (self) :
    
            # Création de la fenêtre
        self.__window = Tk()
        self.__window.title("Installation updates Wizard")
        self.__window.resizable(width=False, height=False)
        
            # Widgets
        gr = Frame(self.__window)
        gr.pack(padx=5, pady=5)
        
        self.__archive_file = StringVar()
        Label(gr, text="WormBase releases\n(archive) :").grid(row=1, column=1, sticky=W)
        Entry(gr, textvariable=self.__archive_file, justify=LEFT, state='readonly').grid(row=1, column=2, columnspan=2, padx=5, sticky=W+E)
        Button(gr, text="Change", command=self.__change_file).grid(row=1, column=4, padx=5, pady=10)

   
        Label(gr, text="RELEASES AVAILABLE :").grid(row=3, column=1, columnspan=4, sticky=W)
        
        self.__first_available = StringVar()
        Label(gr, text="First :").grid(row=4, column=1, sticky=E)
        Entry(gr, textvariable=self.__first_available, justify=CENTER, state='readonly', width=6).grid(row=4, column=2, padx=5, pady=2, sticky=W)

        self.__last_available = StringVar()
        Label(gr, text="Last :").grid(row=4, column=3, sticky=E)
        Entry(gr, textvariable=self.__last_available, justify=CENTER, state='readonly', width=6).grid(row=4, column=4, padx=5, pady=2, sticky=W)

        Label(gr, text="").grid(row=5, column=1, columnspan=4, sticky=W)


        Label(gr, text="RELEASES INSTALLED :").grid(row=6, column=1, columnspan=4, sticky=W)
        
        self.__first_installed = StringVar()
        Label(gr, text="First :").grid(row=7, column=1, sticky=E)
        Entry(gr, textvariable=self.__first_installed, justify=CENTER, state='readonly', width=6).grid(row=7, column=2, padx=5, pady=2, sticky=W)

        self.__last_installed = StringVar()
        Label(gr, text="Last :").grid(row=7, column=3, sticky=E)
        Entry(gr, textvariable=self.__last_installed, justify=CENTER, state='readonly', width=6).grid(row=7, column=4, padx=5, pady=2, sticky=W)        

        Label(gr, text="").grid(row=8, column=1, columnspan=4, sticky=W)


        Label(gr, text="RELEASES TO INSTALL :").grid(row=9, column=1, columnspan=4, sticky=W)
        
        self.__first_to_install = StringVar()
        Label(gr, text="First :").grid(row=10, column=1, sticky=E)
        Entry(gr, textvariable=self.__first_to_install, justify=CENTER, width=6).grid(row=10, column=2, padx=5, pady=2, sticky=W)

        self.__last_to_install = StringVar()
        Label(gr, text="Last :").grid(row=10, column=3, sticky=E)
        Entry(gr, textvariable=self.__last_to_install, justify=CENTER, width=6).grid(row=10, column=4, padx=5, pady=2, sticky=W)        

        Label(gr, text="").grid(row=11, column=1, columnspan=4, sticky=W)

        self.__install_ACeDB = IntVar()
        self.check_ACeDB = Checkbutton(gr, text=' Install all the ACeDB files', justify=LEFT, variable=self.__install_ACeDB)
        self.check_ACeDB.grid(row=12, column=1, columnspan=4, padx=5, pady=2, sticky=W)    


        self.btn_install = Button(gr, text="INSTALL THE NEW RELEASES", command=self.__install)
        self.btn_install.grid(row=13, column=1, columnspan=4, padx=5, pady=10, sticky=W+E)


        self.__set_default_settings()
   
        self.__window.mainloop()
   
   
   
    def __set_default_settings (self) :
            
            # Récupération des versions installées
        releases_installed = self.get_releases_installed()
        if (len(releases_installed) != 0) :
            self.__first_installed.set(str(releases_installed[0]))
            self.__last_installed.set(str(releases_installed[-1]))
        else :
            self.__first_installed.set('---')
            self.__last_installed.set('---')
   
            # Désactivation de l'installation des fichiers ACeDB, si installation SERVEUR
        if (self.__CFG.get('UPDATE', 'install') != 'LOCAL') :
            self.__install_ACeDB.set(False)
            self.check_ACeDB.config(state='disabled')
   
            # Désactivation du bouton INSTALLER
        self.btn_install.config(state='disabled')

        

    def get_releases_installed (self) :
        
        r_installed = self.__CFG.get('WORMBASE', 'releases')
        r_installed = r_installed.strip().split(',')
        releases_installed = []
 
        for r in r_installed :
            if (r != '') : releases_installed.append(int(r))
            
        releases_installed.sort()
        
        return releases_installed
        

   
    def __change_file (self) :  

        filename = tkFileDialog.askopenfilename(title="WormBase releases archive", filetypes=[('Archive', '*.tar.gz')])

        if (filename != "") and (str(filename) != "()") :
            self.__test_file(filename)
                
                
              
    def __test_file (self, filename) :

        self.__archive_file.set(filename)               # affichage du chemin de l'archive
        self.btn_install.config(state='normal')         # activation du bouton d'installation
            
            # Récupération des versions disponibles
        releases_available = self.__get_releases_available()
        self.__first_available.set(str(releases_available[0]))
        self.__last_available.set(str(releases_available[-1]))
            

   
    def __get_releases_available (self) :
        releases = []

        tar = tarfile.open(self.__archive_file.get(), "r:gz")
        for file_info in tar:
            if (file_info.name[:18] == "geneIDs/geneIDs.WS") :
                releases.append(int(file_info.name[18:]))
        tar.close()            
                
        releases.sort()

        return releases  
        
   
   
    def __install (self) :
    
            # Vérifie que les numéros de versions soient bien renseignées
        try :
            first = int(self.__first_to_install.get())
            last = int(self.__last_to_install.get())
        except :
            tkMessageBox.showerror("Missing releases", "Please enter the first and the last release to install.")
            return
   
            # Vérifie que les versions renseignées sont présentes dans le package     
        if (first < int(self.__first_available.get())) or (last > int(self.__last_available.get())) :
            tkMessageBox.showerror("Releases outside", "The first or the latest release is outside the limits (versions available).")
            return


            # Ouverture de l'archive
        tar = tarfile.open(self.__archive_file.get(), "r:gz")

            # Installation des fichiers souhaités à partir du package
        for r in range(first, last+1) :
            tar.extract("geneIDs/geneIDs.WS" + str(r), 'wormbase/')

        for r in range(first, last) :
            tar.extract("geneEvols/WS" + str(r) + "-WS" + str(r+1), 'wormbase/')
            
        if (self.__install_ACeDB.get() == True) :
            acedb_files = []

            for file_info in tar:
                if (file_info.name[:12] == "ACeDB/ACeDB_") :
                    acedb_files.append(file_info.name)
                    
            for file in acedb_files :
                tar.extract(file, 'wormbase/temp/')
                
            # Fermeture de l'archive
        tar.close()

   
            # Ajout des version dans le fichier config.ini
        releases_installed = self.get_releases_installed()
        
        for r in range(first, last+1) :
            releases_installed.append(r)
        releases_installed = list(set(releases_installed))
        releases_installed.sort()
        
        releases_installed__str = ""
        for r in releases_installed :
            releases_installed__str = releases_installed__str + str(r) + ","
        
        self.__CFG.set('WORMBASE', 'releases', releases_installed__str[:-1])
        
        tkMessageBox.showinfo("Installation complete", "The WormBase releases have been installed.")       
   



   

    # MODE GRAPHIQUE
if (len(sys.argv) == 1) :
    wizard = Installation_updates_Wizard()



    # MODE LIGNE DE COMMANDE :
    #   argv[1] -> archive
    #   argv[2] -> installer les fichiers ACeDB ? (facultatif)   [yes/no (par défaut)]
else :

        # Vérification du fichier
    if (sys.argv[1][-7:] != ".tar.gz") :
        print "The file specified is not a 'tar.gz' file."
        sys.exit(1)

        # Ouverture de l'archive
    tar = tarfile.open(sys.argv[1], "r:gz")

    releases = []
    for file in tar :
            # copie des fichiers geneIDs et geneEvols
        if (file.name[:18] == "geneIDs/geneIDs.WS") :
            tar.extract(file, 'wormbase/')
            releases.append(int(file.name[18:]))
            
        if (file.name[:12] == "geneEvols/WS") : tar.extract(file, 'wormbase/')

            # copie des fichiers ACeDB si besoin
        if (file.name[:12] == "ACeDB/ACeDB_") :
            if (len(sys.argv) >= 3) and (sys.argv[2].lower() == "yes") :
                tar.extract(file, 'wormbase/temp/')
                
        # Fermeture de l'archive
    tar.close()


        # Ajout des version dans le fichier config.ini
    wizard = Installation_updates_Wizard(cmd = True)
    CFG = MyConfigParser('config.ini')
    releases_installed = wizard.get_releases_installed()

    releases.sort()
    for r in range(releases[0], releases[-1]+1) :
        releases_installed.append(r)
    releases_installed = list(set(releases_installed))
    releases_installed.sort()
    
    releases_installed__str = ""
    for r in releases_installed :
        releases_installed__str = releases_installed__str + str(r) + ","
        
    CFG.set('WORMBASE', 'releases', releases_installed__str[:-1])   
     
    print "Installation complete : The WormBase releases have been installed."


