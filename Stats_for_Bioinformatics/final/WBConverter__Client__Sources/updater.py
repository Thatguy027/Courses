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
import ttk, tkFont
import ConfigParser, sys, threading, update


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

            
            
            
            
class Update_WormBase :

    __parent = None                     # Fenêtre parente (Convertisseur)
    __window = None                     # Fenêtre
    
    CFG = None                          # Configuration / Options
    LANG = None                         # Langue utilisée
    __updates_enabled = None            # Bouton UPDATE activé (True | False)
    
    __up = None                         # Instance de MAJ

    __server_host = None                # Adresse du serveur (dans le cas d'une installation client/serveur)
    __auto_correct = None               # Option de relancement automatique de la MAJ d'une release si une erreur est survenue lors de la récupération des changements
    __save_update_log = None            # Option d'enregistrement du log des MAJ
    __save_acedb_file = None            # Option d'enregistrement/archivage des fichiers ACeDB

    __ftp_host = None                   # Hôte du serveur FTP (pour la récupération des GeneIDs)
    __ftp_port = None                   # Port du serveur FTP
    __ftp_login = None                  # Login pour la connexion au serveur FTP
    __ftp_password = None               # Mot de passe pour la connexion au serveur FTP
    __ftp_regexp = None                 # Expression régulière du chemin (+ nom du fichier) utilisé par les archives de GeneIDs

    __db_host = None                    # [idem] pour la base de données
    __db_port = None                    # [idem] pour la base de données
    __db_login = None                   # [idem] pour la base de données
    __db_password = None                # [idem] pour la base de données

    __letter_host = None                # [idem] pour la "letter"
    __letter_port = None                # [idem] pour la "letter"
    __letter_login = None               # [idem] pour la "letter"
    __letter_password = None            # [idem] pour la "letter"
    __letter_regexp = None              # [idem] pour la "letter"

    __thread_update = None              # Lancement de la MAJ sur le serveur
    __thread_params = None              # Enregistrement des paramètres de MAJ sur le serveur


    def __init__(self, parent, cfg_filename, lang_filename, updates_enabled = True) :

            # Enregistrement des paramètres
        self.__parent = parent
        self.CFG = MyConfigParser(cfg_filename)
        self.LANG = MyConfigParser(lang_filename)
        self.__updates_enabled = updates_enabled

        self.display_window()



    def __del__ (self) :
        
            # Fermeture des Thread forcée
        try :
            self.__thread_update._Thread__stop()
            self.__thread_params._Thread__stop()
        except :
            pass
        


    def display_window (self) :
        """Affichage de la fenêtre Updater."""

            # Autorisation de modification des paramètres
        if (self.CFG.getboolean('UPDATE', 'access') == True) :
            mod = NORMAL
            mod2 = NORMAL
        else :
            mod = 'readonly'
            mod2 = 'disabled'

            # Création de la fenêtre
        self.__window = Toplevel(self.__parent)
        self.__window.title(self.LANG.get('UPDATER', 'window_title'))
        self.__window.resizable(width=False, height=False)

            # Conteneur général
        grille = Frame(self.__window)
        grille.pack(side=LEFT, padx=5, pady=5)


            # Création des onglets
        notebook = ttk.Notebook(grille)
        gr1 = ttk.Frame(notebook)
        gr2 = ttk.Frame(notebook)
        gr3 = ttk.Frame(notebook)
        gr4 = ttk.Frame(notebook)
        notebook.add(gr1, text=self.LANG.get('UPDATER', 'other'))
        notebook.add(gr2, text=self.LANG.get('UPDATER', 'ftp'))
        notebook.add(gr3, text=self.LANG.get('UPDATER', 'database'))
        notebook.add(gr4, text=self.LANG.get('UPDATER', 'letter'))
        notebook.grid(row=1, column=1, columnspan=3, pady=5)

        font_italic = tkFont.Font()
        font_italic.config(family='courier', size=9, slant=tkFont.ITALIC)

            # 1er onglet : Général
        self.__server_host = StringVar()
        Label(gr1, text=self.LANG.get('UPDATER', 'server_host'), justify=LEFT).grid(row=1, column=1, padx=5, pady=5, sticky=W)
        self.server_host = Entry(gr1, textvariable=self.__server_host, justify=LEFT, width=17)
        self.server_host.grid(row=1, column=2, padx=5, pady=5, sticky=W+E) 

        self.__auto_correct = IntVar()
        Checkbutton(gr1, text=' ' + self.LANG.get('UPDATER', 'auto_correct'), justify=LEFT, variable=self.__auto_correct, state=mod2, command=self.tkerr).grid(row=2, column=1, columnspan=2, padx=2, pady=2, sticky=W)    

        self.__save_update_log = IntVar()
        Checkbutton(gr1, text=' ' + self.LANG.get('UPDATER', 'save_update_log'), variable=self.__save_update_log, state=mod2, command=self.tkerr).grid(row=3, column=1, columnspan=2, padx=2, pady=2, sticky=W)    

        self.__save_acedb_file  = IntVar()
        Checkbutton(gr1, text=' ' + self.LANG.get('UPDATER', 'save_acedb_file') % ('\n'), justify=LEFT, variable=self.__save_acedb_file, state=mod2, command=self.tkerr).grid(row=4, column=1, columnspan=2, padx=2, pady=2, sticky=W)    

            # 2ème onglet : Options du serveur FTP (GeneIDs)
        self.__ftp_host = StringVar()
        Label(gr2, text=self.LANG.get('UPDATER', 'ftp_host'), justify=LEFT).grid(row=1, column=1, padx=5, pady=5, sticky=W)
        Entry(gr2, textvariable=self.__ftp_host, justify=LEFT, state=mod, width=25).grid(row=1, column=2, padx=5, pady=5, sticky=W+E)

        self.__ftp_port = StringVar()
        Label(gr2, text=self.LANG.get('UPDATER', 'ftp_port'), justify=LEFT).grid(row=2, column=1, padx=5, pady=5, sticky=W)
        Entry(gr2, textvariable=self.__ftp_port, justify=LEFT, state=mod).grid(row=2, column=2, padx=5, pady=5, sticky=W+E)

        self.__ftp_login = StringVar()
        Label(gr2, text=self.LANG.get('UPDATER', 'ftp_login'), justify=LEFT).grid(row=3, column=1, padx=5, pady=5, sticky=W)
        Entry(gr2, textvariable=self.__ftp_login, justify=LEFT, state=mod).grid(row=3, column=2, padx=5, pady=5, sticky=W+E)

        self.__ftp_password = StringVar()
        Label(gr2, text=self.LANG.get('UPDATER', 'ftp_password'), justify=LEFT).grid(row=4, column=1, padx=5, pady=5, sticky=W)
        Entry(gr2, textvariable=self.__ftp_password, justify=LEFT, state=mod).grid(row=4, column=2, padx=5, pady=5, sticky=W+E)

        self.__ftp_regexp = StringVar()
        Label(gr2, text=self.LANG.get('UPDATER', 'ftp_regexp'), justify=LEFT).grid(row=5, column=1, columnspan=2, padx=5, pady=2, sticky=W)
        Entry(gr2, textvariable=self.__ftp_regexp, justify=LEFT, state=mod).grid(row=6, column=1, columnspan=2, padx=5, pady=0, sticky=W+E)

        Label(gr2, text=self.LANG.get('UPDATER', 'regexp_help') % ('\n', '\n'), justify=LEFT, font=font_italic).grid(row=7, column=1, columnspan=2, padx=5, pady=2, sticky=W)

            # 3ème onglet : Options de la base de données (ACeDB)
        self.__db_host = StringVar()
        Label(gr3, text=self.LANG.get('UPDATER', 'db_host'), justify=LEFT).grid(row=1, column=1, padx=5, pady=5, sticky=W)
        Entry(gr3, textvariable=self.__db_host, justify=LEFT, state=mod, width=25).grid(row=1, column=2, padx=5, pady=5, sticky=W+E)

        self.__db_port = StringVar()
        Label(gr3, text=self.LANG.get('UPDATER', 'db_port'), justify=LEFT).grid(row=2, column=1, padx=5, pady=5, sticky=W)
        Entry(gr3, textvariable=self.__db_port, justify=LEFT, state=mod).grid(row=2, column=2, padx=5, pady=5, sticky=W+E)

        self.__db_login = StringVar()
        Label(gr3, text=self.LANG.get('UPDATER', 'db_login'), justify=LEFT).grid(row=3, column=1, padx=5, pady=5, sticky=W)
        Entry(gr3, textvariable=self.__db_login, justify=LEFT, state=mod).grid(row=3, column=2, padx=5, pady=5, sticky=W+E)

        self.__db_password = StringVar()
        Label(gr3, text=self.LANG.get('UPDATER', 'db_password'), justify=LEFT).grid(row=4, column=1, padx=5, pady=5, sticky=W)
        Entry(gr3, textvariable=self.__db_password, justify=LEFT, state=mod).grid(row=4, column=2, padx=5, pady=5, sticky=W+E)

        Label(gr3, text=self.LANG.get('UPDATER', 'db_help') % ('\n','\n','\n'), justify=LEFT, font=font_italic).grid(row=7, column=1, columnspan=2, padx=5, pady=2, sticky=W)

            # 4ème onglet : Options du serveur avec la 'letter'
        self.__letter_host = StringVar()
        Label(gr4, text=self.LANG.get('UPDATER', 'letter_host'), justify=LEFT).grid(row=1, column=1, padx=5, pady=5, sticky=W)
        Entry(gr4, textvariable=self.__letter_host, justify=LEFT, state=mod, width=25).grid(row=1, column=2, padx=5, pady=5, sticky=W+E)

        self.__letter_port = StringVar()
        Label(gr4, text=self.LANG.get('UPDATER', 'letter_port'), justify=LEFT).grid(row=2, column=1, padx=5, pady=5, sticky=W)
        Entry(gr4, textvariable=self.__letter_port, justify=LEFT, state=mod).grid(row=2, column=2, padx=5, pady=5, sticky=W+E)

        self.__letter_login = StringVar()
        Label(gr4, text=self.LANG.get('UPDATER', 'letter_login'), justify=LEFT).grid(row=3, column=1, padx=5, pady=5, sticky=W)
        Entry(gr4, textvariable=self.__letter_login, justify=LEFT, state=mod).grid(row=3, column=2, padx=5, pady=5, sticky=W+E)

        self.__letter_password = StringVar()
        Label(gr4, text=self.LANG.get('UPDATER', 'letter_password'), justify=LEFT).grid(row=4, column=1, padx=5, pady=5, sticky=W)
        Entry(gr4, textvariable=self.__letter_password, justify=LEFT, state=mod).grid(row=4, column=2, padx=5, pady=5, sticky=W+E)

        self.__letter_regexp = StringVar()
        Label(gr4, text=self.LANG.get('UPDATER', 'letter_regexp'), justify=LEFT).grid(row=5, column=1, columnspan=2, padx=5, pady=2, sticky=W)
        Entry(gr4, textvariable=self.__letter_regexp, justify=LEFT, state=mod).grid(row=6, column=1, columnspan=2, padx=5, pady=0, sticky=W+E)

        Label(gr4, text=self.LANG.get('UPDATER', 'letter_help') % ('\n', '\n'), justify=LEFT, font=font_italic).grid(row=7, column=1, columnspan=2, padx=5, pady=2, sticky=W)


            # Boutons
        self.btn_update = Button(grille, text=self.LANG.get('UPDATER', 'update'), width=8, command=self.__update)
        self.btn_update.grid(row=2, column=1, pady=2) 
        Button(grille, text=self.LANG.get('UPDATER', 'save'), width=8, command=self.__save).grid(row=2, column=2, pady=2)             
        self.btn_close = Button(grille, text=self.LANG.get('UPDATER', 'close'), width=8, command=self.__quit)
        self.btn_close.grid(row=2, column=3, pady=2) 


            # Valeurs par défaut
        self.__set_default_settings()
        self.__window.protocol("WM_DELETE_WINDOW", self.__quit)
        

    
    def tkerr (self) :
        pass



    def __set_default_settings (self) :
        """Définit les paramètres par défaut des objets."""

            # Affichage des informations générales
        if (self.CFG.get('UPDATE', 'install') == "LOCAL") :
            self.__server_host.set("LOCAL installation")
            self.server_host.config(state='disabled')
        else :
            self.__server_host.set(self.CFG.get('UPDATE', 'server_host'))  

        self.__auto_correct.set(self.CFG.getboolean('UPDATE', 'auto_correct')) 
        self.__save_update_log.set(self.CFG.getboolean('UPDATE', 'save_update_log')) 
        self.__save_acedb_file.set(self.CFG.getboolean('UPDATE', 'save_acedb_file')) 

            # Affichage des informations sur le serveur FTP
        self.__ftp_host.set(self.CFG.get('UPDATE', 'ftp_host'))        
        self.__ftp_port.set(self.CFG.get('UPDATE', 'ftp_port'))  
        self.__ftp_login.set(self.CFG.get('UPDATE', 'ftp_login'))  
        self.__ftp_password.set(self.CFG.get('UPDATE', 'ftp_password'))  
        self.__ftp_regexp.set(self.CFG.get('UPDATE', 'ftp_regexp'))  

            # Affichage des informations sur la base de données
        self.__db_host.set(self.CFG.get('UPDATE', 'db_host'))  
        self.__db_port.set(self.CFG.get('UPDATE', 'db_port'))  
        self.__db_login.set(self.CFG.get('UPDATE', 'db_login'))  
        self.__db_password.set(self.CFG.get('UPDATE', 'db_password'))  

            # Affichage des informations sur la base de données
        self.__letter_host.set(self.CFG.get('UPDATE', 'letter_host'))  
        self.__letter_port.set(self.CFG.get('UPDATE', 'letter_port'))  
        self.__letter_login.set(self.CFG.get('UPDATE', 'letter_login'))  
        self.__letter_password.set(self.CFG.get('UPDATE', 'letter_password'))  
        self.__letter_regexp.set(self.CFG.get('UPDATE', 'letter_regexp'))

            # Etat d'activation du bouton UPDATE
        if (self.__updates_enabled == False) :
            self.btn_update.config(state='disabled')



    def __quit (self) :
        """Arrête la mise à jour de WormBase en cours, et détruit la fenêtre."""
        
            # Si une MAJ de WormBase est en cours (en local), on force à quitter
        if (self.__up != None) and (self.__up.get_run_status() == True) :
            self.__up.stop_update_WormBase()
            
            # Fermeture de la fenêtre
        self.__window.destroy()
        self.__window = None


       
    def __save (self) :
        """Sauvegardes les paramètres (en local ou sur le serveur, selon les droits)"""
        
        param= {'server_host' : self.__server_host.get(),
                'auto_correct' : self.__auto_correct.get(),
                'save_update_log' : self.__save_update_log.get(), 
                'save_acedb_file' : self.__save_acedb_file.get(), 
                
                'ftp_host' : self.__ftp_host.get(), 
                'ftp_port' : self.__ftp_port.get(), 
                'ftp_login' : self.__ftp_login.get(), 
                'ftp_password' : self.__ftp_password.get(), 
                'ftp_regexp' : self.__ftp_regexp.get(),
                
                'db_host' : self.__db_host.get(), 
                'db_port' : self.__db_port.get(), 
                'db_login' : self.__db_login.get(), 
                'db_password' : self.__db_password.get(), 
                
                'letter_host' : self.__letter_host.get(), 
                'letter_port' : self.__letter_port.get(), 
                'letter_login' : self.__letter_login.get(), 
                'letter_password' : self.__letter_password.get(), 
                'letter_regexp' : self.__letter_regexp.get()}
        
        if (self.CFG.get('UPDATE', 'install') == "LOCAL") :
            up = update.Update_WormBase(self.CFG.filename, self.LANG.filename)
            up.save_parameters(param, 'LOCAL')
            self.CFG = MyConfigParser('config.ini')
            
        elif (self.CFG.get('UPDATE', 'install') == "SERVER") and (self.CFG.getboolean('UPDATE', 'access') == True) :
            up = update.Update_WormBase(self.CFG.filename, self.LANG.filename)
            self.__thread_params = threading.Thread(target=up.send_parameters, args=(param,))
            self.__thread_params.start()
            
        elif (self.CFG.get('UPDATE', 'install') == "SERVER") and (self.CFG.getboolean('UPDATE', 'access') == False) :
            if (param['server_host'][:7] != "http://") : self.CFG.set('UPDATE', 'server_host', "http://" + param['server_host'])  
            else : self.CFG.set('UPDATE', 'server_host', param['server_host'])
        
        

    def __update (self) :
        """Met à jour les versions de WormBase en local ou sur le serveur (selon l'installation)."""
    
            # Enregistrement des éventuelles modifications des paramètres
        self.__save()    
        
            # Création de l'instance de la classe Update_WormBase
        self.__up = update.Update_WormBase(self.CFG.filename, self.LANG.filename)                
        
        
            # Lancement de la MAJ en LOCAL
        if (self.CFG.get('UPDATE', 'install') == "LOCAL") :
            thread = threading.Thread(target=self.__launch_update, args=(self.__up,))           # lancement du thread
            thread.start()
            
            self.btn_update.config(activebackground='green3', fg='green3')                      # modification de la couleur du bouton 'update'
            self.btn_close.config(activebackground='red', fg='red')                             # modification de la couleur du bouton 'close'
               
            # Demande au serveur de se mettre à jour
        elif (self.CFG.get('UPDATE', 'install') == "SERVER") :
            self.__thread_update = threading.Thread(target=self.__up.ask_update_server)
            self.__thread_update.start()
            


    def __launch_update (self, up_instance) :
        """Met à jour les versions de WormBase en local."""
    
        self.btn_update.config(state='disabled')                                                # Désactive le bouton 'update'
        
            # Lancment de la MAJ en local
        if (self.CFG.getboolean('UPDATE', 'save_update_log') == True) :
            recov = sys.stdout
            log_file = open('wormbase/temp/UPDATE_LOG.txt', 'ab', 0)
            sys.stdout = log_file
            up_instance.update_WormBase()
            sys.stdout = recov
            log_file.close()
        else :
            up_instance.update_WormBase()

        try :
            if (self.__window != None) :
                self.btn_update.config(state='normal')                                                # Active le bouton 'update'
                self.btn_update.config(activebackground='#ececec', fg='black')                        # modification de la couleur du bouton 'update'
                self.btn_close.config(activebackground='#ececec', fg='black')                         # modification de la couleur du bouton 'close'
        except :        # Exception si la fenêtre est détruite avant la reconfiguration des boutons
            pass    



