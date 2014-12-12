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
import ttk, tkFont, tkFileDialog, tkMessageBox, tablelist, os, threading, ConfigParser
import conversion, updater, update, utils


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
            
            
            
            

class WBConverter :
    
    __window = None                     # Fenêtre
    __conv = None                       # Instance de la classe Conversion
    
    CFG = None                          # Configuration / Options
    LANG = None                         # Langue utilisée
    
    __menu = None                       # Menu
    
    __input_list = None                 # Liste initiale de gènes
    __input_geneID = None               # ID utilisé dans la liste initiale
    __input_release = None              # Release utilisée dans la liste initiale
    __input_releases = None             # Liste des releases disponibles (installées)
    __input_only_freeze = None          # Afficher (ou non) uniquement les versions Freezes
    __input_nb = None                   # Nombre de gènes dans la liste initiale
    
    __output_list = None                # Liste de gènes après conversion
    __output_geneID = None              # ID à utiliser pour la conversion
    __output_release = None             # Release à utiliser pour la conversion
    __output_releases = None            # Liste des releases disponibles (installées) [conversion uniquement vers version supérieure]
    __output_only_freeze = None         # Afficher (ou non) uniquement les versions Freezes
    __output_nb = None                  # Nombre de gènes dans la liste après conversion
    
    __settings_warnings = None          # Afficher (après conversion) les gènes qui n'ont pas été convertis
    __settings_display_changes = None   # Afficher (après conversion) les changements effectués dans le nom des gènes
    
    __statusbar = None                  # Informations sur l'état du programme
    __status = None                     # Barre de status
    
    __menu_languages = {}               # Langues disponibles
    __menu_language = None              # Langue utilisée
    __menu_display_not_found = None     # Option par défaut
    __menu_display_changes = None       # Option par défaut
    __menu_installation_profile = None  # Profil d'installation
    __menu_update_on_startup = None     # Recherche de MAJ au lancement de l'application
    __menu_params_on_startup = None     # Recherche des nouveaux paramètres au lancement de l'application

    
    
    def __init__ (self, cfg, lang):
        """Crée l'application et la fenêtre.
           cfg : Fichier de configuration
           lang : Fichier de la langue utilisée"""

            # Instance de la classe 'conversion' (module conversion.py)
        self.__conv = conversion.Conversion()

            # Enregistrement des paramètres
        self.CFG = cfg
        self.LANG = lang

        self.display_window()
        
    
    
    def display_window (self):
        """Affiche la fenêtre du convertisseur."""

            # Création de la fenêtre
        self.__window = Tk()
        self.__window.title(self.LANG.get('CONVERSION', 'window_title'))
        self.__window.resizable(width=False, height=False)

            # Variables (semi-)globales
        gene_IDs_Input = ['WB Gene ID   [WBGene00000254]', 'Gene Sequence Name  [K04F10.4]', 'CDS Sequence Name    [K04F10.4a]', 'Transcript Seq. Name   [K04F10.4a.1]',
                          'Gene Name   [bli-4]', '- Unknown / Mix -']
        
        gene_IDs_Output = ['WB Gene ID   [WBGene00000254]', 'Gene Sequence Name  [K04F10.4]', 'Gene Name   [bli-4]']

        font_bold_underline = tkFont.Font()
        font_bold_underline.config(weight=tkFont.BOLD, underline=True)

            # Separateur Menu / Contenu / Barre de status
        sep_window = Frame(self.__window)
        sep_window.pack()

            # Menu
        menu = Menu(self.__window)
    
        quit = Menu(menu, tearoff=0)
        menu.add_command(label=self.LANG.get('CONVERSION', 'menu_quit'), command=self.__window.destroy)
        
        
        settings = Menu(menu, tearoff=0)
        menu.add_cascade(label=self.LANG.get('CONVERSION', 'menu_settings'), menu=settings)
        
        settings_language = Menu(settings, tearoff=0)
        settings.add_cascade(label=self.LANG.get('CONVERSION', 'menu_settings_language'), menu=settings_language)

        self.__menu_language = IntVar()
        self.__add_languages(settings_language)
       
       
        settings_settings = Menu(settings, tearoff=0)
        settings.add_cascade(label=self.LANG.get('CONVERSION', 'menu_settings_settings'), menu=settings_settings)

        self.__menu_display_not_found = IntVar()
        self.__menu_display_changes = IntVar()
        settings_settings.add_checkbutton(label=self.LANG.get('CONVERSION', 'settings_display_not_found'), variable=self.__menu_display_not_found, command=self.__modif_default_settings)
        settings_settings.add_checkbutton(label=self.LANG.get('CONVERSION', 'settings_display_changes'), variable=self.__menu_display_changes, command=self.__modif_default_settings)
        
        
        settings_profile = Menu(settings, tearoff=0)
        settings.add_cascade(label=self.LANG.get('CONVERSION', 'menu_settings_profile'), menu=settings_profile)

        self.__menu_installation_profile = IntVar()
        self.old_installation_profile = IntVar()
        settings_profile.add_radiobutton(label="LOCAL", variable=self.__menu_installation_profile, value=0, command=self.__modif_installation_profile)
        settings_profile.add_radiobutton(label="SERVER / Client", variable=self.__menu_installation_profile, value=1, command=self.__modif_installation_profile)
        
        
        update = Menu(menu, tearoff=0)
        menu.add_cascade(label=self.LANG.get('CONVERSION', 'menu_update'), menu=update)
        
        update.add_command(label=self.LANG.get('CONVERSION', 'menu_update_wbupdater'), command=self.__launch_WBUpdater)
        
        self.update_settings = Menu(settings, tearoff=0)
        update.add_cascade(label=self.LANG.get('CONVERSION', 'menu_update_settings'), menu=self.update_settings)

        self.__menu_update_on_startup = IntVar()
        self.__menu_params_on_startup = IntVar()
        self.update_settings.add_checkbutton(label=self.LANG.get('CONVERSION', 'menu_update_settings_autoup'), variable=self.__menu_update_on_startup, command=self.__modif_default_settings)
        self.update_settings.add_checkbutton(label=self.LANG.get('CONVERSION', 'menu_update_settings_autoparam'), variable=self.__menu_params_on_startup, command=self.__modif_default_settings)

        
        help = Menu(menu, tearoff=0)
        menu.add_cascade(label=self.LANG.get('CONVERSION', 'menu_help'), menu=help)
        
        help.add_command(label=self.LANG.get('CONVERSION', 'menu_help_tutorial'), command=self.__tutorial)     
        help.add_command(label=self.LANG.get('CONVERSION', 'menu_help_help'), command=self.__help)  
        help.add_command(label=self.LANG.get('CONVERSION', 'menu_help_about'), command=self.__about)  
    
        
        self.__window.config(menu=menu)


            # Conteneur général
        grille = Frame(sep_window)
        grille.grid(row=1, column=1, padx=5, pady=5)

            # Partie INPUT LIST
        gr = Frame(grille)
        gr.grid(row=1, column=1, rowspan=5, padx=5, pady=5)
        
        label = Label(gr, text=self.LANG.get('CONVERSION', 'label_input_list'), justify=CENTER)
        label.grid(row=1, column=1, columnspan=3, padx=2, pady=2)
        label.config(font=font_bold_underline)
        
        Button(gr, text=self.LANG.get('CONVERSION', 'open_file'), width=10, command=self.__open_file).grid(row=2, column=1, padx=2, pady=5)             
        Button(gr, text=self.LANG.get('CONVERSION', 'paste'), width=10, command=self.__paste).grid(row=2, column=2, padx=2, pady=5) 
        Button(gr, text='X', command=lambda  : self.__clear_list('input')).grid(row=2, column=3, padx=2, pady=5) 
 
        self.__input_list = Listbox(gr, height=21)
        self.__input_list.grid(row=3, column=1, columnspan=2, sticky=N+S+W+E)
        scrollbarIn = ttk.Scrollbar(gr, orient=VERTICAL, command=self.__input_list.yview)
        scrollbarIn.grid(row=3, column=3, sticky=N+S)
        self.__input_list['yscrollcommand'] = scrollbarIn.set
        self.__input_list.config(setgrid=2, width=30)

            # Partie centrale        
        # input information
        input_infos = ttk.Labelframe(grille, text=" " + self.LANG.get('CONVERSION', 'input_info') + " ")
        input_infos.grid(row=1, column=2, padx=5, pady=5)
        
        gr = Frame(input_infos)    
        gr.pack()

        Label(gr, text=self.LANG.get('CONVERSION', 'gene_ID')).grid(row=1, column=1, padx=2, pady=2, sticky=W) 
        self.__input_geneID = StringVar() 
        ttk.Combobox(gr, values=gene_IDs_Input, textvariable=self.__input_geneID, width=28, state='readonly').grid(row=1, column=2, columnspan=2, padx=2, pady=2, sticky=W+E)

        Label(gr, text=self.LANG.get('CONVERSION', 'gene_release')).grid(row=2, column=1, padx=2, pady=2, sticky=W) 
        self.__input_release = StringVar()
        self.__input_releases = ttk.Combobox(gr, values=[], textvariable=self.__input_release, width=7, state='readonly')
        self.__input_releases.grid(row=2, column=2, padx=2, pady=2, sticky=W+E)

        self.__input_only_freeze = IntVar()
        Checkbutton(gr, text=self.LANG.get('CONVERSION', 'only_freezes'), variable=self.__input_only_freeze, command=lambda  : self.__refresh_releases_list('input')).grid(row=2, column=3, padx=2, pady=2)    

        self.__input_nb = StringVar()
        Label(gr, text=self.LANG.get('CONVERSION', 'number')).grid(row=3, column=1, columnspan=2, padx=2, pady=2, sticky=E)
        Entry(gr, textvariable=self.__input_nb, justify=CENTER, width=6, state='readonly').grid(row=3, column=3, padx=2, pady=2, sticky=W)

        # output information
        output_infos = ttk.Labelframe(grille, text=" " + self.LANG.get('CONVERSION', 'output_info') + " ")
        output_infos.grid(row=2, column=2, padx=5, pady=5)
        
        gr = Frame(output_infos)   
        gr.pack()

        Label(gr, text=self.LANG.get('CONVERSION', 'gene_ID')).grid(row=1, column=1, padx=2, pady=2, sticky=W) 
        self.__output_geneID = StringVar() 
        ttk.Combobox(gr, values=gene_IDs_Output, textvariable=self.__output_geneID, width=28, state='readonly').grid(row=1, column=2, columnspan=2, padx=2, pady=2, sticky=W+E)

        Label(gr, text=self.LANG.get('CONVERSION', 'gene_release')).grid(row=2, column=1, padx=2, pady=2, sticky=W) 
        self.__output_release = StringVar()
        self.__output_releases = ttk.Combobox(gr, values=[], textvariable=self.__output_release, width=7, state='readonly')
        self.__output_releases.grid(row=2, column=2, padx=2, pady=2, sticky=W+E)

        self.__output_only_freeze = IntVar()
        Checkbutton(gr, text=self.LANG.get('CONVERSION', 'only_freezes'), variable=self.__output_only_freeze, command=lambda  : self.__refresh_releases_list('output')).grid(row=2, column=3, padx=2, pady=2)    

        self.__output_nb = StringVar()
        Label(gr, text=self.LANG.get('CONVERSION', 'number')).grid(row=3, column=1, columnspan=2, padx=2, pady=2, sticky=E)
        Entry(gr, textvariable=self.__output_nb, justify=CENTER, width=6, state='readonly').grid(row=3, column=3, padx=2, pady=2, sticky=W)

        # options
        options = ttk.Labelframe(grille, text=" " + self.LANG.get('CONVERSION', 'settings') + " ")
        options.grid(row=3, column=2, padx=5, pady=5, sticky=W+E)
        
        gr = Frame(options)    
        gr.pack()

        self.__settings_warnings = IntVar()
        Checkbutton(gr, text=self.LANG.get('CONVERSION', 'settings_display_not_found'), variable=self.__settings_warnings).grid(row=1, column=1, padx=2, pady=2, sticky=W)    

        self.__settings_display_changes = IntVar()
        Checkbutton(gr, text=self.LANG.get('CONVERSION', 'settings_display_changes'), variable=self.__settings_display_changes).grid(row=2, column=1, padx=2, pady=2, sticky=W)    

        # StatusBar
        self.__statusbar = Label(grille, text=self.LANG.get('CONVERSION', 'default_statusbar_text'), bd=1, relief=SUNKEN, justify=CENTER)
        self.__statusbar.grid(row=4, column=2, padx=25, sticky=W+E)   
        
        # bouton CONVERSION
        Button(grille, text=self.LANG.get('CONVERSION', 'button_conversion'), height=3, width=25, command=self.__launch_conversion).grid(row=5, column=2, padx=5, pady=5)    

            # Partie OUTPUT LIST
        gr = Frame(grille)
        gr.grid(row=1, column=3, rowspan=5, padx=5, pady=5)
        
        label = Label(gr, text=self.LANG.get('CONVERSION', 'label_output_list'), justify=CENTER)
        label.grid(row=1, column=1, columnspan=3, padx=2, pady=2)
        label.config(font=font_bold_underline)
        
        Button(gr, text=self.LANG.get('CONVERSION', 'save_file'), command=self.__save_file, width=10).grid(row=2, column=1, padx=2, pady=5)             
        Button(gr, text=self.LANG.get('CONVERSION', 'copy'), width=10, command=self.__copy).grid(row=2, column=2, padx=2, pady=5) 
        Button(gr, text='X', command=lambda  : self.__clear_list('output')).grid(row=2, column=3, padx=2, pady=5) 
 
        self.__output_list = Listbox(gr, height=21)
        self.__output_list.grid(row=3, column=1, columnspan=2, sticky=N+S+W+E)
        scrollbarOut = ttk.Scrollbar(gr, orient=VERTICAL, command=self.__output_list.yview)
        scrollbarOut.grid(row=3, column=3, sticky=N+S)
        self.__output_list['yscrollcommand'] = scrollbarOut.set
        
            # Barre de status
        self.__status = Label(sep_window, text="", bd=1, relief=SUNKEN, justify=LEFT)
        self.__status.grid(row=2, column=1, sticky=W+E)   
        
        
            # Evénements 
        self.__input_list.bind('<Double-Button-1>', lambda *args : self.__delete_items('input'))
        self.__output_list.bind('<Double-Button-1>', lambda *args : self.__delete_items('output'))

            # Valeurs par défaut
        self.__set_default_settings()

            # Recherche de MAJ sur le serveur
        self.__launch_update()
            
        self.__window.mainloop()
    

            
    def __set_default_settings(self):
        """Définit les paramètres par défaut des objets"""
        
            # Identifiants
        self.__input_geneID.set("Gene Sequence Name  [K04F10.4]")
        self.__output_geneID.set("Gene Sequence Name  [K04F10.4]")
    
            # Releases only freezes
        self.__input_only_freeze.set(True)
        self.__output_only_freeze.set(True)
        
            # Options
        self.__settings_warnings.set(self.CFG.getboolean('WORMBASE', 'settings_display_not_found'))
        self.__settings_display_changes.set(self.CFG.getboolean('WORMBASE', 'settings_display_changes'))
        
            # Affiche les versions WB installées
        self.__refresh_releases_list('input')
        self.__refresh_releases_list('output')
        
            # Affiche le nombre de gènes dans les listes
        self.__input_nb.set(0)
        self.__output_nb.set(0)
        
            # Valeurs par défaut des menus
        self.__menu_language.set(self.__menu_languages[self.CFG.get('WORMBASE', 'language')[9:]])
        
        self.__menu_display_not_found.set(self.CFG.getboolean('WORMBASE', 'settings_display_not_found'))
        self.__menu_display_changes.set(self.CFG.getboolean('WORMBASE', 'settings_display_changes'))
        
        if (self.CFG.get('UPDATE', 'install') == "LOCAL") :
            self.__menu_installation_profile.set(0)
        elif (self.CFG.get('UPDATE', 'install') == "SERVER") and (self.CFG.getboolean('UPDATE', 'access') == False) :
            self.__menu_installation_profile.set(1)
        self.old_installation_profile.set(self.__menu_installation_profile.get())        
        
        if  (self.CFG.get('UPDATE', 'install') == "LOCAL") :
            self.update_settings.entryconfig(0, state='disabled')
            self.update_settings.entryconfig(1, state='disabled')
        else :
            self.__menu_update_on_startup.set(self.CFG.getboolean('WORMBASE', 'update_on_startup'))
            self.__menu_params_on_startup.set(self.CFG.getboolean('WORMBASE', 'params_on_startup'))


            
    def __add_languages (self, obj) :
        """Ajoute la liste de toutes les langues disponibles dans le menu."""
            
        value = 0
        for lang in os.listdir('language') :
            obj.add_radiobutton(label=lang, variable=self.__menu_language, value=value, command=self.__modif_language)
            self.__menu_languages[lang] = value
            value = value + 1
            
            
            
    def __modif_language (self) :
        """Modifie la langue utilisée."""
        
        for lang in self.__menu_languages :
            if (self.__menu_languages[lang] == self.__menu_language.get()) :
                self.CFG.set('WORMBASE', 'language', 'language/' + lang)
                tkMessageBox.showinfo(self.LANG.get('CONVERSION', 'window_language_title'), self.LANG.get('CONVERSION', 'window_language'))
                break
            
            
           
    def __modif_default_settings (self) :
        """Modifie les options par défaut."""
            
        self.CFG.setboolean('WORMBASE', 'settings_display_not_found', self.__menu_display_not_found.get())
        self.CFG.setboolean('WORMBASE', 'settings_display_changes', self.__menu_display_changes.get())
        self.CFG.setboolean('WORMBASE', 'update_on_startup', self.__menu_update_on_startup.get())
        self.CFG.setboolean('WORMBASE', 'params_on_startup', self.__menu_params_on_startup.get())
            
            
            
    def __modif_installation_profile (self) :
        """Modifie le profil d'installation."""
        
        res = tkMessageBox.askyesno(self.LANG.get('CONVERSION', 'window_profile_title'), self.LANG.get('CONVERSION', 'window_profile'))
        if (res == True) :
        
            if (self.__menu_installation_profile.get() == 0) :        # passer en LOCAL
                self.CFG.set('UPDATE', 'install', 'LOCAL')
                self.CFG.set('UPDATE', 'access', 'True')
                
            elif (self.__menu_installation_profile.get() == 1) :      # passer en Client Serveur
                self.CFG.set('UPDATE', 'install', 'SERVER')
                self.CFG.set('UPDATE', 'access', 'False')
                
            self.old_installation_profile.set(self.__menu_installation_profile.get())  
            
        else:
            self.__menu_installation_profile.set(self.old_installation_profile.get())
  
  
    
    def __launch_WBUpdater (self) :
        """Ouvre la fenêtre de paramétrage des mises à jour."""
        
        wbup = updater.Update_WormBase(self.__window, self.CFG.filename, self.LANG.filename)
  
  
  
    def __launch_update (self) :
        """Lance la mise à jour de l'ordinateur Client (par rapport au serveur)"""
        
        if (self.CFG.get('UPDATE', 'install') == "SERVER") :
            up = update.Update_WormBase(self.CFG.filename, self.LANG.filename)

            thread = threading.Thread(target=up.check_server_info, args=(self.__status, self.CFG.getboolean('WORMBASE', 'update_on_startup'), self.CFG.getboolean('WORMBASE', 'params_on_startup')))  # lancement du thread
            thread.start()
        
    
    
    def __tutorial (self) :
        """Tutoriel sur le programme et les mises à jour."""
        try :   # Windows
            os.startfile('"help/Tutorial - WB Converter.pdf"')
        except :    

            try :   # Linux
                os.system('xdg-open ' + '"help/Tutorial - WB Converter.pdf"')
            except :
            
                try :    # Mac OS
                    os.system('open ' + '"help/Tutorial - WB Converter.pdf"')
                except :
                    tkMessageBox.showinfo(self.LANG.get('CONVERSION', 'menu_help_tutorial'), self.LANG.get('CONVERSION', 'pdf_error'))
        
        
        
    def __help (self) :
        """Aide complète sur le programme et les mises à jour."""
        try :   # Windows
            os.startfile('"help/Documentation.pdf"')
        except :    

            try :   # Linux
                os.system('xdg-open ' + '"help/Documentation.pdf"')
            except :
            
                try :    # Mac OS
                    os.system('open ' + '"help/Documentation.pdf"')
                except :
                    tkMessageBox.showinfo(self.LANG.get('CONVERSION', 'menu_help_help'), self.LANG.get('CONVERSION', 'pdf_error'))
  

            
    def __about (self) :
        """A propos du programme..."""
        __win_about = Toplevel(self.__window)
        __win_about.title(self.LANG.get('CONVERSION', 'menu_help_about'))

        gr = Frame(__win_about)
        gr.pack()
        
        Label(gr, text="WormBase Converter (1.0)").grid(row=1, column=1, padx=5, pady=10)
        Label(gr, text="CIML - Centre d'Immunologie de Marseille-Luminy").grid(row=2, column=1, padx=5, pady=1)   
        Label(gr, text="Parc Scientifique & Technologique de Luminy").grid(row=3, column=1, padx=5, pady=1)
        Label(gr, text="Case 906 - 13288 MARSEILLE cedex 09").grid(row=4, column=1, padx=5, pady=1)
        Label(gr, text="FRANCE").grid(row=5, column=1, padx=5, pady=1)
        Label(gr, text="Team J. Ewbank <ewbank@ciml.univ-mrs.fr>").grid(row=6, column=1, padx=5, pady=7)
        Label(gr, text="Copyright © 2010").grid(row=7, column=1, padx=5, pady=5)

        Button(gr, text=self.LANG.get('CONVERSION', 'about_close'), command=lambda : __win_about.destroy(), width=8).grid(row=8, column=1, padx=5, pady=5) 



    def __refresh_releases_list (self, list):
        """Affiche la liste des releases disponibles pour la conversion.
           list = 'input' | 'output' : liste à afficher"""
        
        if (list == 'input') :
            releases_installed = utils.get_WB_releases_installed(freezes_only=self.__input_only_freeze.get())
            releases_installed.sort()
            releases_installed.reverse()
            releases_installed.append('Unknown')
            self.__input_releases.config(values=releases_installed)
            self.__input_release.set(releases_installed[0])
            
        elif (list == 'output') :
            releases_installed = utils.get_WB_releases_installed(freezes_only=self.__output_only_freeze.get())
            releases_installed.sort()
            releases_installed.reverse()
            self.__output_releases.config(values=releases_installed)
            if (len(releases_installed) != 0) :
                self.__output_release.set(releases_installed[0])

            
            
    def __paste (self):
        """Copie le contenu du presse-papier dans la input list, en séparant les informations selon : ',',';',' ','/','\\t','\\n'."""
        
            # Récupération du presse-papiers
        try :
            text = self.__window.clipboard_get()
        except :
            return
        
            # Séparation du texte copié pour récupérer la liste des gènes
        text = text.replace(',', '\n')
        text = text.replace(';', '\n')
        text = text.replace(' ', '\n')
        text = text.replace('\t', '\n')
        text = text.replace('/', '\n')
        text = text.replace('\r\n', '\n')
        genes = text.split('\n')
        
            # Ajout des gènes à la liste
        for gene in genes :
            if (gene != "") : self.__input_list.insert(END, gene)
            
            # Affiche le nombre de gènes collés
        self.__nb_genes('input')
            

    
    def __copy (self):
        """Copie la liste des gènes de la output list dans le presse-papier. La séparation des gènes est '\\n'"""
        
            # Récupération de la liste des gènes
        genes = self.__output_list.get(0, END)
        
            # Enregistrement des gènes dans le presse-papiers (séparation : \n)
        text = ""
        for gene in genes :
            text = text + gene + '\n'
        self.__window.clipboard_clear()
        self.__window.clipboard_append(text)
        

    
    def __clear_list (self, list):
        """Efface une liste de gènes.
           list = 'input' | 'output' : Liste à effacer"""
           
        if (list == 'input') :
            self.__input_list.delete(0, END)
        elif (list == 'output') :
            self.__output_list.delete(0, END)
        self.__nb_genes(list)
         
         
         
    def __open_file (self):
        """Ouvre un fichier et ajoute la liste des gènes à la input liste."""
        
        file = tkFileDialog.askopenfilename(filetypes = [("Gene list", "*")])
        if (len(file) != 0) :
                # Récupère le contenu du fichier
            f = open(file, 'rb')
            list = f.read()
            f.close()
            genes = list.replace('\r\n', '\n').split('\n')
            
                # Ajout des gènes à la liste
            for gene in genes :
                if (gene != "") : self.__input_list.insert(END, gene)
                
        self.__nb_genes('input')
         
         
         
    def __save_file (self):
        """Enregistre la liste des gènes de la output list dans un fichier."""
        
        file = tkFileDialog.asksaveasfilename(filetypes = [("Gene list", "*.txt")])
        if (file != "") :
            if (file[-4:] != '.txt') : file = file + '.txt'
            
                # Récupère la liste des gènes
            genes = self.__output_list.get(0, END)
            
                # Enregistre la liste des gènes
            f = open(file, 'wb')
            for gene in genes :
                f.write(gene + '\r\n')
            f.close()
         
        self.__window.focus()


         
    def __delete_items (self, list):
        """Supprime un gène dans la liste lors d'un double-clic.
           list = 'input' | 'output' : Liste de gènes concernée"""
        
        if (list == 'input') :
             selection = self.__input_list.curselection()
             if (selection != ()) : self.__input_list.delete(selection, selection)
        
        elif (list == 'output') :
             selection = self.__output_list.curselection()
             if (selection != ()) : self.__output_list.delete(selection, selection)
            
        self.__nb_genes(list)
         
    
    
    def __nb_genes (self, list):
        """Affiche le nombre de gènes dans une liste.
           list = 'input' | 'output' : Liste de gènes concernée"""
        
        if (list == 'input') : self.__input_nb.set(self.__input_list.size())
        elif (list == 'output') : self.__output_nb.set(self.__output_list.size())
        
    
 
    def __statusbar_text(self, text = 'none', status = 'none'):
        """Affiche l'avancement de la conversion.
           text : Texte à afficher
           status = 'done' | 'error' | 'waiting' | 'asking' | '' : Status de l'application (= couleur du texte)"""
        
        if (status == 'done') : color = 'DarkGreen'
        elif (status == 'error') : color = 'red'
        elif (status == 'waiting') : color = 'DarkOrange'
        elif (status == 'asking') : color = 'blue'
        else : color = 'black'
        
        if (text != 'none') : self.__statusbar.config(text=text)
        if (status != 'none') : self.__statusbar.config(fg=color)
        self.__window.update()
 

    
    def __launch_conversion (self):
        """Lance la conversion d'une liste de gènes (input list)."""
        
            ### Récupération de la liste de gènes
        gene_list = list(self.__input_list.get(0, END))
        if (len(gene_list) == 0) :
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_error_empty_input_list'), 'error')
            return
        
            ### RAZ de la output list
        self.__output_list.delete(0, END)
        
    
            ### ID(s) utilisé(s) dans la liste de gènes initiale
        input_ID = self.__input_geneID.get()
        if (input_ID == 'WB Gene ID   [WBGene00000254]') : input_ID = ['wb']
        elif (input_ID == 'Gene Sequence Name  [K04F10.4]') : input_ID = ['gene']
        elif (input_ID == 'CDS Sequence Name    [K04F10.4a]') : input_ID = ['cds']
        elif (input_ID == 'Transcript Seq. Name   [K04F10.4a.1]') : input_ID = ['transcript']
        elif (input_ID == 'Gene Name   [bli-4]') : input_ID = ['cgc']
        else :
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_detect_IDs'), 'waiting')
            input_ID = self.__conv.detect_IDs(gene_list)


            ### Conversion des Transcrits & CDS en Gene Sequence Name
        if 'transcript' in input_ID :
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_convert_transcripts'), 'waiting')
            gene_list = self.__conv.convert_Transcript_to_GeneID(gene_list) # conversion des Transcrits & CDS
            input_ID.remove('transcript')                                   # modifie la liste ..
            if 'cds' in input_ID : input_ID.remove('cds')                   # .. des identifiants ..
            if 'gene' not in input_ID : input_ID.append('gene')             # .. de la liste initiale
            
        elif 'cds' in input_ID :
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_convert_cds'), 'waiting')
            gene_list = self.__conv.convert_CDS_to_GeneID(gene_list)        # conversion des CDS
            input_ID.remove('cds')                                          # modifie la liste des identifiants ..
            if 'gene' not in input_ID : input_ID.append('gene')             # .. de la liste initiale
        
        
            ### Release utilisée dans la liste de gènes
        try :
                # utilisation de la release choisie
            input_release = int(self.__input_release.get())
        except :
                # recherche des releases potentielles, si UNKNOWN
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_detect_release'), 'waiting')
            releases_installed = utils.get_WB_releases_installed(freezes_only=False)
            
            try :
                input_release = self.__conv.detect_release(self.__window, gene_list, releases_installed, input_ID)
            except :
                self.__statusbar_text("Error", 'error')
                return


            ### Release souhaitée après conversion
        output_release = int(self.__output_release.get())


            ### Conversion des IDs (WB, gene, cgc) en WormBase ID avec la release définie
        self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_convert_into_WbID'), 'waiting')
        genes_list_WB = []                                          # liste initiale des gènes (après conversion en WB ID)
            
        genes_available = []                                        # gènes retrouvés dans la input_release
        genes_not_found = []                                        # gènes non retrouvés dans la liste input_release
        
        gene_list_separated = self.__conv.separate_IDs(gene_list)   # liste des gènes séparée selon les identifiants
        for ID in input_ID :
                # Conversion des différents ID en WB ID (même WB ID -> WB ID pour valider la présence du gène dans la input_release)
            res = self.__conv.convert_GeneIDs(gene_list_separated[ID], input_release, ID, 'wb')
            
                # Enregistrement de la liste des gènes retrouvés ou non dans la input_release
            genes_available = genes_available + res['converted']
            genes_not_found = genes_not_found + res['unconverted']
            
            genes_list_WB = genes_list_WB + res['results']
        

            ### Conversion des identifiants, de version en versions

            # Suppression des doublons
        genes_list_WB = list(set(genes_list_WB))
            
            # Conversion directe
        if (input_release <= output_release) :
            genes_list_WB = self.__conversion(genes_list_WB, input_release, output_release)
            
            # Rétro-conversion
        elif (input_release > output_release) :
            genes_list_WB = self.__conversion_reverse(genes_list_WB, input_release, output_release)

            ### ID souhaité dans la OUTPUT LIST
        output_ID = self.__output_geneID.get()
        if (output_ID == 'WB Gene ID   [WBGene00000254]') : output_ID = 'wb'
        elif (output_ID == 'Gene Sequence Name  [K04F10.4]') : output_ID = 'gene'
        elif (output_ID == 'Gene Name   [bli-4]') : output_ID = 'cgc'                 
                    
                    
            ### Conversion des WB IDs en l'ID final souhaité
        output_gene_list = []               # liste des gènes dans l'identifiant souhaité
        
        output_genes_available = []         # gènes retrouvés dans la output_release
        output_genes_no_synonym = []        # gènes retrouvés dans la output_release mais indisponible dans l'identifiant souhaité
        
        if (output_ID == 'gene') or (output_ID == 'cgc') :
            res = self.__conv.convert_GeneIDs(genes_list_WB, output_release, 'wb', output_ID)
        
            output_genes_available = res['converted']
            output_genes_no_synonym = res['no_synonym']
            output_gene_list = res['results']
        else :
            output_gene_list = genes_list_WB
        
            ### Affichage de la OUTPUT LIST, avec suppression des doublons
        output_gene_list = list(set(output_gene_list))
        for gene in output_gene_list :
            self.__output_list.insert(END, gene)

            ### Affichage du nombre de gènes
        self.__nb_genes('output') 
        
            ### RAZ de la statusbar
        self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_conversion_done'), 'done')
        
            ### Affichage des erreurs de conversions, si souhaité
        if (self.__settings_warnings.get() == True) :
            self.__display_errors(input_release, output_release, genes_not_found, output_genes_no_synonym)

            ### Affichage des changements dans le nom des gènes, si souhaité
        if (self.__settings_display_changes.get() == True) :
            self.__display_changes()



    def __conversion (self, genes_list_WB, input_release, output_release) :
        """Conversion des WB IDs de version en version jusqu'à celle souhaitée.
           genes_list_WB : Liste des gènes (en WB ID)
           input_release : Version initiale de WormBase
           output_release : Version de WormBase souhaitée après conversion"""

            # Création du fichier contenant les changements dans le nom des gènes entre les versions
        if (self.__settings_display_changes.get() == True) :
            f = open('temp/conversion.txt', 'wb')
            f.close()
            
            # Conversion des IDs de version en version, jusqu'à celle souhaitée (+ enregistrement des évolutions)
        all_genes_IDs = genes_list_WB          # liste de tous les gènes rencontrés lors des conversions de version en version

        for release in range(input_release, output_release) :
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_conversion_between_releases') % (release, release+1), 'waiting')
            try :
                list_updated, genes_resurrected = self.__conv.update_geneIDs(genes_list_WB, release, True)
            except self.__conv.Error, e :
                if (e.errno == 2) :
                    self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_fileEvols_not_found') % (release, release+1), 'error')
                return

                # Création de la nouvelle liste
            genes_list_WB = []
            for old_gene, evol, new_gene in list_updated :

                    # Enregistrement de l'évolution dans le nom des gènes
                if (self.__settings_display_changes.get() == True) :
                    f = open('temp/conversion.txt', 'ab')
                    f.write(str(release) + '\t' + str(release+1) + '\t' + old_gene + '\t' + evol + '\t' + new_gene + '\r\n')
                    f.close()      
            
                    # A partir des gènes convertis
                if (new_gene != "") :

                    if new_gene not in genes_list_WB :
                        genes_list_WB.append(new_gene)
                    else :
                        continue                                # suppression des doublons
                    
                    if new_gene not in all_genes_IDs :
                        all_genes_IDs.append(new_gene)          # ajout à la liste totale des gènes
                        
                # Ajout des gènes ressuscités
            for resurrec_gene in genes_resurrected :
                if resurrec_gene in all_genes_IDs :
                    genes_list_WB.append(resurrec_gene)
                    if (self.__settings_display_changes.get() == True) :
                        f = open('temp/conversion.txt', 'ab')
                        f.write(str(release) + '\t' + str(release+1) + '\t' + resurrec_gene + '\tResurrected\t' + '' + '\r\n')
                        f.close()  

        return genes_list_WB



    def __conversion_reverse (self, genes_list_WB, input_release, output_release) :
        """Rétro-conversion des WB IDs de version en version jusqu'à celle souhaitée.
           genes_list_WB : Liste des gènes (en WB ID)
           input_release : Version initiale de WormBase
           output_release : Version de WormBase souhaitée après conversion"""
           
            # Création du fichier contenant les changements dans le nom des gènes entre les versions
        if (self.__settings_display_changes.get() == True) :
            f = open('temp/conversion.txt', 'wb')
            f.close()
            
            # Conversion des IDs de version en version, jusqu'à celle souhaitée (+ enregistrement des évolutions)
        all_genes_IDs = genes_list_WB          # liste de tous les gènes rencontrés lors des conversions de version en version     
            
        for release in range(input_release, output_release, -1) : 
            self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_conversion_reverse_between_releases') % (release, release-1), 'waiting')
            try :
                list_downdated, genes_killed = self.__conv.downdate_geneIDs(genes_list_WB, release, True)
            except self.__conv.Error, e :
                if (e.errno == 2) :
                    self.__statusbar_text(self.LANG.get('CONVERSION', 'statusbar_fileEvols_not_found') % (release-1, release), 'error')
                return

                # Création de la nouvelle liste
            genes_list_WB = []
            for old_gene, evol, new_gene in list_downdated :

                    # Enregistrement de l'évolution et le nom des gènes
                if (self.__settings_display_changes.get() == True) :
                    f = open('temp/conversion.txt', 'ab')
                    f.write(str(release) + '\t' + str(release-1) + '\t' + old_gene + '\t' + evol + '\t' + new_gene + '\r\n')
                    f.close()
            
                    # A partir des gènes convertis
                if (new_gene != "") :

                    if new_gene not in genes_list_WB :
                        genes_list_WB.append(new_gene)
                    else :
                        continue                                # suppression des doublons
                    
                    if new_gene not in all_genes_IDs :
                        all_genes_IDs.append(new_gene)          # ajout à la liste totale des gènes
                        
                # Ajout des gènes ressuscités
            for kill_gene in genes_killed :
                if kill_gene in all_genes_IDs :
                    genes_list_WB.append(kill_gene)
                    if (self.__settings_display_changes.get() == True) :
                        f = open('temp/conversion.txt', 'ab')
                        f.write(str(release) + '\t' + str(release-1) + '\t' + kill_gene + '\tResurrected\t' + '' + '\r\n')
                        f.close()

        return genes_list_WB



    def __display_errors (self, input_release, output_release, genes_not_found, genes_without_synonyms):
        """Affiche une fenêtre avec les gènes qui n'ont pas été convertis, car non valides dans la version initiale de WormBase sélectionnée ou dont il n'existe pas l'identifiant souhaité.
           input_release : Version initiale de WormBase
           output_release : Version souhaitée de WormBase
           genes_not_found : Gènes non existants dans la 'input_release'
           genes_without_synonyms : Gènes dont il n'existe pas l'identifiant souhaité"""
                    
        def __quit ():
            win_errors.destroy()       

        def __copy (list):
                # Récupération de la liste des gènes
            if (list == 'not_found') :
                genes = list_genes_not_found.get(0, END)
            elif (list == 'no_synonym') :
                genes = list_genes_without_synonyms.get(0, END)
            
                # Enregistrement des gènes dans le presse-papiers (séparation : \n)
            text = ""
            for gene in genes :
                text = text + gene + '\n'
            self.__window.clipboard_clear()
            self.__window.clipboard_append(text)         
                    
        def __save (list):
            if ((list == 'not_found') and (list_genes_not_found.size() == 0)) or \
               ((list == 'no_synonym') and (list_genes_without_synonyms.size() == 0)):
                return
            
            file = tkFileDialog.asksaveasfilename(filetypes = [("Gene list", "*.txt")])
            if (file != "") :
                if (file[-4:] != '.txt') : file = file + '.txt'
                
                    # Récupère la liste des gènes
                if (list == 'not_found') :
                    genes = list_genes_not_found.get(0, END)
                elif (list == 'no_synonym') :
                    genes = list_genes_without_synonyms.get(0, END)
                
                    # Enregistre la liste des gènes
                f = open(file, 'wb')
                for gene in genes :
                    f.write(gene + '\r\n')
                f.close()
             
            self.__window.focus()
            win_errors.focus() 
            
                    
            # Création de la fenêtre
        win_errors = Toplevel(self.__window)
        win_errors.title(self.LANG.get('CONVERSION_ERRORS', 'window_title'))
        win_errors.resizable(width=False, height=False)
                    
            # Grille principale
        grille = Frame(win_errors)
        grille.pack(pady=5)
        
            # Genes non existants dans la Input release
        gr = Frame(grille)
        gr.grid(row=1, column=1, padx=10, sticky=W+E+N+S)
            
        Label(gr, text=self.LANG.get('CONVERSION_ERRORS', 'genes_not_found') % ("\n", input_release)).grid(row=1, column=1, columnspan=3, sticky=W+E)

        Button(gr, text=self.LANG.get('CONVERSION_ERRORS', 'save_file'), width=10, command=lambda : __save('not_found')).grid(row=2, column=1, padx=2, pady=5)             
        Button(gr, text=self.LANG.get('CONVERSION_ERRORS', 'copy'), width=10, command=lambda : __copy('not_found')).grid(row=2, column=2, padx=2, pady=5) 

        list_genes_not_found = Listbox(gr, height=10)
        list_genes_not_found.grid(row=3, column=1, columnspan=2, sticky=N+S+W+E)
        scrollbar1 = ttk.Scrollbar(gr, orient=VERTICAL, command=list_genes_not_found.yview)
        scrollbar1.grid(row=3, column=3, sticky=N+S)
        list_genes_not_found['yscrollcommand'] = scrollbar1.set      
                    
            # Genes dont il n'existe que le WB ID
        gr = Frame(grille)
        gr.grid(row=1, column=2, padx=10, sticky=W+E+N+S)
            
        Label(gr, text=self.LANG.get('CONVERSION_ERRORS', 'genes_no_synonym') % "\n").grid(row=1, column=1, columnspan=3, sticky=W+E)

        Button(gr, text=self.LANG.get('CONVERSION_ERRORS', 'save_file'), width=10, command=lambda : __save('no_synonym')).grid(row=2, column=1, padx=2, pady=5)             
        Button(gr, text=self.LANG.get('CONVERSION_ERRORS', 'copy'), width=10, command=lambda : __copy('no_synonym')).grid(row=2, column=2, padx=2, pady=5) 

        list_genes_without_synonyms = Listbox(gr, height=10)
        list_genes_without_synonyms.grid(row=3, column=1, columnspan=2, sticky=N+S+W+E)
        scrollbar2 = ttk.Scrollbar(gr, orient=VERTICAL, command=list_genes_without_synonyms.yview)
        scrollbar2.grid(row=3, column=3, sticky=N+S)
        list_genes_without_synonyms['yscrollcommand'] = scrollbar2.set
        
            # Bouton quitter
        Button(grille, text=self.LANG.get('CONVERSION_ERRORS', 'quit'), width=10, command=__quit).grid(row=2, column=1, columnspan=2, pady=5) 

            # Affichage des listes de gènes
        for gene in genes_not_found :
            list_genes_not_found.insert(END, gene)
        for gene in genes_without_synonyms :
            list_genes_without_synonyms.insert(END, gene)



    def __display_changes (self):
        """Affiche une fenêtre avec les changements réalisés lors de la conversion (ou rétro-conversion) des identifiants."""
        
        def __quit ():
            #self.__window.focus()
            win_changes.destroy()  
            
        def __sort_by_column(none, col):
            order = '-increasing'
            if (table.sortcolumn() == int(col)) and (table.sortorder() == 'increasing') :
                order = '-decreasing'
            table.sortbycolumn(col, order)
            
        def __save ():
            file = tkFileDialog.asksaveasfilename(filetypes = [("Gene history", "*.txt")])
            if (file != "") :
                if (file[-4:] != '.txt') : file = file + '.txt'
                
                    # Copie du fichier de conversion
                f1 = open('temp/conversion.txt', 'rb')
                f2 = open(file, 'wb')
                line = f1.readline()
                while (line != "") :
                    f2.write(line)
                    line = f1.readline()
                f2.close()
                f1.close
             
            self.__window.focus()
            win_changes.focus() 
            
        
            # Création de la fenêtre
        win_changes = Toplevel(self.__window)
        win_changes.title(self.LANG.get('CONVERSION_CHANGES', 'window_title'))
        win_changes.resizable(width=False, height=False)
                    
            # Grille principale
        grille = Frame(win_changes)
        grille.pack(padx=5, pady=5)
        
            # Tableau avec les changements
        entete = [13, "Conversion", 20, "WB ID before conversion", 15, "Modification", 20, "WB ID after conversion"]
        table = tablelist.TableList(grille, background='white', columns=entete, height=15, stretch='all', width=80, labelcommand=__sort_by_column)
        table.grid(row=1, column=1, pady=5, sticky=W+E+N+S)
        
        scrollbar = Scrollbar(grille, orient=VERTICAL)
        scrollbar.grid(row=1, column=2, pady=5, sticky=N+S)
        scrollbar.config(command=table.yview)
        table.config(yscrollcommand=scrollbar.set)    
        
            # Boutons
        gr = Frame(grille)
        gr.grid(row=2, column=1)    
        
        Button(gr, text=self.LANG.get('CONVERSION_CHANGES', 'save'), width=10, command=__save).grid(row=2, column=1, padx=20, pady=5)             
        Button(gr, text=self.LANG.get('CONVERSION_CHANGES', 'quit'), width=10, command=__quit).grid(row=2, column=2, padx=20, pady=5) 

            # Affichage de l'historique des conversions
        f = open('temp/conversion.txt', 'rb')
        line = f.readline()
        while (line != "") :
            line = line.strip().split('\t')
            if (len(line) == 4) :
                table.insert('end', (line[0] + " --> " + line[1], line[2], line[3]))
            else :
                table.insert('end', (line[0] + " --> " + line[1], line[2], line[3], line[4]))
            line = f.readline()
        f.close()




####################  DEMARRAGE DU SCRIPT  ####################
if __name__ == '__main__' :

        # Sélection de la langue
    CFG = MyConfigParser('config.ini')
    lang_file = CFG.get('WORMBASE', 'language')

    LANG = MyConfigParser(lang_file)

        # Création de l'application
    app = WBConverter(CFG, LANG)

